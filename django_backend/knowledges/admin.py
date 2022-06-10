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
            'fields': ('error_phone_number', 'error_username', 'error_date_of_birth', 'error_city')
        }),
        ('Сообщение после регистрации', {
            'fields': ('success_reg',)
        }),
        ('Уровни игры (через запятую)', {
            'fields': ('play_skill_params',)
        }),
        ('Эмодзи выбора времени', {
            'fields': ('time_unselect_emoji', 'time_select_emoji')
        }),
        ('Кнопки главного меню', {
            'fields': ('menu_message_text', 'btn_future_games', 'btn_my_games', 'btn_friends',
                       'btn_profile', 'btn_notifications')
        }),
        ('Кнопки меню редактирования', {
            'fields': ('edit_message_text', 'btn_edit_phone', 'btn_edit_name', 'btn_edit_date_of_birth',
                       'btn_edit_city', 'btn_edit_level', 'btn_edit_playtime')
        }),
        ('Дополнительные кнопки', {
            'fields': ('btn_back_menu',)
        }),
    )

    list_display = ('language',)
    list_display_links = ('language',)
