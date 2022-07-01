from telegram import Update, ReplyKeyboardMarkup

from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CommandHandler
)

from knowledges.models import Knowledge
from polls.models import PollVariant, UserPoll
from telegrambot.management.tools import get_user_or_notify, send_menu


def get_user_answer(update: Update, context: CallbackContext, user, answer_id):
    """Сохраняет ответ пользователя при опросе с вариантами ответа"""

    message = update.effective_message
    poll_answer = PollVariant.objects.filter(id=answer_id).first()

    if poll_answer is None:
        return

    poll = poll_answer.poll

    user_answer, is_created = UserPoll.objects.get_or_create(user=user, poll=poll)

    user_answer.answer = poll_answer.text
    user_answer.save()

    try:
        message.edit_text(Knowledge.objects.get(language='RU').polls_answer_ok)
    except Exception as e:
        message.reply_text(Knowledge.objects.get(language='RU').polls_answer_ok)


@get_user_or_notify
def collect_user_answer(update: Update, context: CallbackContext, answer_id=None, user=None):
    """Собирает текстовые ответы на опрос"""

    user_data_poll = context.user_data.get('poll')

    if user_data_poll is None:
        context.user_data['poll'] = {'answer_id': answer_id, 'text': ''}

        keyboard = [
            [Knowledge.objects.get(language='RU').polls_btn_send],
            [Knowledge.objects.get(language='RU').polls_btn_cancel]
        ]

        update.effective_message.reply_text(
            Knowledge.objects.get(language='RU').polls_enter_text,
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
        )
    else:
        if update.message.text:
            user_data_poll['text'] += '\n' + update.message.text
    return 0


@get_user_or_notify
def drop_collect(update: Update, context: CallbackContext, user=None):
    """Отменяет прохождение опроса"""

    context.user_data.clear()
    send_menu(update)

    return ConversationHandler.END


@get_user_or_notify
def send_collect(update: Update, context: CallbackContext, user=None):
    """Сохраняет ответ пользователя при опросе с развернутым ответом"""

    user_poll_data = context.user_data.get('poll')

    if user_poll_data is None:
        return ConversationHandler.END

    poll_answer = PollVariant.objects.filter(id=user_poll_data.get('answer_id')).first()

    if poll_answer is None:
        return ConversationHandler.END

    poll = poll_answer.poll

    user_answer, is_created = UserPoll.objects.get_or_create(user=user, poll=poll)

    user_answer.answer = user_poll_data.get('text')
    user_answer.save()

    context.user_data.clear()

    try:
        update.effective_message.edit_text(Knowledge.objects.get(language='RU').polls_answer_ok)
    except Exception as e:
        update.effective_message.reply_text(Knowledge.objects.get(language='RU').polls_answer_ok)

    send_menu(update)
    return ConversationHandler.END


@get_user_or_notify
def _poll_handler(update: Update, context: CallbackContext, user):
    button_press = update.callback_query
    button_data = button_press.data.split(' ')

    if button_data[0] != 'Poll':
        return

    command = button_data[1]

    if command == 'answer':
        get_user_answer(update, context, user, button_data[2])
    if command == 'open_answer':
        return collect_user_answer(update, context, button_data[2])


def get_poll_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(_poll_handler, pattern=r'^Poll open_answer')],
        states={0: [MessageHandler(~Filters.text([Knowledge.objects.get(language='RU').polls_btn_send]) &
                                   ~Filters.text([Knowledge.objects.get(language='RU').polls_btn_cancel]) &
                                   Filters.text & ~Filters.command, collect_user_answer)]},
        fallbacks=[CommandHandler('menu', drop_collect),
                   CommandHandler('cancel', drop_collect),
                   CommandHandler('send', send_collect),
                   MessageHandler(Filters.text([Knowledge.objects.get(language='RU').polls_btn_send]), send_collect),
                   MessageHandler(Filters.text([Knowledge.objects.get(language='RU').polls_btn_cancel]), drop_collect)
                   ]), CallbackQueryHandler(_poll_handler, pattern=r'^Poll')
