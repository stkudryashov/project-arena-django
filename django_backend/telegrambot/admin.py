from django.contrib import admin

from telegrambot.models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'telegram_username', 'phone_number')
