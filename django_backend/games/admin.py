from django.contrib import admin

from games.models import Game, TelegramUserGame


class TelegramUserGameInLine(admin.TabularInline):
    model = TelegramUserGame
    verbose_name_plural = 'Игроки'


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'arena', 'status')
    inlines = [TelegramUserGameInLine]


@admin.register(TelegramUserGame)
class TelegramUserGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'status')
