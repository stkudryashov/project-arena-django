from enum import Enum

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
    transform_date,
)

from characteristics.models import Characteristic, UserCharacteristic
from playtime.models import DayOfTheWeek, UserTime
from knowledges.models import Knowledge
from arenas.models import City

from telegrambot.models import TelegramUser


class Registration(Enum):
    ASK_PHONE = 0
    REG_PHONE = 1
    ASK_NAME = 2
    REG_NAME = 3
    ASK_BIRTHDAY = 4
    REG_BIRTHDAY = 5
    ASK_CITY = 6
    REG_CITY = 7
    ASK_LEVEL = 8
    REG_LEVEL = 9
    ASK_DAY = 10
    ASK_HOUR = 11


def ask_phone(update: Update, context: CallbackContext):
    """Просит пользователя в телеграмме указать номер телефона или отправляет меню"""

    if TelegramUser.objects.filter(telegram_id=update.effective_user.id).exists():
        markup = ReplyKeyboardMarkup(get_menu_keyboard(), one_time_keyboard=False, resize_keyboard=True)
        update.message.reply_text('Главное меню 🖥', reply_markup=markup)

        return ConversationHandler.END

    update.effective_message.reply_text(Knowledge.objects.get(language='RU').reg_phone_number)
    return Registration.REG_PHONE


def reg_phone(update: Update, context: CallbackContext):
    """Проверяет корректность и записывает телефон пользователя"""

    message = update.effective_message

    if is_phone_valid(message.text):
        context.user_data["phone"] = message.text
        return ask_name(update, context)
    else:
        message.reply_text(Knowledge.objects.get(language='RU').error_phone_number)
        return Registration.ASK_PHONE


def ask_name(update: Update, context: CallbackContext):
    """Спрашивает имя пользователя"""

    update.message.reply_text(Knowledge.objects.get(language='RU').reg_username)
    return Registration.REG_NAME


def reg_name(update: Update, context: CallbackContext):
    """Записывает имя пользователя во временную память"""

    context.user_data["name"] = update.message.text
    return ask_birthday(update, context)


def ask_birthday(update: Update, context: CallbackContext):
    """Спрашивает дату рождения"""

    update.message.reply_text(Knowledge.objects.get(language='RU').reg_date_of_birth)
    return Registration.REG_BIRTHDAY


def reg_birthday(update: Update, context: CallbackContext):
    """Проверяет дату рождения на корректность и записывает ее в память"""

    message_text = update.message.text

    if not is_birthday_valid(message_text, '%d.%m.%Y'):
        update.message.reply_text(Knowledge.objects.get(language='RU').error_date_of_birth)
        return Registration.REG_BIRTHDAY

    context.user_data["birthday"] = transform_date(message_text)
    return ask_city(update, context)


def ask_city(update: Update, context: CallbackContext):
    """Отправляет клавиатуру с выбором города"""

    _cities = City.objects.all()
    cities_keyboard = prepare_inline_keyboard(_cities, 3, 'city')

    markup = InlineKeyboardMarkup(cities_keyboard)
    update.message.reply_text(Knowledge.objects.get(language='RU').reg_city, reply_markup=markup)
    return Registration.REG_CITY


def reg_city(update: Update, context: CallbackContext):
    """Записывает выбранный город"""

    callback_data = get_callback_as_dict(update.callback_query.data)
    city_id = callback_data.get('id')

    message = update.callback_query.message
    _selected_city = City.objects.filter(id=city_id).first()

    if _selected_city is None:
        message.reply_text(Knowledge.objects.get(language='RU').error_city)
        return Registration.REG_CITY

    message.edit_text(Knowledge.objects.get(language='RU').reg_city + '\n\nВыбрано: ' + _selected_city.title)
    context.user_data['city'] = city_id

    # Создание объекта пользователя Telegram
    TelegramUser.objects.create(
        username=context.user_data["name"],
        city_id=context.user_data["city"],
        phone_number=context.user_data["phone"],
        telegram_id=update.effective_user.id,
        date_of_birth=context.user_data["birthday"],
        telegram_username=update.effective_user.username
    )

    return ask_level(update, context)


def ask_level(update: Update, context: CallbackContext):
    """Отправляет клавиатуру с выбором уровня игры"""

    _levels = Knowledge.objects.get(language='RU').play_skill_params.strip().split(',')

    markup = InlineKeyboardMarkup.from_row(
        [InlineKeyboardButton(_levels[i], callback_data=create_callback('level', i)) for i in range(len(_levels))]
    )

    update.effective_message.reply_text(Knowledge.objects.get(language='RU').reg_level, reply_markup=markup)
    return Registration.REG_LEVEL


def reg_level(update: Update, context: CallbackContext):
    """Записывает выбранный уровень игры"""

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    if user is None:
        return Registration.ASK_PHONE

    callback_data = get_callback_as_dict(update.callback_query.data)
    level_index = callback_data.get("id")

    _levels = Knowledge.objects.get(language='RU').play_skill_params.strip().split(',')
    level_value = _levels[level_index]

    characteristic_obj, _ = Characteristic.objects.get_or_create(title='Уровень игры')

    UserCharacteristic.objects.create(
        value=level_value,
        characteristic=characteristic_obj,
        user=user
    )

    message = update.callback_query.message
    message.edit_text(Knowledge.objects.get(language='RU').reg_level + '\n\nВыбрано: ' + level_value)

    return ask_time_day(update, context)


