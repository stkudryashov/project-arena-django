from django.contrib import admin

from games.models import Game, TelegramUserGame


class TelegramUserGameInLine(admin.TabularInline):
    model = TelegramUserGame
    extra = 0
    verbose_name_plural = 'Игроки'


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'arena', 'status', 'free_space')
    inlines = [TelegramUserGameInLine]

    fieldsets = (
        ('Дата и время игры', {
            'fields': ('datetime',)
        }),
        ('Количество мест', {
            'fields': ('max_players', 'free_space')
        }),
        ('Цена участия', {
            'fields': ('price',)
        }),
        ('Место проведения', {
            'fields': ('arena', 'status')
        })
    )

    readonly_fields = ('free_space',)


@admin.register(TelegramUserGame)
class TelegramUserGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'status')
