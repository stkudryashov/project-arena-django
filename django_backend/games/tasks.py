from celery import shared_task
from django.conf import settings
from django.utils import dateformat
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from games.models import Game

import telegram
import time

from datetime import timedelta

from knowledges.models import Knowledge
from telegrambot.models import TelegramUser
from characteristics.models import UserCharacteristic


@shared_task(name='new_game_notification_task')
def new_game_notification_task(game_id, users_ids: list):
    bot = telegram.Bot(settings.TELEGRAM_TOKEN)

    game = Game.objects.filter(id=game_id).first()
    if game is None:
        return

    message = game.print()

    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_about,
                               callback_data=f'SearchAbout {game.id}'),
          InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_enter,
                               callback_data=f'SearchEnter {game.id}')]]
    )

    for telegram_id in users_ids:
        try:
            if Game.objects.filter(id=game_id).first().arena.photos.exists():
                bot.send_photo(
                    chat_id=telegram_id,
                    photo=Game.objects.filter(id=game_id).first().arena.photos.first().photo,
                    caption=message,
                    reply_markup=markup
                )
            else:
                bot.send_message(
                    chat_id=telegram_id,
                    text=message,
                    reply_markup=markup
                )
        except Exception as e:
            pass


@shared_task(name='canceled_game_notification_task')
def canceled_game_notification_task(game_id, users_ids: list):
    bot = telegram.Bot(settings.TELEGRAM_TOKEN)

    game = Game.objects.get(id=game_id)

    date = dateformat.format(game.datetime, 'd E')
    time = dateformat.time_format(game.datetime, 'H:i')

    message = Knowledge.objects.get(language='RU').notifications_game_canceled
    message += f'\n\n{date} {time} {game.arena.title}'

    for telegram_id in users_ids:
        try:
            bot.send_message(chat_id=telegram_id, text=message)
        except Exception as e:
            pass


@shared_task(name='notify_friends_about_game')
def notify_friends_about_game(user_id, game_id):
    bot = telegram.Bot(settings.TELEGRAM_TOKEN)

    user = TelegramUser.objects.filter(telegram_id=user_id).first()
    if user is None:
        return

    game = Game.objects.filter(id=game_id).first()
    if game is None:
        return

    message = game.print()

    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_about,
                               callback_data=f'SearchAbout {game.id}'),
          InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_enter,
                               callback_data=f'SearchEnter {game.id}')]]
    )

    friends_ids = list(user.friends.all().exclude(
        friend__games__game_id=game_id).values_list('friend__telegram_id', flat=True))

    if friends_ids:
        for friend_id in friends_ids:
            try:
                bot.send_message(
                    chat_id=friend_id,
                    text=f'Ваш друг @{user.telegram_username} приглашает вас поучаствовать в игре!'
                )

                if Game.objects.filter(id=game_id).first().arena.photos.exists():
                    bot.send_photo(
                        chat_id=friend_id,
                        photo=Game.objects.filter(id=game_id).first().arena.photos.first().photo,
                        caption=message,
                        reply_markup=markup
                    )
                else:
                    bot.send_message(
                        chat_id=friend_id,
                        text=message,
                        reply_markup=markup
                    )
            except Exception as e:
                pass


@shared_task(name='notify_game_confirm')
def notify_game_confirm(game_id):
    bot = telegram.Bot(settings.TELEGRAM_TOKEN)

    game = Game.objects.filter(id=game_id).first()
    if game is None:
        return

    info = Knowledge.objects.get(language='RU')

    _date = dateformat.format(game.datetime, 'd E')
    _time = dateformat.time_format(game.datetime, 'H:i')

    message = f'\n\n{_date} {_time} {game.arena.title}\n\n'
    message += info.notifications_confirm_text

    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(info.btn_notify_game_yes, callback_data=f'SearchConfirm {game.id}'),
          InlineKeyboardButton(info.btn_notify_game_no, callback_data=f'SearchDecline {game.id}')]]
    )

    for user_id in list(game.players.filter(status='signed_up').values_list('user__telegram_id', flat=True)):
        try:
            bot.send_message(chat_id=user_id, text=message, reply_markup=markup)
        except Exception as e:
            pass

    wait_time = timedelta(hours=info.notifications_confirm_wait.hour, minutes=info.notifications_confirm_wait.minute)
    time.sleep(wait_time.total_seconds())

    refused_users = game.players.filter(status='signed_up')

    for user in refused_users:
        characteristic = UserCharacteristic.objects.get(user=user.user, characteristic__title='Цифровой рейтинг')

        characteristic.value = int(characteristic.value) - 5
        characteristic.save()

    game.players.filter(status='signed_up').update(status='refused')

    if game.has_space:
        message = f'\n\n{_date} {_time} {game.arena.title}\n\n'
        message += info.notifications_confirm_reserve

        for user_id in list(game.players.filter(status='reserve').values_list('user__telegram_id', flat=True)):
            try:
                bot.send_message(chat_id=user_id, text=message, reply_markup=markup)
            except Exception as e:
                pass
