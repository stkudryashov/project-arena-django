from django.contrib import admin

from characteristics.models import Characteristic, UserCharacteristic


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    pass


@admin.register(UserCharacteristic)
class UserCharacteristicAdmin(admin.ModelAdmin):
    pass
