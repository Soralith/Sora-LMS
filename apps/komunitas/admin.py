from django.contrib import admin
from .models import KomunitasMessage


@admin.register(KomunitasMessage)
class KomunitasMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'content', 'created_at']
    list_filter = ['created_at', 'course']
    search_fields = ['user__username', 'content']