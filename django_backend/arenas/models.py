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

    address = models.CharField(max_length=128, verbose_name='Адрес')
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='Город')

    phone_number = models.CharField(max_length=32, verbose_name='Номер телефона')
    description = models.TextField(verbose_name='Описание')

    photo = models.ImageField(upload_to='arenas/', blank=True, verbose_name='Фото')
    logo = models.ImageField(upload_to='arenas/', blank=True, verbose_name='Логотип')

    def __str__(self):
        return f'{self.address} - {self.city}'

    class Meta:
        verbose_name = 'Манеж'
        verbose_name_plural = 'Манежи'
