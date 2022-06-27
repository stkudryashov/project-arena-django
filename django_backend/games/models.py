from datetime import timedelta
from django.db import models

from django_celery_beat.models import ClockedSchedule, PeriodicTask

from arenas.models import Arena
from telegrambot.models import TelegramUser

import json


class Game(models.Model):
    datetime = models.DateTimeField(verbose_name='Дата')
    max_players = models.PositiveIntegerField(verbose_name='Количество мест')
    price = models.PositiveIntegerField(verbose_name='Стоимость участия')

    arena = models.ForeignKey(Arena, on_delete=models.PROTECT, related_name='games', verbose_name='Манеж')

    GAME_STATUS = (
        ('pending', 'Ожидает'),
        ('is_over', 'Закончена'),
        ('canceled', 'Отменена'),
    )

    status = models.CharField(choices=GAME_STATUS, max_length=32, verbose_name='Статус')

    def save(self, *args, **kwargs):
        super(Game, self).save(*args, **kwargs)

        if ClockedSchedule.objects.filter(periodictask__name=f'Telegram Notification {self.id}').exists():
            ClockedSchedule.objects.filter(periodictask__name=f'Telegram Notification {self.id}').delete()

        clocked_schedule = ClockedSchedule.objects.create(
            clocked_time=self.datetime - timedelta(minutes=15) - timedelta(hours=3)  # Костыль для scheduler
        )  # Из даты вычитаем нужные 15 минут до игры и еще минус три часа для синхронизации UTC

        PeriodicTask.objects.create(
            name=f'Telegram Notification {self.id}',
            task='games_notification_task',
            clocked=clocked_schedule,
            args=json.dumps([self.id]),
            one_off=True
        )

    def __str__(self):
        return f'{self.datetime} - {self.arena}'

    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'


class TelegramUserGame(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, blank=True,
                             related_name='games', verbose_name='Пользователь')

    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True,
                             related_name='players', verbose_name='Игра')

    PLAYER_STATUS = (
        ('signed_up', 'Записался'),
        ('confirmed', 'Подтвердил'),
        ('refused', 'Отказался'),
    )

    status = models.CharField(choices=PLAYER_STATUS, max_length=32, verbose_name='Статус')

    def __str__(self):
        return f'{self.user.telegram_username} - {self.game.arena} {self.game.datetime}'

    class Meta:
        verbose_name = 'Игра пользователя'
        verbose_name_plural = 'Игры пользователей'
