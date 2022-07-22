from datetime import timedelta, datetime

from django.utils import dateformat

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import CallbackContext, CallbackQueryHandler, MessageHandler, Filters

from games.models import TelegramUserGame
from knowledges.models import Knowledge
from telegrambot.management.tools import get_user_or_notify
from telegrambot.models import TelegramUser


def user_games_list(update: Update, context: CallbackContext):
    user = TelegramUser.objects.get(telegram_id=update.effective_user.id)

    current_games = TelegramUserGame.objects.filter(user=user).exclude(
            status='refused').exclude(game__status__in=['is_over', 'canceled'])

    if not current_games.exists():
        update.effective_message.reply_text(Knowledge.objects.get(language='RU').my_games_no_games)
        return

    keyboard = []

    message = 'Список твоих игр'

    for game in current_games.order_by('id'):
        date = dateformat.format(game.game.datetime, 'd E')
        time = dateformat.time_format(game.game.datetime, 'H:i')

        keyboard.append(
            [InlineKeyboardButton(f'{date} {time} - {game.game.arena.title} - {game.game.price}',
                                  callback_data=f'MyGames view {game.id}')]
        )

    keyboard = InlineKeyboardMarkup(keyboard)

    update.effective_message.reply_text(message, reply_markup=keyboard)


def get_user_games(update: Update, context: CallbackContext, game_id=None):
    current_game = TelegramUserGame.objects.filter(id=game_id).first()

    if current_game is None:
        update.effective_message.reply_text(Knowledge.objects.get(language='RU').my_games_no_games)
        return

    game = current_game.game
    message = game.print()

    buttons = [
        [
            InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_about,
                                 callback_data=f'MyGames about {current_game.id}'),
            InlineKeyboardButton(Knowledge.objects.get(language='RU').my_games_cancel_btn,
                                 callback_data=f'MyGames leave {current_game.id}'),
        ]
    ]

    if game.arena.photos.exists():
        update.effective_message.reply_photo(game.arena.photos.first().photo, message,
                                             reply_markup=InlineKeyboardMarkup(buttons))
    else:
        update.effective_message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))


def get_about(update: Update, context: CallbackContext, user: TelegramUser, last_id):
    """Информация о манеже"""

    current_game = TelegramUserGame.objects.filter(id=last_id).first().game
    message = current_game.arena.print()

    # markup = InlineKeyboardMarkup.from_column(
    #     [InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_back,
    #                           callback_data=f'MyGames next {last_id}')]
    # )

    if current_game.arena.photos.exists():
        media_group = []

        for i, photo in enumerate(current_game.arena.photos.all()):
            media_group.append(InputMediaPhoto(media=photo.photo, caption=message if i == 0 else ''))

        update.effective_message.reply_media_group(media_group)
    else:
        update.effective_message.reply_text(message)


def user_leave_game(update: Update, context: CallbackContext, user: TelegramUser, last_id=None):
    game: TelegramUserGame = TelegramUserGame.objects.filter(user=user, id=last_id).first()

    if game is None:
        update.effective_message.reply_text("Произошла ошибка. Игра не была найдена, а это странно..")
        return

    safe_time_info = Knowledge.objects.get(language='RU').my_games_safe_time
    safe_time = timedelta(hours=safe_time_info.hour, minutes=safe_time_info.minute)

    if game.game.datetime - safe_time < datetime.now():
        markup = InlineKeyboardMarkup.from_row([
            InlineKeyboardButton(Knowledge.objects.get(language='RU').my_games_btn_yes,
                                 callback_data=f'SearchLeave True {game.id}'),
            InlineKeyboardButton(Knowledge.objects.get(language='RU').my_games_btn_no,
                                 callback_data='SearchLeave False')
        ])

        update.effective_message.reply_text(
            Knowledge.objects.get(language='RU').my_games_wrong_text, reply_markup=markup)
    else:
        game.delete()
        update.effective_message.reply_text(Knowledge.objects.get(language='RU').my_games_cancel_text)


@get_user_or_notify
def show_first_game(update: Update, context: CallbackContext, user: TelegramUser):
    user_games_list(update, context)


@get_user_or_notify
def _user_game_handler(update: Update, context: CallbackContext, user: TelegramUser):
    button_press = update.callback_query
    button_data = button_press.data.split(' ')

    if button_data[0] != 'MyGames':
        return

    command = button_data[1]

    if command == 'leave':
        last_id = button_data[2]
        user_leave_game(update, context, user, last_id)
        button_press.message.delete()
    elif command == 'about':
        last_id = button_data[2]
        get_about(update, context, user, last_id)
    elif command == 'view':
        last_id = button_data[2]
        get_user_games(update, context, last_id)


def get_user_games_handlers():
    buttons = Knowledge.objects.get(language='RU')

    return CallbackQueryHandler(_user_game_handler, pattern=r'^MyGames'), MessageHandler(
        Filters.text([buttons.btn_my_games]), show_first_game)
