from django.contrib import admin
from .models import UserAPIKey

@admin.register(UserAPIKey)
class UserAPIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'prefix', 'created', 'revoked']
    search_fields = ['user__username', 'name']
