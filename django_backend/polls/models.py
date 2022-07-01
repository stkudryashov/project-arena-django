from django.db import models

from arenas.models import City
from telegrambot.models import TelegramUser

from datetime import timedelta

from django_celery_beat.models import ClockedSchedule, PeriodicTask

import json


class Poll(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    datetime = models.DateTimeField(verbose_name='Дата')
    description = models.TextField(verbose_name='Описание')
    photo = models.ImageField(upload_to='polls/', blank=True, verbose_name='Фото')
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='cities', verbose_name='Город')

    def __str__(self):
        return f'{self.title} - {self.city} {self.datetime}'

    def save(self, *args, **kwargs):
        super(Poll, self).save(*args, **kwargs)

        if ClockedSchedule.objects.filter(periodictask__name__contains=f'Telegram Notification Poll {self.id}').exists():
            ClockedSchedule.objects.filter(periodictask__name__contains=f'Telegram Notification Poll {self.id}').delete()

        users_ids = [x.telegram_id for x in TelegramUser.objects.filter(city=self.city).all()]

        clocked_schedule = ClockedSchedule.objects.create(
            clocked_time=self.datetime - timedelta(hours=3)  # Минус для синхронизации UTC
        )

        PeriodicTask.objects.create(
            name=f'Telegram Notification Poll {self.id} New',
            task='new_poll_notification_task',
            clocked=clocked_schedule,
            args=json.dumps([self.id, list(users_ids)]),
            one_off=True
        )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class PollVariant(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, blank=True,
                             related_name='answers', verbose_name='Опрос')

    text = models.CharField(max_length=255, verbose_name="Текст")
    is_open = models.BooleanField(default=False, verbose_name='Требует развернутого ответа')

    def __str__(self):
        return f'{self.text} - {self.poll.title}'

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'


class UserPoll(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, blank=True,
                             related_name='users', verbose_name='Пользователь')

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, blank=True,
                             related_name='polls', verbose_name='Опрос')

    answer = models.TextField(verbose_name="Ответ")

    def __str__(self):
        return f'{self.user.telegram_username} - {self.poll.title}'

    class Meta:
        verbose_name = 'Ответы пользователя'
        verbose_name_plural = 'Ответы пользователей'
