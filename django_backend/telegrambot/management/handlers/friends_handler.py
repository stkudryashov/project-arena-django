from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, \
    Filters

from telegrambot.models import TelegramUser


def start_friend_handler(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Вы можете добавлять друзей. Им будут приходить приглашения на игры, "
                                        "на которые вы собираетесь пойти")


def show_user_friend_list(update: Update, context: CallbackContext):
    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    # На всякий случай буду всегда проверять пользователя
    if user is None:
        return None

    user_friends = user.friends.all()
    message_text = "Список друзей"
    message_text += "\n\n"
    for my_friend in user_friends:
        message_text += f"@{my_friend.friend.telegram_username} - {my_friend.friend.username}\n"

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('Добавить нового друга', callback_data="Friends new")]]
    )

    update.effective_message.reply_text(message_text, reply_markup=markup)


def ask_friend_telegram_username(update: Update, context: CallbackContext):
    update.effective_message.reply_text("Отправьте имя пользователя вашего друга")
    return 0


def find_friend(update: Update, context: CallbackContext):
    friend_telegram_username = update.effective_message.text

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    # На всякий случай буду всегда проверять пользователя
    if user is None:
        return

    found_user = TelegramUser.objects.filter(telegram_username=friend_telegram_username).first()

    if found_user is None:
        update.effective_message.reply_text("Такой пользователь не пользуется нашем ботом!")
        return ConversationHandler.END

    if user.friends.filter(friend=found_user).exists():
        update.effective_message.reply_text("Ошибка")
        return ConversationHandler.END

    if found_user == user:
        update.effective_message.reply_text("Ошибка")
        return ConversationHandler.END

    ask_friend_text = "Пользователь хочет добавить вас в друзья"
    ask_friend_text += "\n"
    ask_friend_text += f"@{user.telegram_username} - {user.username}"

    ask_friend_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('Добавить', callback_data=f"Friends accept {user.id}")],
        [InlineKeyboardButton('Отклонить', callback_data=f"Friends deny {user.id}")]
    ]
    )

    # Отправляет запрос на дружбу
    context.bot.send_message(chat_id=found_user.telegram_id, text=ask_friend_text, reply_markup=ask_friend_markup)

    # Отправляет сообщение о том, что запрос отправлен
    update.effective_message.reply_text("Запрос дружбы отправлен")
    return ConversationHandler.END


def accept_friend(update: Update, context: CallbackContext, user_id):
    if user_id is None:
        return

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    # На всякий случай буду всегда проверять пользователя
    if user is None:
        return

    potential_friend = TelegramUser.objects.filter(id=user_id).first()
    if potential_friend is None:
        return

    user.friends.get_or_create(user=user, friend=potential_friend)
    potential_friend.friends.get_or_create(user=potential_friend, friend=user)

    update.effective_message.reply_text(f"Вы добавили @{potential_friend.telegram_username} тебе в друзья!")
    context.bot.send_message(chat_id=potential_friend.telegram_id, text=f"@{user.telegram_username} принял вашу заявку в друзья! ")

    return 0


def deny_friend(update: Update, context: CallbackContext, user_id):
    if user_id is None:
        return

    potential_friend = TelegramUser.objects.filter(id=user_id).first()

    if potential_friend is None:
        return

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    # На всякий случай буду всегда проверять пользователя
    if user is None:
        return

    potential_friend_text = f"@{user.telegram_username} - {user.username}\n"
    potential_friend_text += "не захотел с тобой дружить :("

    context.bot.send_message(potential_friend.telegram_id, potential_friend_text)
    update.effective_message.reply_text("Вы отказались от дружбы")

    return 0


def _friends_handler(update: Update, context: CallbackContext):
    button_press = update.callback_query

    button_data = button_press.data.split(" ")

    if button_data[0] != "Friends":
        return

    command = button_data[1]

    _res = ConversationHandler.END

    if command == "new":
        _res = ask_friend_telegram_username(update, context)

    elif command == "accept":
        user_id = button_data[2]
        _res = accept_friend(update, context, user_id)

    elif command == "deny":
        user_id = button_data[2]
        _res = deny_friend(update, context, user_id)

    # Возможно здесь нужно try -> except
    update.effective_message.delete()

    return _res


def end_friend_lookup(update: Update, context: CallbackContext):
    return ConversationHandler.END


def get_friends_handlers():

    return MessageHandler(Filters.regex("^(👥 Друзья)$"), show_user_friend_list), \
           ConversationHandler(
               entry_points=[CommandHandler('add_friend', ask_friend_telegram_username),
                             CallbackQueryHandler(_friends_handler, pattern=r'^Friends new')],
               states={
                   0: [MessageHandler(Filters.text & ~Filters.command, find_friend)],
               },
               fallbacks=[CommandHandler('menu', end_friend_lookup), CommandHandler('cancel', end_friend_lookup)]
           ), \
           CallbackQueryHandler(_friends_handler, pattern=r'^Friends')
