from django.db import models

from telegrambot.models import TelegramUser


class DayOfTheWeek(models.Model):
    """Модель дней недели"""

    title = models.CharField(max_length=32, unique=True, verbose_name='День недели')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'День недели'
        verbose_name_plural = 'Дни недели'

        ordering = ('id',)


class UserTime(models.Model):
    """Модель времени и пользователей, которым оно удобно"""

    time = models.TimeField(verbose_name='Время')

    day_of_the_week = models.ForeignKey(DayOfTheWeek, on_delete=models.PROTECT, verbose_name='День недели')

    users = models.ManyToManyField(TelegramUser, related_name='times', blank=True,
                                   verbose_name='Готовы играть в это время')

    def __str__(self):
        return f'{self.day_of_the_week} {self.time}'

    class Meta:
        verbose_name = 'Время'
        verbose_name_plural = 'Время'

        ordering = ('day_of_the_week', 'time')
