from django.core.management.base import BaseCommand

from django.conf import settings

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext, Defaults, CallbackQueryHandler

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

import logging
import pytz

from telegrambot.management.handlers import registration_handler
from telegrambot.management.handlers import profile_handler
from telegrambot.management.handlers import search_handler
from telegrambot.management.handlers import friends_handler
from telegrambot.management.handlers import user_games_handler
from telegrambot.management.tools import notification_change

from knowledges.models import Knowledge


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        defaults = Defaults(tzinfo=pytz.timezone('Europe/Moscow'))
        updater = Updater(settings.TELEGRAM_TOKEN, defaults=defaults)

        buttons = Knowledge.objects.get(language='RU')

        dispatcher = updater.dispatcher

        dispatcher.add_handler(registration_handler.get_registration_handler())
        dispatcher.add_handler(profile_handler.get_profile_handler())

        dispatcher.add_handler(CallbackQueryHandler(search_handler.search_callbacks, pattern=r'^Search'))
        dispatcher.add_handler(MessageHandler(Filters.text([buttons.btn_future_games]), search_handler.search_games))

        dispatcher.add_handler(MessageHandler(Filters.text([buttons.btn_notifications_on,
                                                            buttons.btn_notifications_off]), notification_change))

        dispatcher.add_handler(MessageHandler(Filters.text([buttons.btn_back_menu]),
                                              registration_handler.start_registration))

        for _handler in friends_handler.get_friends_handlers():
            dispatcher.add_handler(_handler)

        for _handler in user_games_handler.get_user_games_handlers():
            dispatcher.add_handler(_handler)

        updater.start_polling()
        updater.idle()
