from django.contrib import admin

from games.models import Game, TelegramUserGame


class TelegramUserGameInLine(admin.TabularInline):
    model = TelegramUserGame
    extra = 0
    verbose_name_plural = 'Игроки'


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'arena', 'max_players', 'free_space', 'price', 'status')
    inlines = [TelegramUserGameInLine]

    STATUS_HELP = ' '.join(['<p>Уведомления для набора будут отправлены только при статусе "Ожидает".</p>'])

    fieldsets = (
        ('Дата и время игры', {
            'fields': ('datetime', 'send_t', 'rule_n')
        }),
        ('Количество мест', {
            'fields': ('max_players', 'free_space', 'reserve_count')
        }),
        ('Цена участия', {
            'fields': ('price', 'level')
        }),
        ('Место проведения', {
            'fields': ('arena',)
        }),
        ('Статус игры (видно в поиске при статусе "Ожидает")', {
            'fields': ('status',),
            'description': STATUS_HELP
        })
    )

    list_filter = ('arena__city', 'status')
    readonly_fields = ('free_space', 'reserve_count', 'send_t', 'rule_n')


@admin.register(TelegramUserGame)
class TelegramUserGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'status')
