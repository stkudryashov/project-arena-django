from django.contrib import admin

from notifications.models import Rule, RuleCharacteristic


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'time')


@admin.register(RuleCharacteristic)
class RuleCharacteristicAdmin(admin.ModelAdmin):
    list_display = ('rule', 'characteristic', 'query', 'value')

    fieldsets = (
        ('Правило - Характеристика', {
            'fields': ('rule', 'characteristic')
        }),
        ('Логическое выражение', {
            'fields': ('query', 'value')
        })
    )
