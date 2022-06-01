from django.core.management.base import BaseCommand

from django.conf import settings

from telegram import Update
from telegram.ext import Updater, Filters, CallbackContext, Defaults
from telegram.ext import MessageHandler

import logging
import pytz


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    message = update.message.text
    update.message.reply_text(message)


class Command(BaseCommand):
    def handle(self, *args, **options):
        defaults = Defaults(tzinfo=pytz.timezone('Europe/Moscow'))
        updater = Updater(settings.TELEGRAM_TOKEN, defaults=defaults)

        dispatcher = updater.dispatcher

        dispatcher.add_handler(MessageHandler(Filters.text, start))

        updater.start_polling()
        updater.idle()
