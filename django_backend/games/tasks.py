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
