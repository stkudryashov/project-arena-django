# Generated by Django 4.0.4 on 2022-06-19 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledges', '0006_knowledge_btn_continue_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knowledge',
            name='friends_404_text',
            field=models.TextField(verbose_name='Друг не найден'),
        ),
    ]