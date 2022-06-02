from django.contrib import admin

from knowledges.models import Knowledge


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    pass
