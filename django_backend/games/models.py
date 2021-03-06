from datetime import timedelta
from django.db import models
from django.utils import dateformat

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
        ('recruitment_done', 'Набор закончен'),
        ('is_over', 'Закончена'),
        ('canceled', 'Отменена'),
    )

    status = models.CharField(choices=GAME_STATUS, max_length=32, verbose_name='Статус')

    GAME_LEVEL = (
        ('Новичок', 'Новичок'),
        ('Средний', 'Средний'),
        ('Высокий', 'Высокий'),
    )

    level = models.CharField(choices=GAME_LEVEL, max_length=32, verbose_name='Уровень игры')

    send_t = models.DateTimeField(blank=True, null=True, verbose_name='Старт уведомлений')
    rule_n = models.IntegerField(blank=True, null=True, verbose_name='Получат уведомления')

    @property
    def free_space(self):
        """Число свободных мест в игре"""

        space = self.max_players - self.players.filter(status__in=['signed_up', 'confirmed']).count()
        return space if space > 0 else 0
    free_space.fget.short_description = 'Свободно мест'

    @property
    def reserve_count(self):
        """Число свободных резервных мест в игре"""

        reserve_percent = Knowledge.objects.get(language='RU').reserve_percent
        return int(self.max_players * (reserve_percent / 100)) - self.players.filter(status='reserve').count()
    reserve_count.fget.short_description = 'Резервных мест'

    @property
    def has_space(self):
        """Есть ли свободные места в игре"""

        return self.free_space > 0

    @property
    def has_reserve_space(self):
        """Есть ли свободные резервные места в игре"""

        return self.reserve_count > 0

    def print(self):
        date = dateformat.format(self.datetime, 'd E')
        time = dateformat.time_format(self.datetime, 'H:i')

        return f'Дата игры: {date} {time}\n' \
               f'Максимально игроков: {self.max_players}\n' \
               f'Свободно мест: {self.free_space}\n' \
               f'Резервных мест: {self.reserve_count}\n' \
               f'Цена участия: {self.price}\n' \
               f'Манеж: {self.arena.title}\n'

    def save(self, *args, **kwargs):
        super(Game, self).save(*args, **kwargs)

        # Удаление старых уведомлений по этой игре
        if ClockedSchedule.objects.filter(periodictask__name__contains=f'Telegram Notification {self.id}').exists():
            ClockedSchedule.objects.filter(periodictask__name__contains=f'Telegram Notification {self.id}').delete()

        if self.status == 'pending':
            # Подбор пользователей для уведомления по характеристикам

            all_users_ids = set()

            levels_ids = list(set(UserCharacteristic.objects.filter(
                characteristic__title='Уровень игры',
                value=self.level
            ).values_list('user__telegram_id', flat=True)))

            for rule in RuleCharacteristic.objects.all().order_by('rule__time'):
                users_ids = set()

                if rule.query == 'equals':
                    users_ids = set(UserCharacteristic.objects.filter(
                        characteristic=rule.characteristic,
                        value=rule.value,
                        user__notifications=True,
                        user__city=self.arena.city,
                        user__telegram_id__in=levels_ids
                    ).values_list('user__telegram_id', flat=True))

                if rule.query == 'lt':
                    users_ids = set(UserCharacteristic.objects.filter(value__regex=r'^\d+$').annotate(
                        int_value=Cast('value', output_field=IntegerField())
                    ).filter(
                        characteristic=rule.characteristic,
                        int_value__lt=int(rule.value),
                        user__notifications=True,
                        user__city=self.arena.city,
                        user__telegram_id__in=levels_ids
                    ).values_list('user__telegram_id', flat=True))

                if rule.query == 'gt':
                    users_ids = set(UserCharacteristic.objects.filter(value__regex=r'^\d+$').annotate(
                        int_value=Cast('value', output_field=IntegerField())
                    ).filter(
                        characteristic=rule.characteristic,
                        int_value__gt=int(rule.value),
                        user__notifications=True,
                        user__city=self.arena.city,
                        user__telegram_id__in=levels_ids
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
                        clocked_time=send_t - timedelta(hours=7)  # Минус для синхронизации UTC
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

        if self.status == 'pending' or self.status == 'recruitment_done':
            info = Knowledge.objects.get(language='RU')
            confirm_time = timedelta(hours=info.notifications_confirm.hour, minutes=info.notifications_confirm.minute)

            clocked_schedule = ClockedSchedule.objects.create(
                clocked_time=self.datetime - confirm_time - timedelta(hours=7)  # Минус для синхронизации UTC
            )

            PeriodicTask.objects.create(
                name=f'Telegram Notification {self.id} Confirm',
                task='notify_game_confirm',
                clocked=clocked_schedule,
                args=json.dumps([self.id]),
                one_off=True
            )

        if self.status == 'is_over':
            users_ids = set(self.players.filter(status='confirmed').values_list('user__telegram_id', flat=True))

            clocked_schedule = ClockedSchedule.objects.create(
                clocked_time=datetime.now() - timedelta(hours=7)  # Минус для синхронизации UTC
            )

            PeriodicTask.objects.create(
                name=f'Telegram Notification {self.id} End',
                task='end_game_notification_task',
                clocked=clocked_schedule,
                args=json.dumps([self.id, list(users_ids)]),
                one_off=True
            )

        if self.status == 'canceled':
            users_ids = set(self.players.all().values_list('user__telegram_id', flat=True))

            clocked_schedule = ClockedSchedule.objects.create(
                clocked_time=datetime.now() - timedelta(hours=7)  # Минус для синхронизации UTC
            )

            PeriodicTask.objects.create(
                name=f'Telegram Notification {self.id} Canceled',
                task='canceled_game_notification_task',
                clocked=clocked_schedule,
                args=json.dumps([self.id, list(users_ids)]),
                one_off=True
            )

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
        ('reserve', 'В резерве'),
        ('refused', 'Отказался'),
    )

    status = models.CharField(choices=PLAYER_STATUS, max_length=32, verbose_name='Статус', default=PLAYER_STATUS[0][0])

    def __str__(self):
        return f'{self.user.telegram_username} - {self.game.arena} {self.game.datetime}'

    class Meta:
        verbose_name = 'Игра пользователя'
        verbose_name_plural = 'Игры пользователей'
