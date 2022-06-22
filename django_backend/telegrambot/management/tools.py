from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup

import datetime
import json
import re

from telegram.ext import CallbackContext

from characteristics.models import Characteristic, UserCharacteristic
from playtime.models import UserTime, DayOfTheWeek
from knowledges.models import Knowledge
from telegrambot.models import TelegramUser


class ProfileStatus:
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
    ASK_VALUE = 12
    REG_VALUE = 13

    DISTRIBUTE = 14


def prepare_inline_keyboard(data, btn_per_line: int, callback_name: str):
    """Динамически распределяет пространство для клавиатуры"""

    result = []
    line = []

    for i in range(len(data)):
        line.append(InlineKeyboardButton(data[i].title, callback_data=create_callback(callback_name, data[i].id)))

        if (i + 1) % btn_per_line == 0:
            result.append(line)
            line = []

    result.append(line)
    return result


def transform_date(date: str, from_format: str = '%d.%m.%Y', to_format: str = '%Y-%m-%d') -> str:
    """Преобразовывает принятую дату в необходимый Date формат"""

    _date = datetime.datetime.strptime(date, from_format)
    return _date.strftime(to_format)


def is_birthday_valid(date: str, _format: str = "%d.%m.%Y") -> bool:
    """Проверяет что дата введена корректно"""

    try:
        datetime.datetime.strptime(date, _format)
    except ValueError:
        return False
    return True


def is_phone_valid(number: str) -> bool:
    """Проверяет если номер телефона указан корректно"""

    regex = r'^((\+7|7|8)+([0-9]){10})$'

    if re.match(regex, number):
        return True

    return False


def is_name_valid(name: str) -> bool:
    """Простая проверка имени пользователя на адекватность"""

    if len(name.split()) == 2:
        return True

    return False


def get_callback_as_dict(data) -> dict:
    return dict(json.loads(data))


def create_callback(callback_name, callback_value) -> str:
    _dict = {'callback': callback_name, 'value': callback_value}
    return json.dumps(_dict)


def get_menu_keyboard():
    """Возвращает список с кнопками главного меню"""

    buttons = Knowledge.objects.get(language='RU')

    keyboard = [
        [buttons.btn_future_games],
        [buttons.btn_my_games, buttons.btn_friends],
        [buttons.btn_profile, buttons.btn_notifications]
    ]

    return keyboard


def get_profile_keyboard():
    """Возвращает список с кнопками меню профиля"""

    buttons = Knowledge.objects.get(language='RU')

    keyboard = [
        [buttons.btn_edit_name, buttons.btn_edit_date_of_birth],
        [buttons.btn_edit_city, buttons.btn_edit_phone],
        [buttons.btn_edit_level, buttons.btn_edit_playtime]
    ]

    characteristics = Characteristic.objects.filter(show_in_menu=True).exclude(title='Уровень игры')

    if characteristics:
        line = []

        for index, value in enumerate(list(characteristics.values_list('title', flat=True))):
            line.append(value)

            if (index + 1) % 2 == 0:
                keyboard.append(line)
                line = []

        keyboard.append(line)

    keyboard.append([buttons.btn_back_menu])

    return keyboard


def time_day(update: Update, context: CallbackContext):
    _days = DayOfTheWeek.objects.all()

    text_button = Knowledge.objects.get(language='RU').btn_continue_time

    days_keyboard = prepare_inline_keyboard(_days, 1, 'day')
    days_keyboard.append([InlineKeyboardButton(text_button, callback_data=create_callback('skip', ''))])

    markup = InlineKeyboardMarkup(days_keyboard)

    update.effective_message.reply_text(Knowledge.objects.get(language='RU').reg_playtime, reply_markup=markup)


def time_selected(user, text_prefix, update: Update, context: CallbackContext):
    message = update.callback_query.message
    message.edit_reply_markup(None)

    time_text = '\n\nВыбрано:'

    for user_time in user.times.all():
        day_of_the_week = user_time.day_of_the_week.title
        select_time = user_time.time.strftime("%H:%M")

        time_text += f'\n{text_prefix.get("selected")} {day_of_the_week} {select_time}'

    message.edit_text(Knowledge.objects.get(language='RU').reg_playtime + time_text)


