from django.db import models
from typing import Optional
from utils.models import BaseModel

class Source(BaseModel):
    """Representa la fuente de mensajería (WhatsApp, Telegram, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    additional1 = models.TextField(blank=True, null=True)
    additional2 = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # type: ignore

    class Meta:
        verbose_name = "Fuente de Mensajería"
        verbose_name_plural = "Fuentes de Mensajería"

    def __str__(self):
        return self.name

class Message(BaseModel):
    """Registra cada idea recibida desde las fuentes"""
    content = models.TextField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='messages')
    recipient = models.CharField(max_length=100)  # número/chat_id del usuario
    
    # Campos adicionales para análisis
    is_command = models.BooleanField(default=False)  # type: ignore  # Si es un comando especial
    command_type = models.CharField(max_length=50, blank=True, null=True)  # /resumen, /hoy, etc.
    
    # Campos para archivos
    is_file = models.BooleanField(default=False)  # type: ignore  # Si es un archivo
    file_type = models.CharField(max_length=50, blank=True, null=True)  # image, document, audio, etc.
    file_name = models.CharField(max_length=255, blank=True, null=True)  # Nombre del archivo
    file_url = models.URLField(blank=True, null=True)  # URL del archivo original
    google_drive_id = models.CharField(max_length=255, blank=True, null=True)  # ID en Google Drive
    google_drive_link = models.URLField(blank=True, null=True)  # Link de Google Drive
    
    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['-created_at']

    def __str__(self):
        content_preview = str(self.content)[:50] if self.content else ""
        return f"{self.source.name} - {content_preview}..."