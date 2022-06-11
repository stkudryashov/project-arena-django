from django.contrib import admin

from games.models import Game, TelegramUserGame


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'arena', 'status')


@admin.register(TelegramUserGame)
class TelegramUserGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'status')
