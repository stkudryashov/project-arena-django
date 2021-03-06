from django.db import models


class Knowledge(models.Model):
    """Модель справочника с текстовками для Telegram бота"""

    language = models.CharField(max_length=16, default='RU', verbose_name='Язык справочника', unique=True)

    reg_phone_number = models.CharField(max_length=128, verbose_name='Запрос номера телефона')
    reg_username = models.CharField(max_length=128, verbose_name='Запрос имени и фамилии')
    reg_date_of_birth = models.CharField(max_length=128, verbose_name='Запрос даты рождения')
    reg_city = models.CharField(max_length=128, verbose_name='Запрос города')
    reg_level = models.CharField(max_length=128, verbose_name='Запрос уровня игры')
    reg_playtime = models.CharField(max_length=128, verbose_name='Запрос времени игры')

    error_phone_number = models.CharField(max_length=128, verbose_name='Ошибка номера телефона')
    error_username = models.CharField(max_length=128, verbose_name='Ошибка имени и фамилии')
    error_date_of_birth = models.CharField(max_length=128, verbose_name='Ошибка даты рождения')
    error_city = models.CharField(max_length=128, verbose_name='Ошибка города')

    success_reg = models.TextField(verbose_name='Успешная регистрация')
    friends_reg = models.TextField(verbose_name='Текст "Добавь друга"')

    play_skill_params = models.CharField(max_length=64, verbose_name='Уровни игры')
    reliable_params = models.CharField(max_length=64, verbose_name='Рейтинг надежности')
    digital_start = models.IntegerField(verbose_name='Цифровой рейтинг', default=0)

    reliable_up_games = models.PositiveIntegerField(verbose_name='Игр подряд для повышения', default=2)

    time_unselect_emoji = models.CharField(max_length=16, verbose_name='Эмодзи (не выбрано)')
    time_select_emoji = models.CharField(max_length=16, verbose_name='Эмодзи (выбрано)')

    btn_continue_time = models.CharField(max_length=32, verbose_name='Кнопка "Подтвердить время"')

    menu_message_text = models.CharField(max_length=64, verbose_name='Сообщение "Главное меню"')

    btn_future_games = models.CharField(max_length=32, verbose_name='Кнопка "Предстоящие игры"')
    btn_my_games = models.CharField(max_length=32, verbose_name='Кнопка "Мои игры"')
    btn_friends = models.CharField(max_length=32, verbose_name='Кнопка "Друзья"')
    btn_profile = models.CharField(max_length=32, verbose_name='Кнопка "Профиль"')

    btn_notifications_on = models.CharField(max_length=32, verbose_name='Кнопка "Уведомления (вкл.)"')
    btn_notifications_off = models.CharField(max_length=32, verbose_name='Кнопка "Уведомления (отк.)"')

    edit_message_text = models.CharField(max_length=64, verbose_name='Сообщение "Редактирование профиля"')

    btn_edit_phone = models.CharField(max_length=32, verbose_name='Кнопка "Изменить телефон"')
    btn_edit_name = models.CharField(max_length=32, verbose_name='Кнопка "Изменить имя"')
    btn_edit_date_of_birth = models.CharField(max_length=32, verbose_name='Кнопка "Изменить дату рождения"')
    btn_edit_city = models.CharField(max_length=32, verbose_name='Кнопка "Изменить город"')
    btn_edit_level = models.CharField(max_length=32, verbose_name='Кнопка "Изменить уровень игры"')
    btn_edit_playtime = models.CharField(max_length=32, verbose_name='Кнопка "Изменить удобное время"')

    edit_characteristic_request = models.CharField(max_length=64, verbose_name='Запрос значения характеристики')
    edit_characteristic_success = models.CharField(max_length=64, verbose_name='Характеристика изменена')

    edit_please_select_buttons = models.CharField(max_length=64, verbose_name='Выберите пункт из меню')

    btn_back_menu = models.CharField(max_length=32, verbose_name='Кнопка "Назад в меню"')

    btn_search_about = models.CharField(max_length=32, verbose_name='Кнопка "О манеже"')
    btn_search_enter = models.CharField(max_length=32, verbose_name='Кнопка "Записаться"')
    btn_search_back = models.CharField(max_length=32, verbose_name='Кнопка "Назад"')
    btn_search_next = models.CharField(max_length=32, verbose_name='Кнопка "Далее"')

    search_enter = models.CharField(max_length=64, verbose_name='Вы записались на игру')
    search_already_enter = models.CharField(max_length=64, verbose_name='Уже записан на игру')
    search_not_free_space = models.CharField(max_length=64, verbose_name='В игре нет мест')

    msg_games_empty = models.CharField(max_length=64, verbose_name='Сообщение о конце поиска')

    msg_game_friends = models.CharField(max_length=64, verbose_name='Текст "Уведомить друзей"')
    msg_game_friends_no = models.CharField(max_length=64, verbose_name='Текст "Отказался уведомить"')
    btn_game_friends_yes = models.CharField(max_length=32, verbose_name='Кнопка "Уведомить"')
    btn_game_friends_no = models.CharField(max_length=32, verbose_name='Кнопка "Не нужно"')

    friends_text = models.CharField(max_length=64, verbose_name='Старт добавления друга')
    friends_enter_text = models.CharField(max_length=64, verbose_name='Запрос имени друга')

    friends_404_text = models.TextField(verbose_name='Друг не найден')
    friends_invite_msg = models.TextField(verbose_name='Сообщение для приглашения')

    friends_already_text = models.CharField(max_length=64, verbose_name='Ошибка "Друг уже добавлен"')
    friends_is_you_text = models.CharField(max_length=64, verbose_name='Ошибка "Себя добавить нельзя"')

    friends_send_text = models.CharField(max_length=64, verbose_name='Уведомление для друга')
    friends_request_text = models.CharField(max_length=64, verbose_name='Запрос дружбы отправлен')

    friends_request_fall = models.CharField(max_length=64, verbose_name='Запрос дружбы отклонен')
    friends_request_decline = models.CharField(max_length=64, verbose_name='Вы отклонили дружбу')

    friends_btn_add_new = models.CharField(max_length=32, verbose_name='Кнопка "Добавить нового друга"')
    friends_btn_add = models.CharField(max_length=32, verbose_name='Кнопка "Принять приглашение"')
    friends_btn_decline = models.CharField(max_length=32, verbose_name='Кнопка "Отклонить приглашение"')

    my_games_no_games = models.CharField(max_length=32, verbose_name='Вы не записаны на игры')
    my_games_cancel_btn = models.CharField(max_length=32, verbose_name='Кнопка "Отменить запись"')
    my_games_cancel_text = models.CharField(max_length=64, verbose_name='Текст отмены записи')

    my_games_safe_time = models.TimeField(verbose_name='За сколько до игры можно снять запись')
    my_games_wrong_text = models.TextField(verbose_name='Текст "Рейтинг упадет"')

    my_games_btn_yes = models.CharField(max_length=32, verbose_name='Кнопка "Уверен"')
    my_games_btn_no = models.CharField(max_length=32, verbose_name='Кнопка "Оставить запись"')

    notifications_start = models.TimeField(verbose_name='Старт уведомлений')
    notifications_end = models.TimeField(verbose_name='Конец уведомлений')
    notifications_delay = models.TimeField(verbose_name='Задержка до начала игры')

    notifications_confirm_text = models.TextField(verbose_name='Текст "Подтвердите участие"')
    notifications_confirm_reserve = models.TextField(verbose_name='Текст "Резервное подтверждение"')
    notifications_confirm = models.TimeField(verbose_name='Отправить подтверждение')
    notifications_confirm_wait = models.TimeField(verbose_name='Время на подтверждение')

    notifications_game_canceled = models.CharField(max_length=64, verbose_name='Игра была отменена')
    notifications_game_end = models.CharField(max_length=64, verbose_name='Игра завершилась')

    btn_notify_game_yes = models.CharField(max_length=32, verbose_name='Кнопка "Подтвердить участие"')
    btn_notify_game_no = models.CharField(max_length=32, verbose_name='Кнопка "Отказаться от игры"')

    polls_btn_send = models.CharField(max_length=32, verbose_name='Кнопка "Ответить"')
    polls_btn_cancel = models.CharField(max_length=32, verbose_name='Кнопка "Отменить"')

    polls_enter_text = models.CharField(max_length=32, verbose_name='Запрос ответа на опрос')
    polls_answer_ok = models.CharField(max_length=32, verbose_name='Ответ получен')

    reserve_percent = models.PositiveIntegerField(verbose_name='Процент резервных мест', default=50)
    reserve_message = models.TextField(verbose_name='Текст "Есть резервные места"')

    is_banned_text = models.TextField(verbose_name='Текст "Вам заблокированы игры"')

    def __str__(self):
        return f'{self.language}'

    class Meta:
        verbose_name = 'Справочник'
        verbose_name_plural = 'Справочники'