def ask_time_day(update: Update, context: CallbackContext):
    """Предлагает выбрать удобный день игры"""

    _days = DayOfTheWeek.objects.all()

    days_keyboard = prepare_inline_keyboard(_days, 1, "day")
    days_keyboard.append([InlineKeyboardButton("CONTINUE", callback_data=create_callback("skip", ""))])

    markup = InlineKeyboardMarkup(days_keyboard)

    update.callback_query.message.reply_text(Knowledge.objects.get(language='RU').reg_playtime, reply_markup=markup)

    return Registration.ASK_HOUR


def ask_time_hour(update: Update, context: CallbackContext):
    """Предлагает выбрать удобное время игры"""

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    if user is None:
        return reg_phone(update, context)

    callback_data = get_callback_as_dict(update.callback_query.data)
    user_data = context.user_data

    message = update.callback_query.message

    text_prefix = {
        'selected': Knowledge.objects.get(language='RU').time_select_emoji,
        'unselected': Knowledge.objects.get(language='RU').time_unselect_emoji
    }

    if callback_data.get('callback') == 'skip':
        message = update.callback_query.message
        message.edit_reply_markup(None)

        time_text = '\n\nВыбрано:'

        for user_time in user.times.all():
            day_of_the_week = user_time.day_of_the_week.title
            select_time = user_time.time.strftime("%H:%M")

            time_text += f'\n{text_prefix.get("selected")} {day_of_the_week} {select_time}'

        message.edit_text(Knowledge.objects.get(language='RU').reg_level + time_text)

        return reg_finish(update, context)

    if callback_data.get('callback') == 'day':
        if context.user_data.get('day') == callback_data.get('id'):
            context.user_data['day'] = None
        else:
            context.user_data['day'] = callback_data.get('id')

    _days = DayOfTheWeek.objects.all()

    # Создаем клавиатуру
    days_keyboard = []

    for i in range(len(_days)):
        days_keyboard.append([InlineKeyboardButton(_days[i].title, callback_data=create_callback('day', _days[i].id))])

        if str(_days[i].id) == str(user_data['day']):
            _hours = UserTime.objects.filter(day_of_the_week_id=_days[i].id).all()
            line = []

            # Количество кнопок в ряду (для часов)
            btns_per_line = 5

            for j in range(len(_hours)):
                _prefix = text_prefix.get('unselected')

                user_selected_this_hour = user in _hours[j].users.all()

                if callback_data.get('callback') == 'hour':
                    if callback_data.get('id') == _hours[j].id:
                        if user_selected_this_hour:
                            _hours[j].users.remove(user)
                            user_selected_this_hour = False
                        else:
                            _hours[j].users.add(user)
                            user_selected_this_hour = True

                if user_selected_this_hour:
                    _prefix = text_prefix.get('selected')

                line.append(InlineKeyboardButton(_prefix + _hours[j].time.strftime('%H:%M'),
                                                 callback_data=create_callback('hour', _hours[j].id)))

                if (j + 1) % btns_per_line == 0:
                    days_keyboard.append(line)
                    line = []

            days_keyboard.append(line)

    days_keyboard.append([InlineKeyboardButton("CONTINUE", callback_data=create_callback('skip', 'skip'))])

    markup = InlineKeyboardMarkup(days_keyboard)
    message.edit_reply_markup(markup)

    return Registration.ASK_HOUR


def reg_finish(update: Update, context: CallbackContext):
    """Отправляет сообщение об окончании регистрации"""

    markup = ReplyKeyboardMarkup(get_menu_keyboard(), one_time_keyboard=False, resize_keyboard=True)
    update.callback_query.message.reply_text(Knowledge.objects.get(language='RU').success_reg, reply_markup=markup)

    return ConversationHandler.END


def reg_cancel(update: Update, context: CallbackContext):
    """Отправляет сообщение об отмене регистрации и удаляет созданный профиль"""

    update.message.reply_text('Вы решили отменить регистрацию.')
    context.user_data.clear()

    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    if user is not None:
        user.delete()

    return ConversationHandler.END


def get_registration_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', ask_phone)],
        states={
            Registration.ASK_PHONE: [MessageHandler(Filters.text & ~Filters.command, ask_phone)],
            Registration.REG_PHONE: [MessageHandler(Filters.text & ~Filters.command, reg_phone)],
            Registration.ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, ask_name)],
            Registration.REG_NAME: [MessageHandler(Filters.text & ~Filters.command, reg_name)],
            Registration.ASK_BIRTHDAY: [MessageHandler(Filters.text & ~Filters.command, ask_birthday)],
            Registration.REG_BIRTHDAY: [MessageHandler(Filters.text & ~Filters.command, reg_birthday)],
            Registration.ASK_CITY: [CallbackQueryHandler(ask_city)],
            Registration.REG_CITY: [CallbackQueryHandler(reg_city)],
            Registration.ASK_LEVEL: [CallbackQueryHandler(ask_level)],
            Registration.REG_LEVEL: [CallbackQueryHandler(reg_level)],
            Registration.ASK_DAY: [CallbackQueryHandler(ask_time_day)],
            Registration.ASK_HOUR: [CallbackQueryHandler(ask_time_hour)]
        },
        fallbacks=[CommandHandler('cancel', reg_cancel)]
    )
