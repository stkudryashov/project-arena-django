from django.contrib import admin

from arenas.models import City, Arena


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(Arena)
class ArenaAdmin(admin.ModelAdmin):
    pass
