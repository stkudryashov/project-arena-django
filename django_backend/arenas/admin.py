from django.contrib import admin

from arenas.models import City, Arena, ArenaPhoto


class ArenaPhotoInline(admin.TabularInline):
    model = ArenaPhoto
    extra = 0
    verbose_name_plural = 'Фотографии'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(Arena)
class ArenaAdmin(admin.ModelAdmin):
    inlines = [ArenaPhotoInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'city')
        }),
        ('Описание', {
            'fields': ('address', 'description', 'phone_number')
        })
    )

    list_display = ('title', 'city', 'phone_number')
    list_filter = ('city',)

    search_fields = ('title', 'address', 'phone_number')
