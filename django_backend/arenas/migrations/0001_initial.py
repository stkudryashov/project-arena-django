# Generated by Django 4.0.4 on 2022-06-01 20:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='Город')),
                ('timezone', models.CharField(blank=True, max_length=32, null=True, verbose_name='Часовой пояс')),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
            },
        ),
        migrations.CreateModel(
            name='Arena',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=128, verbose_name='Адрес')),
                ('phone_number', models.CharField(max_length=32, verbose_name='Номер телефона')),
                ('description', models.TextField(verbose_name='Описание')),
                ('photo', models.ImageField(blank=True, upload_to='arenas/', verbose_name='Фото')),
                ('logo', models.ImageField(blank=True, upload_to='arenas/', verbose_name='Логотип')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='arenas.city', verbose_name='Город')),
            ],
            options={
                'verbose_name': 'Манеж',
                'verbose_name_plural': 'Манежи',
            },
        ),
    ]
