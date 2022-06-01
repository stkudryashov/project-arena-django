from django.db import models

from telegrambot.models import TelegramUser


class Characteristic(models.Model):
    """Модель названий характеристик"""

    title = models.CharField(max_length=128, verbose_name='Название')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'


class UserCharacteristic(models.Model):
    """Модель характеристик Telegram пользователя"""

    value = models.CharField(max_length=128, verbose_name='Значение')

    characteristic = models.ForeignKey(Characteristic, on_delete=models.PROTECT, verbose_name='Характеристика')

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, blank=True,
                             related_name='characteristics', verbose_name='Пользователь')

    def __str__(self):
        return f'{self.user} - {self.characteristic}'

    class Meta:
        verbose_name = 'Характеристика пользователя'
        verbose_name_plural = 'Характеристики пользователей'

        constraints = [
            models.UniqueConstraint(fields=['user', 'characteristic'], name='unique_user_characteristic'),
        ]
