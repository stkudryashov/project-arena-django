from django.contrib import admin

from playtime.models import DayOfTheWeek, UserTime


@admin.register(DayOfTheWeek)
class DayOfTheWeekAdmin(admin.ModelAdmin):
    pass


@admin.register(UserTime)
class UserTimeAdmin(admin.ModelAdmin):
    pass
