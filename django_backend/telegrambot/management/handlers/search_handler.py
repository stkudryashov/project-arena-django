from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler

from games.models import Game, TelegramUserGame
from knowledges.models import Knowledge
from telegrambot.models import TelegramUser

from django.db.models import Q
from datetime import datetime

import telegram


def search_games(update: Update, context: CallbackContext, last_id=None):
    """Поиск игры и вывод информации о ней"""

    user = TelegramUser.objects.get(telegram_id=update.effective_user.id)

    search_query = Q(
        datetime__gt=datetime.now(),
        arena__city=user.city,
        status='pending'
    )

    if last_id:
        search_query &= Q(pk__gt=last_id)

    current_game = Game.objects.filter(search_query).order_by('id').first()

    if current_game is None:
        update.effective_message.reply_text(Knowledge.objects.get(language='RU').msg_games_empty)
        return

    message = f'Дата игры: {current_game.datetime}\n' \
              f'Максимально игроков: {current_game.max_players}\n' \
              f'Свободно мест: {current_game.free_space}\n' \
              f'Цена участия: {current_game.price}\n' \
              f'Адрес манежа: {current_game.arena.address}\n'

    markup = InlineKeyboardMarkup.from_column(
        [InlineKeyboardButton('О манеже', callback_data=f'SearchAbout {current_game.arena.id}'),
         InlineKeyboardButton('Записаться', callback_data=f'SearchEnter {current_game.id}'),
         InlineKeyboardButton('Далее', callback_data=f'SearchNext {current_game.id}')]
    )

    update.effective_message.reply_text(message, reply_markup=markup)


def search_join_game(update: Update, context: CallbackContext, game_id):
    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    # На всякий случай буду всегда проверять пользователя
    if user is None:
        return False

    game = Game.objects.filter(id=game_id).first()
    if game.players.all().filter(user=user).exists():
        update.effective_message.reply_text("Вы уже записаны на эту игру")
        return False

    if not game.has_space:
        update.effective_message.reply_text("К сожалению в игре не осталось мест!")
        return False

    game.players.create(user=user)
    update.effective_message.reply_text("Записали вас на эту игру!")
    return True


def search_callbacks(update: Update, context: CallbackContext):
    """Обработчик inline клавиатуры под сообщениями"""

    button_press = update.callback_query

    if 'SearchNext' in button_press.data:
        try:
            button_press.message.delete()
        except telegram.TelegramError:
            pass
        finally:
            last_id = button_press.data.split()[1]
            search_games(update, context, last_id)
    elif 'SearchEnter' in button_press.data:
        try:
            button_press.message.delete()
        except telegram.TelegramError:
            pass
        finally:
            search_join_game(update, context, button_press.data.split()[1])
