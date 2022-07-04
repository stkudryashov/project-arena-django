from django.db import models


class City(models.Model):
    """Модель городов"""

    title = models.CharField(max_length=32, verbose_name='Город')
    timezone = models.CharField(max_length=32, blank=True, null=True, verbose_name='Часовой пояс')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class Arena(models.Model):
    """Модель манежей"""

    title = models.CharField(max_length=32, verbose_name='Название манежа')

    address = models.CharField(max_length=128, verbose_name='Адрес')
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='Город')

    phone_number = models.CharField(max_length=32, verbose_name='Номер телефона')
    description = models.TextField(verbose_name='Описание')

    logo = models.ImageField(upload_to='arenas/', blank=True, verbose_name='Логотип')

    def __str__(self):
        return f'{self.address} - {self.city}'

    class Meta:
        verbose_name = 'Манеж'
        verbose_name_plural = 'Манежи'


class ArenaPhoto(models.Model):
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE, related_name='photos', verbose_name='Манеж')
    photo = models.ImageField(upload_to='arenas/', blank=True, verbose_name='Фото')

    def __str__(self):
        return f'{self.arena} - {self.photo}'

    class Meta:
        verbose_name = 'Фото манежа'
        verbose_name_plural = 'Фото манежей'
