from django.contrib import admin
from apps.memory_agent.models import Source, Message


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['content_short', 'source', 'recipient', 'is_command', 'command_type', 'created_at']
    list_filter = ['source', 'is_command', 'command_type', 'created_at']
    search_fields = ['content', 'recipient']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Contenido'