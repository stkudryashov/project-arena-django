from django.db import models

from arenas.models import Arena
from telegrambot.models import TelegramUser


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
