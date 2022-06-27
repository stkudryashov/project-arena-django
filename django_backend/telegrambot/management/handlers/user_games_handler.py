from django.utils import dateformat

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler, MessageHandler, Filters

from games.models import TelegramUserGame
from knowledges.models import Knowledge
from telegrambot.management.tools import get_user_or_notify
from telegrambot.models import TelegramUser


def get_user_games(update: Update, context: CallbackContext, user: TelegramUser = None, last_id=None):
    current_game = None

    if last_id:
        current_game = TelegramUserGame.objects.filter(user=user, pk__gt=last_id).order_by('id').exclude(
            status=TelegramUserGame.PLAYER_STATUS[2][0]).first()

    if current_game is None:
        current_game = TelegramUserGame.objects.filter(user=user).order_by('id').exclude(
            status=TelegramUserGame.PLAYER_STATUS[2][0]).first()

    if current_game is None:
        update.effective_message.reply_text(Knowledge.objects.get(language='RU').my_games_no_games)
        return

    game = current_game.game

    date = dateformat.format(game.datetime, 'd E')
    time = dateformat.time_format(game.datetime, 'H:i')

    message = f'Дата игры: {date} {time}\n' \
              f'Максимально игроков: {game.max_players}\n' \
              f'Свободно мест: {game.free_space}\n' \
              f'Цена участия: {game.price}\n' \
              f'Адрес манежа: {game.arena.address}\n'

    buttons = [
        [
            InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_about,
                                 callback_data=f'MyGames about {current_game.id}'),
            InlineKeyboardButton(Knowledge.objects.get(language='RU').my_games_cancel_btn,
                                 callback_data=f'MyGames leave {current_game.id}'),
        ]
    ]

    if user.games.exclude(status=TelegramUserGame.PLAYER_STATUS[2][0]).count() > 1:
        buttons.append([InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_next,
                                             callback_data=f'MyGames next {current_game.id}')])

    if game.arena.photo:
        update.effective_message.reply_photo(game.arena.photo, message,
                                             reply_markup=InlineKeyboardMarkup(buttons))
    else:
        update.effective_message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons))


def get_about(update: Update, context: CallbackContext, user: TelegramUser, last_id):
    """Информация о манеже"""

    current_game = TelegramUserGame.objects.filter(id=last_id).first().game

    message = f'Название: {current_game.arena.title}\n' \
              f'Описание: {current_game.arena.description}\n' \
              f'Телефон: {current_game.arena.phone_number}\n' \
              f'Адрес: {current_game.arena.address}\n'

    markup = InlineKeyboardMarkup.from_column(
        [InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_back,
                              callback_data=f'MyGames next {last_id}')]
    )

    if current_game.arena.photo:
        update.effective_message.reply_photo(current_game.arena.photo, message, reply_markup=markup)
    else:
        update.effective_message.reply_text(message, reply_markup=markup)


def user_leave_game(update: Update, context: CallbackContext, user: TelegramUser, last_id=None):
    game: TelegramUserGame = TelegramUserGame.objects.filter(user=user, id=last_id).first()

    if game is None:
        update.effective_message.reply_text("Произошла ошибка. Игра не была найдена, а это странно..")
        return

    game.delete()

    update.effective_message.reply_text(Knowledge.objects.get(language='RU').my_games_cancel_text)


@get_user_or_notify
def show_first_game(update: Update, context: CallbackContext, user: TelegramUser):
    get_user_games(update, context, user)


@get_user_or_notify
def _user_game_handler(update: Update, context: CallbackContext, user: TelegramUser):
    button_press = update.callback_query

    button_data = button_press.data.split(" ")

    if button_data[0] != "MyGames":
        return

    command = button_data[1]

    if command == "leave":
        last_id = button_data[2]
        user_leave_game(update, context, user, last_id)

    elif command == "next":
        last_id = button_data[2]
        get_user_games(update, context, user, last_id)

    elif command == "about":
        last_id = button_data[2]
        get_about(update, context, user, last_id)

    button_press.message.delete()


def get_user_games_handlers():
    buttons = Knowledge.objects.get(language='RU')

    return CallbackQueryHandler(_user_game_handler, pattern=r'^MyGames'), MessageHandler(
        Filters.text([buttons.btn_my_games]), show_first_game)
