from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

from telegrambot.management.tools import (
    create_callback,
    get_callback_as_dict,
    prepare_inline_keyboard,
    is_phone_valid, is_birthday_valid,
    get_menu_keyboard,
    transform_date, time_day, time_hour, ProfileStatus, level_markup, set_user_level, send_menu, get_profile_keyboard,
    is_name_valid,
)

from characteristics.models import Characteristic, UserCharacteristic
from playtime.models import DayOfTheWeek, UserTime
from knowledges.models import Knowledge
from arenas.models import City

from telegrambot.models import TelegramUser
from telegrambot.management.handlers.registration_handler import start_registration


def start_change(update: Update, context: CallbackContext):
    markup = ReplyKeyboardMarkup(get_profile_keyboard(), one_time_keyboard=False, resize_keyboard=True)
    message = Knowledge.objects.get(language='RU').edit_message_text

    update.effective_message.reply_text(message, reply_markup=markup)

    return ProfileStatus.DISTRIBUTE


def ask_phone(update: Update, context: CallbackContext):
    update.effective_message.reply_text(Knowledge.objects.get(language='RU').reg_phone_number)
    return ProfileStatus.REG_PHONE


def change_phone(update: Update, context: CallbackContext):
    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    if user is None:
        return start_registration(update, context)

    message = update.effective_message

    if is_phone_valid(message.text):
        user.phone_number = message.text
        user.save()

        message.reply_text('Телефон изменен')
        return ProfileStatus.DISTRIBUTE

    else:
        message.reply_text(Knowledge.objects.get(language='RU').error_phone_number)
        return ProfileStatus.REG_PHONE


def ask_name(update: Update, context: CallbackContext):
    """Спрашивает имя пользователя"""

    update.message.reply_text(Knowledge.objects.get(language='RU').reg_username)
    return ProfileStatus.REG_NAME


def change_name(update: Update, context: CallbackContext):
    """Изменяет имя пользователя"""

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    if user is None:
        return start_registration(update, context)

    message = update.effective_message

    if is_name_valid(message.text):
        user.username = message.text.title()
        user.save()

        message.reply_text('Имя изменено')
        return ProfileStatus.DISTRIBUTE
    else:
        update.message.reply_text(Knowledge.objects.get(language='RU').error_username)
        return ProfileStatus.REG_NAME


def ask_birthday(update: Update, context: CallbackContext):
    """Спрашивает день пользователя"""

    update.message.reply_text(Knowledge.objects.get(language='RU').reg_date_of_birth)
    return ProfileStatus.REG_BIRTHDAY


def change_birthday(update: Update, context: CallbackContext):
    """Проверяет дату рождения на корректность и изменяет её"""

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    if user is None:
        return start_registration(update, context)

    message = update.effective_message

    if not is_birthday_valid(message.text, '%d.%m.%Y'):
        update.message.reply_text(Knowledge.objects.get(language='RU').error_date_of_birth)
        return ProfileStatus.REG_BIRTHDAY

    user.date_of_birth = transform_date(message.text)
    user.save()

    message.reply_text('День рождения изменен')
    return ProfileStatus.DISTRIBUTE


def ask_city(update: Update, context: CallbackContext):
    """Отправляет клавиатуру с выбором города"""

    _cities = City.objects.all()
    cities_keyboard = prepare_inline_keyboard(_cities, 3, 'city')

    markup = InlineKeyboardMarkup(cities_keyboard)
    update.message.reply_text(Knowledge.objects.get(language='RU').reg_city, reply_markup=markup)
    return ProfileStatus.REG_CITY


