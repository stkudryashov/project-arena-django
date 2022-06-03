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


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        defaults = Defaults(tzinfo=pytz.timezone('Europe/Moscow'))
        updater = Updater(settings.TELEGRAM_TOKEN, defaults=defaults)

        dispatcher = updater.dispatcher

        # dispatcher.add_handler(MessageHandler(Filters.text, start))

        dispatcher.add_handler(registration_handler.get_registration_handler())

        updater.start_polling()
        updater.idle()