def time_hour(user, update: Update, context: CallbackContext):
    callback_data = get_callback_as_dict(update.callback_query.data)
    user_data = context.user_data

    message = update.callback_query.message

    text_prefix = {
        'selected': Knowledge.objects.get(language='RU').time_select_emoji,
        'unselected': Knowledge.objects.get(language='RU').time_unselect_emoji
    }

    if callback_data.get('callback') == 'skip':
        time_selected(user, text_prefix, update, context)
        return True

    if callback_data.get('callback') == 'day':
        if context.user_data.get('day') == callback_data.get('value'):
            context.user_data['day'] = None
        else:
            context.user_data['day'] = callback_data.get('value')

    _days = DayOfTheWeek.objects.all()

    # Создаем клавиатуру
    days_keyboard = []

    for i in range(len(_days)):
        days_keyboard.append([InlineKeyboardButton(_days[i].title, callback_data=create_callback('day', _days[i].id))])

        if str(_days[i].id) == str(user_data['day']):
            _hours = UserTime.objects.filter(day_of_the_week_id=_days[i].id).all()
            line = []

            # Количество кнопок в ряду (для часов)
            btn_per_line = 5

            for j in range(len(_hours)):
                _prefix = text_prefix.get('unselected')

                user_selected_this_hour = user in _hours[j].users.all()

                if callback_data.get('callback') == 'hour':
                    if callback_data.get('value') == _hours[j].id:
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

                if (j + 1) % btn_per_line == 0:
                    days_keyboard.append(line)
                    line = []

            days_keyboard.append(line)

    days_keyboard.append([InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_continue_time,
                                               callback_data=create_callback('skip', 'skip'))])

    markup = InlineKeyboardMarkup(days_keyboard)
    message.edit_reply_markup(markup)
    return False


def get_user_or_notify(func):
    # Ищет пользователя в БД, если не находит, отправляет текст, возвращает User или None

    def wrapper(*args, **kwargs):
        update: Update = kwargs.get("update")

        if update is None:
            update = args[0]
            if update is None:
                return

        telegram_id = update.effective_user.id
        user = TelegramUser.objects.filter(telegram_id=telegram_id).first()

        if user is None:
            update.effective_message.reply_text("У вас нет прав на использование этой команды")
            return

        return func(*args, **kwargs, user=user)

    return wrapper


def get_user_or_none(telegram_id):
    user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
    return user


def level_markup() -> InlineKeyboardMarkup:
    _levels = Knowledge.objects.get(language='RU').play_skill_params.strip().split(',')

    markup = InlineKeyboardMarkup.from_row(
        [InlineKeyboardButton(_levels[i], callback_data=create_callback('level', i)) for i in range(len(_levels))]
    )
    return markup


def set_user_level(user, update: Update):
    callback_data = get_callback_as_dict(update.callback_query.data)
    level_index = callback_data.get('value')

    _levels = Knowledge.objects.get(language='RU').play_skill_params.strip().split(',')
    level_value = _levels[level_index]

    characteristic_obj, is_get = Characteristic.objects.get_or_create(title='Уровень игры')

    if UserCharacteristic.objects.filter(user=user, characteristic=characteristic_obj).exists():
        u_characteristic = UserCharacteristic.objects.get(user=user, characteristic=characteristic_obj)
        u_characteristic.value = level_value
        u_characteristic.save()
    else:
        UserCharacteristic.objects.create(
            value=level_value,
            characteristic=characteristic_obj,
            user=user
        )

    message = update.callback_query.message
    message.edit_text(Knowledge.objects.get(language='RU').reg_level + '\n\nВыбрано: ' + level_value)


def send_menu(update: Update):
    markup = ReplyKeyboardMarkup(get_menu_keyboard(), one_time_keyboard=False, resize_keyboard=True)
    update.effective_message.reply_text(Knowledge.objects.get(language='RU').menu_message_text, reply_markup=markup)
