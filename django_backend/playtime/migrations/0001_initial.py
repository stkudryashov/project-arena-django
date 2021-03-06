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
            name='DayOfTheWeek',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='День недели')),
            ],
            options={
                'verbose_name': 'День недели',
                'verbose_name_plural': 'Дни недели',
            },
        ),
        migrations.CreateModel(
            name='UserTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField(verbose_name='Время')),
                ('day_of_the_week', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='playtime.dayoftheweek', verbose_name='День недели')),
                ('users', models.ManyToManyField(blank=True, related_name='times', to='telegrambot.telegramuser', verbose_name='Готовы играть в это время')),
            ],
            options={
                'verbose_name': 'Время',
                'verbose_name_plural': 'Время',
            },
        ),
    ]
