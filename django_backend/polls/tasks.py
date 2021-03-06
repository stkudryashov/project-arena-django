from celery import shared_task
from django.conf import settings

import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from knowledges.models import Knowledge
from polls.models import Poll


@shared_task(name='new_poll_notification_task')
def new_poll_notification_task(poll_id, users_ids: list):
    bot = telegram.Bot(settings.TELEGRAM_TOKEN)

    poll = Poll.objects.filter(id=poll_id).first()

    if poll is None:
        return

    message_text = poll.description
    inline_keyboard = []

    if poll.is_open:
        inline_keyboard.append([InlineKeyboardButton(Knowledge.objects.get(language='RU').polls_btn_send,
                                                     callback_data=f'Poll open_answer {poll.id}')])
    else:
        for answer in poll.answers.all():
            inline_keyboard.append([InlineKeyboardButton(answer.text, callback_data=f'Poll answer {answer.id}')])

    markup = InlineKeyboardMarkup(inline_keyboard)

    for user_id in users_ids:
        try:
            if Poll.objects.filter(id=poll_id).first().photo:
                bot.send_photo(chat_id=user_id, photo=Poll.objects.filter(id=poll_id).first().photo,
                               caption=message_text, reply_markup=markup)
            else:
                bot.send_message(chat_id=user_id, text=message_text, reply_markup=markup)
        except Exception as e:
            pass
