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

    def __str__(self):
        return f'{self.language}'

    class Meta:
        verbose_name = 'Справочник'
        verbose_name_plural = 'Справочники'
