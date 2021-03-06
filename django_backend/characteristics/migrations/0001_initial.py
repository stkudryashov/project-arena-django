# Generated by Django 4.0.4 on 2022-06-01 20:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('telegrambot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Characteristic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Характеристика',
                'verbose_name_plural': 'Характеристики',
            },
        ),
        migrations.CreateModel(
            name='UserCharacteristic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=128, verbose_name='Значение')),
                ('characteristic', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='characteristics.characteristic', verbose_name='Характеристика')),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='characteristics', to='telegrambot.telegramuser', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Характеристика пользователя',
                'verbose_name_plural': 'Характеристики пользователей',
            },
        ),
        migrations.AddConstraint(
            model_name='usercharacteristic',
            constraint=models.UniqueConstraint(fields=('user', 'characteristic'), name='unique_user_characteristic'),
        ),
    ]
