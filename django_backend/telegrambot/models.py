from django.db import models

from arenas.models import City


class TelegramUser(models.Model):
    """Модель пользователя Telegram бота"""

    username = models.CharField(max_length=128, verbose_name='Имя пользователя')
    telegram_username = models.CharField(max_length=128, verbose_name='Telegram')

    phone_number = models.CharField(max_length=32, verbose_name='Номер телефона')
    telegram_img = models.ImageField(upload_to='users/', blank=True, verbose_name='Фото')

    date_of_birth = models.DateField(verbose_name='Дата рождения')
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='Город')

    telegram_id = models.CharField(max_length=16, verbose_name='Telegram ID')

    is_banned = models.BooleanField(default=False, verbose_name='Статус блокировки')

    def __str__(self):
        return f'{self.telegram_username}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'