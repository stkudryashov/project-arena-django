from celery import shared_task
from django.conf import settings

from games.models import Game

import telegram


@shared_task(name='games_notification_task')
def games_notification_task(game_id):
    bot = telegram.Bot(settings.TELEGRAM_TOKEN)

    game = Game.objects.get(id=game_id)
    players = game.players.filter(status='signed_up')

    for player in players:
        bot.send_message(
            chat_id=player.user.telegram_id,
            text=f'Игра {game.__str__()} скоро состоится'
        )
