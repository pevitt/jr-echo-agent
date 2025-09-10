from abc import ABC, abstractmethod
from typing import Dict, Any
from apps.memory_agent.models import Source
from apps.memory_agent.services.twilio_service import TwilioService


class MessageStrategy(ABC):
    """Interfaz abstracta para estrategias de procesamiento de mensajes"""
    
    def __init__(self, source: Source):
        self.source = source
    
    @abstractmethod
    def process_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un mensaje entrante y retorna los datos extraídos"""
        pass
    
    @abstractmethod
    def send_response(self, recipient: str, message: str) -> bool:
        """Envía una respuesta al canal correspondiente"""
        pass


class WhatsAppStrategy(MessageStrategy):
    """Estrategia para procesar mensajes de WhatsApp"""
    
    def process_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa mensaje de WhatsApp"""
        # Extraer datos del webhook de WhatsApp
        message_body = data.get('Body', '')
        from_number = data.get('From', '')
        num_media = int(data.get('NumMedia', '0'))
        
        # Detectar si es un comando especial
        is_command, command_type = self._detect_command(message_body)
        
        # Detectar si es un archivo
        is_file = num_media > 0
        file_info = None
        
        if is_file:
            file_info = self._extract_file_info(data)
        
        result = {
            'content': message_body if not is_file else "Archivo cargado",
            'recipient': from_number,
            'is_command': is_command,
            'command_type': command_type,
            'is_file': is_file
        }
        
        # Agregar información del archivo si existe
        if file_info:
            result.update(file_info)
        
        return result
    
    def send_response(self, recipient: str, message: str) -> bool:
        """Envía respuesta vía WhatsApp usando Twilio"""
        try:
            # Obtener credenciales de Twilio desde la fuente
            account_sid = self.source.additional1  # type: ignore
            auth_token = self.source.additional2  # type: ignore
            
            if not account_sid or not auth_token:
                print(f"Error: Credenciales de Twilio no configuradas para {self.source.name}")
                return False
            
            # Crear servicio de Twilio
            twilio_service = TwilioService(account_sid, auth_token)  # type: ignore
            
            # Enviar mensaje
            success = twilio_service.send_whatsapp_message(recipient, message)
            
            if success:
                print(f"WhatsApp response sent to {recipient}: {message}")
            else:
                print(f"Failed to send WhatsApp response to {recipient}")
            
            return success
            
        except Exception as e:
            print(f"Error sending WhatsApp response: {str(e)}")
            return False
    
    def _extract_file_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae información de archivos del webhook de WhatsApp"""
        num_media = int(data.get('NumMedia', '0'))
        
        if num_media == 0:
            return {}
        
        # Obtener información del primer archivo (WhatsApp permite múltiples)
        media_content_type = data.get('MediaContentType0', '')
        media_url = data.get('MediaUrl0', '')
        
        # Determinar tipo de archivo
        file_type = self._get_file_type(media_content_type)
        
        # Generar nombre de archivo
        file_name = self._generate_filename(media_content_type, data.get('MessageSid', ''))
        
        return {
            'file_type': file_type,
            'file_name': file_name,
            'file_url': media_url,
            'file_content_type': media_content_type
        }
    
    def _get_file_type(self, content_type: str) -> str:
        """Determina el tipo de archivo basado en el content-type"""
        if content_type.startswith('image/'):
            return 'image'
        elif content_type.startswith('video/'):
            return 'video'
        elif content_type.startswith('audio/'):
            return 'audio'
        elif content_type.startswith('application/pdf'):
            return 'document'
        elif content_type.startswith('application/'):
            return 'document'
        elif content_type.startswith('text/'):
            return 'document'
        else:
            return 'file'
    
    def _generate_filename(self, content_type: str, message_sid: str) -> str:
        """Genera un nombre de archivo único"""
        import uuid
        from datetime import datetime
        
        # Obtener extensión del content-type
        extension_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'video/mp4': '.mp4',
            'audio/ogg': '.ogg',
            'audio/mpeg': '.mp3',
            'application/pdf': '.pdf',
            'text/plain': '.txt'
        }
        
        extension = extension_map.get(content_type, '.bin')
        
        # Generar nombre único con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        return f"whatsapp_{timestamp}_{unique_id}{extension}"
    
    def _detect_command(self, content: str) -> tuple[bool, str]:
        """Detecta si el mensaje es un comando especial"""
        commands = ['/resumen', '/hoy', '/semana', '/buscar']
        for cmd in commands:
            if content.startswith(cmd):
                return True, cmd
        return False, None  # type: ignore


class TelegramStrategy(MessageStrategy):
    """Estrategia para procesar mensajes de Telegram"""
    
    def process_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa mensaje de Telegram"""
        # Extraer datos del webhook de Telegram
        message_text = data.get('message', {}).get('text', '')
        chat_id = str(data.get('message', {}).get('chat', {}).get('id', ''))
        
        # Detectar si es un comando especial
        is_command, command_type = self._detect_command(message_text)
        
        return {
            'content': message_text,
            'recipient': chat_id,
            'is_command': is_command,
            'command_type': command_type
        }
    
    def send_response(self, recipient: str, message: str) -> bool:
        """Envía respuesta vía Telegram (implementar con Bot API)"""
        # TODO: Implementar envío real con Telegram Bot API
        print(f"Telegram response to {recipient}: {message}")
        return True
    
    def _detect_command(self, content: str) -> tuple[bool, str]:
        """Detecta si el mensaje es un comando especial"""
        commands = ['/resumen', '/hoy', '/semana', '/buscar']
        for cmd in commands:
            if content.startswith(cmd):
                return True, cmd
        return False, None  # type: ignore


class MessageStrategyFactory:
    """Factory para crear estrategias de mensajería"""
    
    def get_strategy(self, source: Source) -> MessageStrategy:
        """Crea la estrategia apropiada basada en la fuente"""
        source_name = source.name.lower()  # type: ignore
        
        if source_name == 'whatsapp':
            return WhatsAppStrategy(source)
        elif source_name == 'twilio':
            return WhatsAppStrategy(source)  # Twilio usa la misma estrategia que WhatsApp
        elif source_name == 'telegram':
            return TelegramStrategy(source)
        else:
            raise ValueError(f"No strategy available for source: {source.name}")
