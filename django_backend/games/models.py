from django.db import models

from arenas.models import Arena
from telegrambot.models import TelegramUser

from datetime import datetime


class Game(models.Model):
    """Модель игры привязанной к определенному манежу"""

    datetime = models.DateTimeField(verbose_name='Дата')
    max_players = models.PositiveIntegerField(verbose_name='Количество мест', default=0)
    price = models.PositiveIntegerField(verbose_name='Стоимость участия')

    arena = models.ForeignKey(Arena, on_delete=models.PROTECT, related_name='games', verbose_name='Манеж')

    GAME_STATUS = (
        ('pending', 'Ожидает'),
        ('is_over', 'Закончена'),
        ('canceled', 'Отменена'),
    )

    status = models.CharField(choices=GAME_STATUS, max_length=32, verbose_name='Статус')

    @property
    def free_space(self):
        """Число свободных мест в игре"""

        space = self.max_players - self.players.all().count()
        return space if space > 0 else 0

    free_space.fget.short_description = 'Свободно мест'

    @property
    def has_space(self):
        """Есть ли свободные места в игре"""

        return self.free_space > 0

    # @property
    # def is_end(self):
    #     """Закончилась ли игра"""
    #
    #     return self.datetime < datetime.now()

    def __str__(self):
        return f'{self.datetime} - {self.arena}'

    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'


class TelegramUserGame(models.Model):
    """Промежуточная модель между пользователем и игрой"""

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
