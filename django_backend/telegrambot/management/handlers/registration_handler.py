from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

from telegrambot.management.tools import (
    get_callback_as_dict,
    prepare_inline_keyboard,
    is_phone_valid, is_birthday_valid,
    transform_date, time_day, time_hour, ProfileStatus, set_user_level, level_markup, send_menu, is_name_valid,
)

from knowledges.models import Knowledge
from arenas.models import City

from telegrambot.models import TelegramUser


def start_registration(update: Update, context: CallbackContext):
    return ask_phone(update, context)


def ask_phone(update: Update, context: CallbackContext):
    """Просит пользователя в телеграмме указать номер телефона или отправляет меню"""

    if TelegramUser.objects.filter(telegram_id=update.effective_user.id).exists():
        send_menu(update)

        return ConversationHandler.END

    update.effective_message.reply_text(Knowledge.objects.get(language='RU').reg_phone_number)
    return ProfileStatus.REG_PHONE


def reg_phone(update: Update, context: CallbackContext):
    """Проверяет корректность и записывает телефон пользователя"""

    message = update.effective_message

    if is_phone_valid(message.text):
        context.user_data['phone'] = message.text
        return ask_name(update, context)
    else:
        message.reply_text(Knowledge.objects.get(language='RU').error_phone_number)
        return ProfileStatus.REG_PHONE


def ask_name(update: Update, context: CallbackContext):
    """Спрашивает имя пользователя"""

    update.message.reply_text(Knowledge.objects.get(language='RU').reg_username)
    return ProfileStatus.REG_NAME


def reg_name(update: Update, context: CallbackContext):
    """Записывает имя пользователя во временную память"""

    if is_name_valid(update.message.text):
        context.user_data["name"] = update.message.text.title()
        return ask_birthday(update, context)
    else:
        update.message.reply_text(Knowledge.objects.get(language='RU').error_username)
        return ProfileStatus.REG_NAME


def ask_birthday(update: Update, context: CallbackContext):
    """Спрашивает дату рождения"""

    update.message.reply_text(Knowledge.objects.get(language='RU').reg_date_of_birth)
    return ProfileStatus.REG_BIRTHDAY


def reg_birthday(update: Update, context: CallbackContext):
    """Проверяет дату рождения на корректность и записывает ее в память"""

    message_text = update.message.text

    if not is_birthday_valid(message_text, '%d.%m.%Y'):
        update.message.reply_text(Knowledge.objects.get(language='RU').error_date_of_birth)
        return ProfileStatus.REG_BIRTHDAY

    context.user_data["birthday"] = transform_date(message_text)
    return ask_city(update, context)


def ask_city(update: Update, context: CallbackContext):
    """Отправляет клавиатуру с выбором города"""

    _cities = City.objects.all()
    cities_keyboard = prepare_inline_keyboard(_cities, 3, 'city')

    markup = InlineKeyboardMarkup(cities_keyboard)
    update.message.reply_text(Knowledge.objects.get(language='RU').reg_city, reply_markup=markup)
    return ProfileStatus.REG_CITY


def reg_city(update: Update, context: CallbackContext):
    """Записывает выбранный город"""

    callback_data = get_callback_as_dict(update.callback_query.data)
    city_id = callback_data.get('value')

    message = update.callback_query.message
    _selected_city = City.objects.filter(id=city_id).first()

    if _selected_city is None:
        message.reply_text(Knowledge.objects.get(language='RU').error_city)
        return ProfileStatus.REG_CITY

    message.edit_text(Knowledge.objects.get(language='RU').reg_city + '\n\nВыбрано: ' + _selected_city.title)
    context.user_data['city'] = city_id

    # user_photos = update.effective_user.get_profile_photos(limit=1).photos
    #
    # if len(user_photos) > 0:
    #     user_photos = user_photos[0]
    # else:
    #     user_photos = None

    # Создание объекта пользователя Telegram
    TelegramUser.objects.create(
        username=context.user_data['name'],
        city_id=context.user_data['city'],
        phone_number=context.user_data['phone'],
        telegram_id=update.effective_user.id,
        date_of_birth=context.user_data['birthday'],
        telegram_username=update.effective_user.username,
        # telegram_img=user_photos
    )

    return ask_level(update, context)


def ask_level(update: Update, context: CallbackContext):
    """Отправляет клавиатуру с выбором уровня игры"""

    update.effective_message.reply_text(Knowledge.objects.get(language='RU').reg_level, reply_markup=level_markup())
    return ProfileStatus.REG_LEVEL


def reg_level(update: Update, context: CallbackContext):
    """Записывает выбранный уровень игры"""

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    if user is None:
        return start_registration(update, context)

    set_user_level(user, update)

    return ask_time_day(update, context)


def ask_time_day(update: Update, context: CallbackContext):
    """Предлагает выбрать удобный день игры"""

    time_day(update, context)
    return ProfileStatus.ASK_HOUR


def ask_time_hour(update: Update, context: CallbackContext):
    """Предлагает выбрать удобное время игры"""

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    if user is None:
        return start_registration(update, context)

    if time_hour(user, update, context):
        return reg_finish(update, context)

    return ProfileStatus.ASK_HOUR


def reg_finish(update: Update, context: CallbackContext):
    """Отправляет сообщение об окончании регистрации"""

    update.effective_message.reply_text(Knowledge.objects.get(language='RU').success_reg)

    send_menu(update)

    return ConversationHandler.END


def reg_cancel(update: Update, context: CallbackContext):
    """Отправляет сообщение об отмене регистрации и удаляет созданный профиль"""

    update.message.reply_text('Вы решили отменить регистрацию.')
    context.user_data.clear()

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    if user is not None:
        user.delete()

    send_menu(update)
    return ConversationHandler.END


def get_registration_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start_registration)],
        states={
            ProfileStatus.ASK_PHONE: [MessageHandler(Filters.text & ~Filters.command, ask_phone)],
            ProfileStatus.REG_PHONE: [MessageHandler(Filters.text & ~Filters.command, reg_phone)],
            ProfileStatus.ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, ask_name)],
            ProfileStatus.REG_NAME: [MessageHandler(Filters.text & ~Filters.command, reg_name)],
            ProfileStatus.ASK_BIRTHDAY: [MessageHandler(Filters.text & ~Filters.command, ask_birthday)],
            ProfileStatus.REG_BIRTHDAY: [MessageHandler(Filters.text & ~Filters.command, reg_birthday)],
            ProfileStatus.ASK_CITY: [CallbackQueryHandler(ask_city)],
            ProfileStatus.REG_CITY: [CallbackQueryHandler(reg_city)],
            ProfileStatus.ASK_LEVEL: [CallbackQueryHandler(ask_level)],
            ProfileStatus.REG_LEVEL: [CallbackQueryHandler(reg_level)],
            ProfileStatus.ASK_DAY: [CallbackQueryHandler(ask_time_day)],
            ProfileStatus.ASK_HOUR: [CallbackQueryHandler(ask_time_hour)]
        },
        fallbacks=[CommandHandler('cancel', reg_cancel)]
    )
