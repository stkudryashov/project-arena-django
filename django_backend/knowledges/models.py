from django.db import models


class Knowledge(models.Model):
    """Модель справочника с текстовками для Telegram бота"""

    language = models.CharField(max_length=16, default='RU', verbose_name='Язык справочника')

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

    play_skill_params = models.CharField(max_length=128, verbose_name='Уровни игры')

    time_unselect_emoji = models.CharField(max_length=128, verbose_name='Эмодзи (не выбрано)')
    time_select_emoji = models.CharField(max_length=128, verbose_name='Эмодзи (выбрано)')

    menu_message_text = models.CharField(max_length=128, verbose_name='Сообщение "Главное меню"')

    btn_future_games = models.CharField(max_length=128, verbose_name='Кнопка "Предстоящие игры"')
    btn_my_games = models.CharField(max_length=128, verbose_name='Кнопка "Мои игры"')
    btn_friends = models.CharField(max_length=128, verbose_name='Кнопка "Друзья"')
    btn_profile = models.CharField(max_length=128, verbose_name='Кнопка "Профиль"')
    btn_notifications = models.CharField(max_length=128, verbose_name='Кнопка "Уведомления"')

    edit_message_text = models.CharField(max_length=128, verbose_name='Сообщение "Редактирование профиля"')

    btn_edit_phone = models.CharField(max_length=128, verbose_name='Кнопка "Изменить телефон"')
    btn_edit_name = models.CharField(max_length=128, verbose_name='Кнопка "Изменить имя"')
    btn_edit_date_of_birth = models.CharField(max_length=128, verbose_name='Кнопка "Изменить дату рождения"')
    btn_edit_city = models.CharField(max_length=128, verbose_name='Кнопка "Изменить город"')
    btn_edit_level = models.CharField(max_length=128, verbose_name='Кнопка "Изменить уровень игры"')
    btn_edit_playtime = models.CharField(max_length=128, verbose_name='Кнопка "Изменить удобное время"')

    btn_back_menu = models.CharField(max_length=128, verbose_name='Кнопка "Назад в меню"')

    def __str__(self):
        return f'{self.language}'

    class Meta:
        verbose_name = 'Справочник'
        verbose_name_plural = 'Справочники'