def change_city(update: Update, context: CallbackContext):
    """Записывает выбранный город"""

    callback_data = get_callback_as_dict(update.callback_query.data)
    city_id = callback_data.get('id')

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()
    if user is None:
        return start_registration(update, context)

    message = update.callback_query.message
    _selected_city = City.objects.filter(id=city_id).first()

    if _selected_city is None:
        message.reply_text(Knowledge.objects.get(language='RU').error_city)
        return ProfileStatus.REG_CITY

    message.edit_text(Knowledge.objects.get(language='RU').reg_city + '\n\nВыбрано: ' + _selected_city.title)

    user.city_id = city_id
    user.save()

    message.reply_text('Город изменен')
    return ProfileStatus.DISTRIBUTE


def ask_level(update: Update, context: CallbackContext):
    update.effective_message.reply_text(Knowledge.objects.get(language='RU').reg_level, reply_markup=level_markup())
    return ProfileStatus.REG_LEVEL


def change_level(update: Update, context: CallbackContext):
    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    if user is None:
        return start_registration(update, context)

    set_user_level(user, update)
    user.save()

    update.effective_message.reply_text('Уровень изменен')
    return ProfileStatus.DISTRIBUTE


def ask_time_day(update: Update, context: CallbackContext):
    time_day(update, context)
    return ProfileStatus.ASK_HOUR


def ask_time_hour(update: Update, context: CallbackContext):
    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    if user is None:
        return start_registration(update, context)

    if time_hour(user, update, context):
        update.effective_message.reply_text('Время изменено')
        return ProfileStatus.DISTRIBUTE


def distribute(update: Update, context: CallbackContext):
    message = update.effective_message
    command = message.text

    buttons = Knowledge.objects.get(language='RU')

    names = [buttons.btn_edit_name, buttons.btn_edit_date_of_birth, buttons.btn_edit_city,
             buttons.btn_edit_phone, buttons.btn_edit_level, buttons.btn_edit_playtime,
             buttons.btn_back_menu]

    if command == names[0]:
        return ask_name(update, context)
    elif command == names[1]:
        return ask_birthday(update, context)
    elif command == names[2]:
        return ask_city(update, context)
    elif command == names[3]:
        return ask_phone(update, context)
    elif command == names[4]:
        return ask_level(update, context)
    elif command == names[5]:
        return ask_time_day(update, context)
    elif command == names[6]:
        return end_change(update, context)

    message.reply_text('Выберите один из пунктов или вернитесь в меню')


def end_change(update: Update, context: CallbackContext):
    send_menu(update)
    return ConversationHandler.END


def get_profile_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('edit_profile', start_change),
                      MessageHandler(Filters.regex("^(👤 Профиль)$"), start_change)],
        states={
            ProfileStatus.DISTRIBUTE: [MessageHandler(Filters.text & ~Filters.command, distribute)],
            ProfileStatus.ASK_PHONE: [MessageHandler(Filters.text & ~Filters.command, ask_phone)],
            ProfileStatus.REG_PHONE: [MessageHandler(Filters.text & ~Filters.command, change_phone)],
            ProfileStatus.ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, ask_name)],
            ProfileStatus.REG_NAME: [MessageHandler(Filters.text & ~Filters.command, change_name)],
            ProfileStatus.ASK_BIRTHDAY: [MessageHandler(Filters.text & ~Filters.command, ask_birthday)],
            ProfileStatus.REG_BIRTHDAY: [MessageHandler(Filters.text & ~Filters.command, change_birthday)],
            ProfileStatus.ASK_CITY: [CallbackQueryHandler(ask_city)],
            ProfileStatus.REG_CITY: [CallbackQueryHandler(change_city)],
            ProfileStatus.ASK_LEVEL: [CallbackQueryHandler(ask_level)],
            ProfileStatus.REG_LEVEL: [CallbackQueryHandler(change_level)],
            ProfileStatus.ASK_DAY: [CallbackQueryHandler(ask_time_day)],
            ProfileStatus.ASK_HOUR: [CallbackQueryHandler(ask_time_hour)]
        },
        fallbacks=[CommandHandler('menu', end_change), CommandHandler('cancel', end_change),
                   MessageHandler(Filters.regex(Knowledge.objects.get(language='RU').btn_back_menu), end_change)]
    )
