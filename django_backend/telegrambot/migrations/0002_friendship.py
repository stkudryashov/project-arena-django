# Generated by Django 4.0.4 on 2022-06-10 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('telegrambot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='telegrambot.telegramuser', verbose_name='Друг')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friends', to='telegrambot.telegramuser', verbose_name='Пригласил')),
            ],
            options={
                'verbose_name': 'Друг пользователя',
                'verbose_name_plural': 'Друзья пользователей',
            },
        ),
    ]