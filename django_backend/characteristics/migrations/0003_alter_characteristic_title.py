# Generated by Django 4.0.4 on 2022-06-19 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('characteristics', '0002_characteristic_show_in_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='characteristic',
            name='title',
            field=models.CharField(max_length=128, unique=True, verbose_name='Название'),
        ),
    ]