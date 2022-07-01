from celery import shared_task
from django.conf import settings
from django.utils import dateformat

import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from polls.models import Poll, PollVariant, UserPoll


@shared_task(name="new_poll_notification_task")
def new_poll_notification_task(poll_id, users_ids: list):
    bot = telegram.Bot(settings.TELEGRAM_TOKEN)

    poll = Poll.objects.filter(id=poll_id).first()

    if poll is None:
        return

    message_text = poll.description
    inline_keyboard = []
    for answer in poll.answers.all():
        inline_keyboard.append([InlineKeyboardButton(answer.text,
                                                     callback_data=f"Poll {'answer' if not answer.is_open else 'open_answer'} {answer.id}")])

    markup = InlineKeyboardMarkup(inline_keyboard)

    for user_id in users_ids:
        if poll.photo:
            bot.send_photo(chat_id=user_id, photo=poll.photo, caption=message_text, reply_markup=markup)
        else:
            bot.send_message(chat_id=user_id, text=message_text, reply_markup=markup)
