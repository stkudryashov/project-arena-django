# Generated by Django 4.0.4 on 2022-06-19 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledges', '0009_knowledge_search_already_enter_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='knowledge',
            name='edit_characteristic_request',
            field=models.CharField(default='-', max_length=64, verbose_name='Запрос значения характеристики'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='knowledge',
            name='edit_characteristic_success',
            field=models.CharField(default='-', max_length=64, verbose_name='Характеристика изменена'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='knowledge',
            name='edit_please_select_buttons',
            field=models.CharField(default='-', max_length=64, verbose_name='Выберите пункт из меню'),
            preserve_default=False,
        ),
    ]