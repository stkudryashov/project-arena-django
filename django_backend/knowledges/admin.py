from django.contrib import admin

from knowledges.models import Knowledge


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Локализация', {
            'fields': ('language',)
        }),
        ('Регистрация', {
            'fields': ('reg_phone_number', 'reg_username', 'reg_date_of_birth', 'reg_city', 'reg_level', 'reg_playtime')
        }),
        ('Ошибки ввода регистрации', {
            'fields': ('error_phone_number', 'error_username', 'error_date_of_birth')
        }),
        ('Уровни игры (через запятую)', {
            'fields': ('play_skill_params',)
        }),
        ('Эмодзи выбора времени', {
            'fields': ('time_unselect_emoji', 'time_select_emoji')
        }),
        ('Главное меню', {
            'fields': ('btn_future_games', 'btn_my_games', 'btn_friends', 'btn_profile', 'btn_notifications')
        })
    )

    list_display = ('language',)
    list_display_links = ('language',)
