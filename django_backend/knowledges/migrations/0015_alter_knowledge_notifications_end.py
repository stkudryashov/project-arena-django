# Generated by Django 4.0.4 on 2022-06-29 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledges', '0014_knowledge_notifications_delay_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knowledge',
            name='notifications_end',
            field=models.TimeField(verbose_name='Конец уведомлений'),
        ),
    ]
