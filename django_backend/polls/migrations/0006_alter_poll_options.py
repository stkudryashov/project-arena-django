# Generated by Django 4.0.4 on 2022-07-07 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_alter_poll_city'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='poll',
            options={'ordering': ('-is_start', '-datetime'), 'verbose_name': 'Сообщение', 'verbose_name_plural': 'Сообщения'},
        ),
    ]
