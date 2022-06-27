from django.db import models

from characteristics.models import Characteristic


class Rule(models.Model):
    """Правило для уведомлений"""

    name = models.CharField(max_length=32, verbose_name='Название')
    time = models.TimeField(verbose_name='Таймер')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Правило'
        verbose_name_plural = 'Правила'


class RuleCharacteristic(models.Model):
    """Описание правила для уведомлений"""

    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, blank=True,
                             related_name='rules', verbose_name='Правило')

    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE, blank=True,
                                       related_name='characteristics', verbose_name='Характеристика')

    LOGIC_QUERY = (
        ('lt', 'Меньше значения'),
        ('gt', 'Больше значения'),
        ('equals', 'Равно значению'),
    )

    query = models.CharField(choices=LOGIC_QUERY, max_length=32, verbose_name='Выражение')

    value = models.CharField(max_length=32, verbose_name='Значение')

    def __str__(self):
        return f'{self.rule} - {self.characteristic}'

    class Meta:
        verbose_name = 'Описание правила'
        verbose_name_plural = 'Описания правил'

        constraints = [
            models.UniqueConstraint(fields=['rule', 'characteristic'], name='unique_rule_characteristic'),
        ]
