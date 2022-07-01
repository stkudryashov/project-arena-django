from datetime import timedelta
from django.db import models

from django_celery_beat.models import ClockedSchedule, PeriodicTask

from arenas.models import Arena
from telegrambot.models import TelegramUser
from notifications.models import RuleCharacteristic
from characteristics.models import UserCharacteristic
from knowledges.models import Knowledge

from django.db.models.functions import Cast
from django.db.models import IntegerField

from datetime import datetime

import json


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

    send_t = models.DateTimeField(blank=True, null=True, verbose_name='Старт уведомлений')
    rule_n = models.IntegerField(blank=True, null=True, verbose_name='Получат уведомления')

    def save(self, *args, **kwargs):
        super(Game, self).save(*args, **kwargs)

        # Удаление старых уведомлений по этой игре
        if ClockedSchedule.objects.filter(periodictask__name__contains=f'Telegram Notification {self.id}').exists():
            ClockedSchedule.objects.filter(periodictask__name__contains=f'Telegram Notification {self.id}').delete()

        if self.status == 'pending':
            # Подбор пользователей для уведомления по характеристикам

            all_users_ids = set()

            for rule in RuleCharacteristic.objects.all().order_by('rule__time'):
                users_ids = set()

                if rule.query == 'equals':
                    users_ids = set(UserCharacteristic.objects.filter(
                        characteristic=rule.characteristic,
                        value=rule.value,
                        user__notifications=True,
                        user__city=self.arena.city
                    ).values_list('user__telegram_id', flat=True))

                if rule.query == 'lt':
                    users_ids = set(UserCharacteristic.objects.filter(value__regex=r'^\d+$').annotate(
                        int_value=Cast('value', output_field=IntegerField())
                    ).filter(
                        characteristic=rule.characteristic,
                        int_value__lt=int(rule.value),
                        user__notifications=True,
                        user__city=self.arena.city
                    ).values_list('user__telegram_id', flat=True))

                if rule.query == 'gt':
                    users_ids = set(UserCharacteristic.objects.filter(value__regex=r'^\d+$').annotate(
                        int_value=Cast('value', output_field=IntegerField())
                    ).filter(
                        characteristic=rule.characteristic,
                        int_value__gt=int(rule.value),
                        user__notifications=True,
                        user__city=self.arena.city
                    ).values_list('user__telegram_id', flat=True))

                users_ids = users_ids - all_users_ids
                all_users_ids = all_users_ids | users_ids

                if users_ids:
                    info = Knowledge.objects.get(language='RU')
                    info_delay = timedelta(hours=info.notifications_delay.hour, minutes=info.notifications_delay.minute)

                    if datetime.now() + info_delay < self.datetime:
                        send_delay = self.datetime - info_delay
                    else:
                        send_delay = datetime.now()

                    send_t = send_delay + timedelta(hours=rule.rule.time.hour, minutes=rule.rule.time.minute)
                    self.send_t = send_delay

                    t_end = info.notifications_end
                    t_start = info.notifications_start

                    if t_end.hour < t_start.hour:
                        dt_end = datetime(send_t.year, send_t.month, send_t.day, t_end.hour, t_end.minute)
                        dt_start = datetime(send_t.year, send_t.month, send_t.day, t_start.hour, t_start.minute)
                    else:
                        if send_t.hour > t_end.hour:
                            dt_end = datetime(send_t.year, send_t.month, send_t.day, t_end.hour, t_end.minute)
                            dt_start = datetime(send_t.year, send_t.month, send_t.day, t_start.hour,
                                                t_start.minute) + timedelta(days=1)
                        else:
                            dt_end = datetime(send_t.year, send_t.month, send_t.day, t_end.hour,
                                              t_end.minute) - timedelta(days=1)
                            dt_start = datetime(send_t.year, send_t.month, send_t.day, t_start.hour, t_start.minute)

                    if dt_end < send_t < dt_start:
                        send_t = dt_start + timedelta(hours=rule.rule.time.hour, minutes=rule.rule.time.minute)
                        self.send_t = dt_start

                    clocked_schedule = ClockedSchedule.objects.create(
                        clocked_time=send_t - timedelta(hours=3)  # Минус для синхронизации UTC
                    )

                    PeriodicTask.objects.create(
                        name=f'Telegram Notification {self.id} {rule.id} New',
                        task='new_game_notification_task',
                        clocked=clocked_schedule,
                        args=json.dumps([self.id, list(users_ids)]),
                        one_off=True
                    )
            if all_users_ids:
                self.rule_n = len(all_users_ids)
            else:
                self.rule_n = 0

            super(Game, self).save(*args, **kwargs)
        elif self.status == 'canceled':
            users_ids = set(self.players.all().values_list('user__telegram_id', flat=True))

            clocked_schedule = ClockedSchedule.objects.create(
                clocked_time=datetime.now() - timedelta(hours=3)  # Минус для синхронизации UTC
            )

            PeriodicTask.objects.create(
                name=f'Telegram Notification {self.id} Canceled',
                task='canceled_game_notification_task',
                clocked=clocked_schedule,
                args=json.dumps([self.id, list(users_ids)]),
                one_off=True
            )

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

    status = models.CharField(choices=PLAYER_STATUS, max_length=32, verbose_name='Статус', default=PLAYER_STATUS[0][0])

    def __str__(self):
        return f'{self.user.telegram_username} - {self.game.arena} {self.game.datetime}'

    class Meta:
        verbose_name = 'Игра пользователя'
        verbose_name_plural = 'Игры пользователей'
