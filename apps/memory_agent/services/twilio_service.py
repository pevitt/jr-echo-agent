from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from django.conf import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TwilioService:
    """Servicio para manejar comunicación con Twilio"""
    
    def __init__(self, account_sid: str, auth_token: str):
        """
        Inicializa el cliente de Twilio
        
        Args:
            account_sid: Account SID de Twilio
            auth_token: Auth Token de Twilio
        """
        self.client = Client(account_sid, auth_token)
        self.account_sid = account_sid
    
    def send_whatsapp_message(self, to: str, message: str, from_number: Optional[str] = None) -> bool:
        """
        Envía un mensaje de WhatsApp
        
        Args:
            to: Número de destino (formato: whatsapp:+1234567890)
            message: Contenido del mensaje
            from_number: Número de origen (opcional, usa el sandbox por defecto)
            
        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            # Si no se especifica número de origen, usar el sandbox
            if not from_number:
                from_number = "whatsapp:+14155238886"  # Número del sandbox de Twilio
            
            # Asegurar formato correcto
            if not to.startswith("whatsapp:"):
                to = f"whatsapp:{to}"
            
            if not from_number.startswith("whatsapp:"):
                from_number = f"whatsapp:{from_number}"
            
            # Enviar mensaje
            message_obj = self.client.messages.create(
                body=message,
                from_=from_number,
                to=to
            )
            
            logger.info(f"Mensaje enviado exitosamente. SID: {message_obj.sid}")
            return True
            
        except TwilioException as e:
            logger.error(f"Error de Twilio al enviar mensaje: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al enviar mensaje: {str(e)}")
            return False
    
    def get_message_status(self, message_sid: str) -> dict:
        """
        Obtiene el estado de un mensaje
        
        Args:
            message_sid: SID del mensaje
            
        Returns:
            dict: Información del estado del mensaje
        """
        try:
            message = self.client.messages(message_sid).fetch()
            return {
                'sid': message.sid,
                'status': message.status,
                'direction': message.direction,
                'date_created': message.date_created,
                'date_sent': message.date_sent,
                'error_code': message.error_code,
                'error_message': message.error_message
            }
        except TwilioException as e:
            logger.error(f"Error al obtener estado del mensaje: {str(e)}")
            return {'error': str(e)}
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Valida si un número de teléfono es válido para WhatsApp
        
        Args:
            phone_number: Número de teléfono a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        try:
            # Remover prefijo whatsapp: si existe
            clean_number = phone_number.replace("whatsapp:", "")
            
            # Validar formato básico (debe empezar con +)
            if not clean_number.startswith("+"):
                return False
            
            # Validar longitud (entre 7 y 15 dígitos)
            digits = clean_number[1:]  # Remover el +
            if not digits.isdigit() or len(digits) < 7 or len(digits) > 15:
                return False
            
            return True
            
        except Exception:
            return False
