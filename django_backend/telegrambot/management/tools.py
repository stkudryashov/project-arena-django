from telegram import InlineKeyboardButton

import datetime
import json

from knowledges.models import Knowledge


def prepare_inline_keyboard(data, btns_per_line: int, callback_name: str):
    """Динамически распределяет пространство для клавиатуры"""

    result = []
    line = []

    for i in range(len(data)):
        line.append(InlineKeyboardButton(data[i].title, callback_data=create_callback(callback_name, data[i].id)))

        if (i + 1) % btns_per_line == 0:
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

    return True


def get_callback_as_dict(data) -> dict:
    return dict(json.loads(data))


def create_callback(callback_name, callback_value) -> str:
    _dict = {'callback': callback_name, 'id': callback_value}
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
