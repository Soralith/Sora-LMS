from django.contrib import admin
from .models import AISettings


@admin.register(AISettings)
class AISettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    fieldsets = (
        ('Umum', {
            'fields': ('name', 'is_active')
        }),
        ('Konfigurasi', {
            'fields': ('gemini_api_key', 'system_instruction'),
            'classes': ('wide',)
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        return fieldsets