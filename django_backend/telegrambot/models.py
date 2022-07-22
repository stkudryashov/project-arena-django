from django.db import models

from arenas.models import City


class TelegramUser(models.Model):
    """Модель пользователя Telegram бота"""

    username = models.CharField(max_length=128, verbose_name='Имя пользователя')
    telegram_username = models.CharField(max_length=128, verbose_name='Telegram', blank=True, null=True)

    phone_number = models.CharField(max_length=32, verbose_name='Номер телефона')
    telegram_img = models.ImageField(upload_to='users/', blank=True, verbose_name='Фото')

    date_of_birth = models.DateField(verbose_name='Дата рождения')
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='Город')

    telegram_id = models.CharField(max_length=16, verbose_name='Telegram ID')
    notifications = models.BooleanField(default=True, verbose_name='Уведомления')

    is_banned = models.BooleanField(default=False, verbose_name='Статус блокировки')

    def __str__(self):
        return f'{self.telegram_username}-{self.id}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Friendship(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='friends', verbose_name='Пригласил')
    friend = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name='Друг')

    def __str__(self):
        return f'{self.user.telegram_username} - {self.friend.telegram_username}'

    class Meta:
        verbose_name = 'Друг пользователя'
        verbose_name_plural = 'Друзья пользователей'

        constraints = [
            models.UniqueConstraint(fields=['user', 'friend'], name='unique_user_friend'),
        ]
