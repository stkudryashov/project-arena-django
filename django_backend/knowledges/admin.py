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
        ('Выбор времени', {
            'fields': ('time_unselect_emoji', 'time_select_emoji', 'btn_continue_time')
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
        ('Поиск игры', {
            'fields': ('btn_search_about', 'btn_search_enter', 'btn_search_next', 'search_enter',
                       'search_already_enter', 'search_not_free_space', 'msg_games_empty')
        }),
        ('Поиск друзей', {
            'fields': ('friends_text', 'friends_enter_text', 'friends_404_text', 'friends_invite_msg',
                       'friends_already_text', 'friends_is_you_text', 'friends_send_text', 'friends_request_text',
                       'friends_request_fall', 'friends_request_decline', 'friends_btn_add_new', 'friends_btn_add',
                       'friends_btn_decline')
        }),
    )

    readonly_fields = ('play_skill_params',)

    list_display = ('language',)
    list_display_links = ('language',)
