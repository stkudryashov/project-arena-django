# Generated by Django 4.0.4 on 2022-07-07 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledges', '0030_knowledge_notifications_confirm_reserve'),
    ]

    operations = [
        migrations.AddField(
            model_name='knowledge',
            name='is_banned_text',
            field=models.TextField(default='-', verbose_name='Текст "Вам заблокированы игры"'),
            preserve_default=False,
        ),
    ]
