from celery import shared_task
from django.conf import settings
from django.utils import dateformat
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from games.models import Game

import telegram

from knowledges.models import Knowledge


@shared_task(name='new_game_notification_task')
def new_game_notification_task(game_id, users_ids: list):
    bot = telegram.Bot(settings.TELEGRAM_TOKEN)

    game = Game.objects.filter(id=game_id).first()

    if game is None:
        return

    date = dateformat.format(game.datetime, 'd E')
    time = dateformat.time_format(game.datetime, 'H:i')

    message = f'Дата игры: {date} {time}\n' \
              f'Максимально игроков: {game.max_players}\n' \
              f'Свободно мест: {game.free_space}\n' \
              f'Цена участия: {game.price}\n' \
              f'Манеж: {game.arena.title}\n'

    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_about,
                               callback_data=f'SearchAbout {game.id} {game.id - 1}'),
          InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_enter,
                               callback_data=f'SearchEnter {game.id}')]]
    )

    for telegram_id in users_ids:
        try:
            if Game.objects.filter(id=game_id).first().arena.photo:
                bot.send_photo(
                    chat_id=telegram_id,
                    photo=Game.objects.filter(id=game_id).first().arena.photo,
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

    message = f'Игра {date} {time} на манеже {game.arena.title} отменена'

    for telegram_id in users_ids:
        try:
            bot.send_message(chat_id=telegram_id, text=message)
        except Exception as e:
            pass
