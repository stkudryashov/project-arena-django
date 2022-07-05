from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import CallbackContext, CallbackQueryHandler

from games.models import Game, TelegramUserGame
from games.tasks import notify_friends_about_game
from knowledges.models import Knowledge
from telegrambot.models import TelegramUser

from django.db.models import Q
from datetime import datetime
from django.utils import dateformat

import telegram


def search_games(update: Update, context: CallbackContext, last_id=None, is_back=False):
    """Поиск игры и вывод информации о ней"""

    user = TelegramUser.objects.get(telegram_id=update.effective_user.id)

    search_query = Q(
        datetime__gt=datetime.now(),
        arena__city=user.city,
        status='pending'
    )

    if last_id:
        if is_back:
            search_query &= Q(pk__lt=last_id)
        else:
            search_query &= Q(pk__gt=last_id)

    current_game = Game.objects.filter(search_query).exclude(players__user=user).order_by('id').first()

    if current_game is None:
        update.effective_message.reply_text(Knowledge.objects.get(language='RU').msg_games_empty)
        return

    message = current_game.print()

    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_about,
                               callback_data=f'SearchAbout {current_game.id}'),
          InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_enter,
                               callback_data=f'SearchEnter {current_game.id}')],
         [InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_back,
                               callback_data=f'SearchBack {current_game.id}'),
          InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_next,
                               callback_data=f'SearchNext {current_game.id}')]]
    )

    if current_game.arena.photos.exists():
        update.effective_message.reply_photo(current_game.arena.photos.first().photo, message, reply_markup=markup)
    else:
        update.effective_message.reply_text(message, reply_markup=markup)


def search_join_game(update: Update, context: CallbackContext, game_id):
    user = TelegramUser.objects.filter(telegram_id=update.effective_user.id).first()

    # На всякий случай буду всегда проверять пользователя
    if user is None:
        return False

    game = Game.objects.filter(id=game_id).first()

    if game.players.all().filter(user=user).exists():
        update.effective_message.reply_text(Knowledge.objects.get(language='RU').search_already_enter)
        return False

    if not game.has_space:
        if game.has_reserve_space:
            game.players.create(user=user, status='reserve')
            update.effective_message.reply_text(Knowledge.objects.get(language='RU').reserve_message)

            if game.has_reserve_space == 0:
                game.status = 'recruitment_done'
                game.save()
                
            return True
        else:
            update.effective_message.reply_text(Knowledge.objects.get(language='RU').search_not_free_space)
            return False

    game.players.create(user=user)
    update.effective_message.reply_text(Knowledge.objects.get(language='RU').search_enter)

    if user.friends.all().exists():
        markup = InlineKeyboardMarkup.from_row([
            InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_game_friends_yes,
                                 callback_data=f'SearchNotify True {game_id}'),
            InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_game_friends_no,
                                 callback_data='SearchNotify False')
        ])

        update.effective_message.reply_text(Knowledge.objects.get(language='RU').msg_game_friends, reply_markup=markup)

    return True


def search_about(update: Update, context: CallbackContext, game_id):
    """Информация о манеже"""

    current_game = Game.objects.filter(id=game_id).first()

    message = current_game.arena.print()

    # markup = InlineKeyboardMarkup.from_column(
    #     [InlineKeyboardButton(Knowledge.objects.get(language='RU').btn_search_back,
    #                           callback_data=f'SearchNext {last_id}')]
    # )

    if current_game.arena.photos.exists():
        media_group = []

        for i, photo in enumerate(current_game.arena.photos.all()):
            media_group.append(InputMediaPhoto(media=photo.photo, caption=message if i == 0 else ''))

        update.effective_message.reply_media_group(media_group)
    else:
        update.effective_message.reply_text(message)


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

            if last_id == 'None':
                last_id = None

            search_games(update, context, last_id)
    elif 'SearchBack' in button_press.data:
        try:
            button_press.message.delete()
        except telegram.TelegramError:
            pass
        finally:
            last_id = button_press.data.split()[1]

            if last_id == 'None':
                last_id = None

            search_games(update, context, last_id, is_back=True)
    elif 'SearchEnter' in button_press.data:
        try:
            button_press.message.delete()
        except telegram.TelegramError:
            pass
        finally:
            search_join_game(update, context, button_press.data.split()[1])
    elif 'SearchAbout' in button_press.data:
        try:
            pass
        except telegram.TelegramError:
            pass
        finally:
            game_id = button_press.data.split()[1]
            search_about(update, context, game_id)
    elif 'SearchNotify' in button_press.data:
        try:
            button_press.message.delete()
        except telegram.TelegramError:
            pass
        finally:
            answer = button_press.data.split()[1]

            if answer == 'True':
                notify_friends_about_game.delay(update.effective_user.id, button_press.data.split()[2])
                update.effective_user.send_message('Уведомления отправлены ✅')
            else:
                update.effective_user.send_message(Knowledge.objects.get(language='RU').msg_game_friends_no)
