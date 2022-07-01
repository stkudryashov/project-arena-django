from django.contrib import admin
from polls.models import UserPoll, Poll, PollVariant


class PollVariantInLine(admin.TabularInline):
    model = PollVariant
    extra = 0
    verbose_name_plural = 'Ответы'


# Register your models here.
@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'datetime', 'description', 'photo', 'city')
    inlines = [PollVariantInLine]


@admin.register(PollVariant)
class TelegramUserGameAdmin(admin.ModelAdmin):
    list_display = ('poll', 'text', "is_open")


@admin.register(UserPoll)
class TelegramUserGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll', 'answer')
