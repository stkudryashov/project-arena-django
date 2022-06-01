from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', admin.site.urls),
]

admin.site.site_header = 'Sport 70'
admin.site.site_title = 'Sport 70'
