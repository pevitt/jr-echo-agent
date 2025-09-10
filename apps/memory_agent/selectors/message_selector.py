from typing import List, Optional
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from apps.memory_agent.models import Message, Source


class MessageSelector:
    """Selector para operaciones de acceso a datos de mensajes"""
    
    @staticmethod
    def create_message(content: str, source: Source, recipient: str, 
                      is_command: bool = False, command_type: Optional[str] = None,
                      is_file: bool = False, file_type: Optional[str] = None,
                      file_name: Optional[str] = None, file_url: Optional[str] = None,
                      google_drive_id: Optional[str] = None, google_drive_link: Optional[str] = None) -> Message:
        """Crea un nuevo mensaje en la base de datos"""
        return Message.objects.create(  # type: ignore
            content=content,
            source=source,
            recipient=recipient,
            is_command=is_command,
            command_type=command_type,
            is_file=is_file,
            file_type=file_type,
            file_name=file_name,
            file_url=file_url,
            google_drive_id=google_drive_id,
            google_drive_link=google_drive_link
        )
    
    @staticmethod
    def get_messages_by_recipient(recipient: str, period: str = 'all') -> List[Message]:
        """Obtiene mensajes de un destinatario por período"""
        now = timezone.now()
        
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return Message.objects.filter(  # type: ignore
                recipient=recipient,
                created_at__gte=start_date,
                is_command=False
            ).order_by('-created_at')
        
        elif period == 'week':
            start_date = now - timedelta(days=7)
            return Message.objects.filter(  # type: ignore
                recipient=recipient,
                created_at__gte=start_date,
                is_command=False
            ).order_by('-created_at')
        
        else:  # all
            return Message.objects.filter(  # type: ignore
                recipient=recipient,
                is_command=False
            ).order_by('-created_at')
    
    @staticmethod
    def search_messages(recipient: str, search_term: str) -> List[Message]:
        """Busca mensajes que contengan el término de búsqueda"""
        return Message.objects.filter(  # type: ignore
            recipient=recipient,
            content__icontains=search_term,
            is_command=False
        ).order_by('-created_at')[:10]
    
    @staticmethod
    def get_source_by_name(name: str) -> Optional[Source]:
        """Obtiene una fuente por nombre"""
        try:
            return Source.objects.get(name=name, is_active=True)  # type: ignore
        except Source.DoesNotExist:  # type: ignore
            return None
