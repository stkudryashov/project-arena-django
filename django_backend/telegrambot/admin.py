from django.contrib import admin

from characteristics.models import UserCharacteristic
from polls.models import UserPoll
from telegrambot.models import TelegramUser

from import_export.admin import ExportMixin
from import_export.fields import Field
from import_export import resources


class TelegramUserResource(resources.ModelResource):
    username = Field(attribute='username', column_name='Имя пользователя')
    telegram_username = Field(attribute='telegram_username', column_name='Telegram')
    phone_number = Field(attribute='phone_number', column_name='Номер телефона')
    date_of_birth = Field(attribute='date_of_birth', column_name='Дата рождения')
    city__title = Field(attribute='city__title', column_name='Город')
    is_banned = Field(attribute='is_banned', column_name='Статус блокировки')

    class Meta:
        model = TelegramUser
        exclude = ('telegram_id', 'telegram_img', 'city', 'id')


class TelegramUserCharacteristic(admin.TabularInline):
    model = UserCharacteristic
    extra = 0
    verbose_name_plural = 'Характеристики'


class TelegramUserPoll(admin.TabularInline):
    model = UserPoll
    extra = 0
    verbose_name_plural = 'Ответы на опросы'

    readonly_fields = ('user', 'poll', 'answer')
    can_delete = False


@admin.register(TelegramUser)
class TelegramUserAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = TelegramUserResource
    inlines = [TelegramUserCharacteristic, TelegramUserPoll]

    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'phone_number', 'date_of_birth', 'city')
        }),
        ('Telegram', {
            'fields': ('telegram_username', 'telegram_id', 'telegram_img')
        }),
        ('Блокировка', {
            'fields': ('is_banned',)
        })
    )

    list_display = ('username', 'telegram_username', 'phone_number', 'city', 'date_of_birth', 'is_banned')
    list_filter = ('city', 'is_banned')

    readonly_fields = ('telegram_id',)
    search_fields = ('username', 'telegram_username', 'phone_number')
