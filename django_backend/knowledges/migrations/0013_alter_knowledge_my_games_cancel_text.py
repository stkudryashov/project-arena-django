# Generated by Django 4.0.4 on 2022-06-23 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledges', '0012_knowledge_my_games_cancel_btn_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knowledge',
            name='my_games_cancel_text',
            field=models.CharField(max_length=64, verbose_name='Текст отмены записи'),
        ),
    ]