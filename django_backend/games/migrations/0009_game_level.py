# Generated by Django 4.0.4 on 2022-07-22 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0008_alter_game_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='level',
            field=models.CharField(choices=[('Новичок', 'Новичок'), ('Средний', 'Средний'), ('Средний', 'Средний')], default='test', max_length=32, verbose_name='Уровень игры'),
            preserve_default=False,
        ),
    ]
