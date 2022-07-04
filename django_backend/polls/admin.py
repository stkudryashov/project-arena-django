from django.contrib import admin
from polls.models import UserPoll, Poll, PollVariant


class PollVariantInLine(admin.TabularInline):
    model = PollVariant
    extra = 0
    verbose_name_plural = 'Ответы'


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'datetime', 'city', 'is_open', 'is_start')
    inlines = [PollVariantInLine]

    TYPE_MESSAGE_HELP = ' '.join(['<p>Если требует развернутого ответа, то игнорирует<br/>',
                                  'прикрепленные варианты, отправляя кнопку "Ответить".<br/><br/>',
                                  'Если активен вывод при регистрации, то игнорирует<br/>',
                                  'все остальное, отправляя в порядке "Дата отправки".</p>'])

    fieldsets = (
        ('Настройка', {
            'fields': ('title', 'datetime')
        }),
        ('Город', {
            'fields': ('city',),
            'description': 'Если город не выбран, отправляет всем пользователям'
        }),
        ('Сообщение', {
            'fields': ('description', 'photo')
        }),
        ('Тип сообщения', {
            'fields': ('is_open', 'is_start'),
            'description': TYPE_MESSAGE_HELP
        })
    )


@admin.register(PollVariant)
class PollVariantAdmin(admin.ModelAdmin):
    list_display = ('poll', 'text')


@admin.register(UserPoll)
class UserPollAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll', 'answer')
