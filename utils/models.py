import uuid
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    Modelo base que proporciona campos comunes para todos los modelos:
    - id: UUID como clave primaria
    - created_at: Fecha de creación automática
    - updated_at: Fecha de actualización automática
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} - {self.id}"
