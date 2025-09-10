from typing import Dict, Any, Tuple
from datetime import datetime
from apps.memory_agent.models import Source
from apps.memory_agent.selectors.message_selector import MessageSelector
from apps.memory_agent.strategies.message_strategies import MessageStrategyFactory
from apps.memory_agent.services.google_drive_service import GoogleDriveService


class MessageService:
    """Servicio para manejar la lógica de negocio de mensajes"""
    
    def __init__(self):
        self.selector = MessageSelector()
        self.strategy_factory = MessageStrategyFactory()
    
    def process_message(self, source_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un mensaje entrante y determina si almacenar o devolver resumen
        """
        # Obtener fuente
        source = self.selector.get_source_by_name(source_name)
        if not source:
            raise ValueError(f"Source '{source_name}' not found or inactive")
        
        # Obtener estrategia para la fuente
        strategy = self.strategy_factory.get_strategy(source)
        
        # Procesar mensaje con la estrategia
        processed_data = strategy.process_message(data)
        
        # Determinar si es comando, archivo o mensaje normal
        if processed_data['is_command']:
            return self._handle_command(processed_data, source)
        elif processed_data.get('is_file', False):
            return self._handle_file_message(processed_data, source)
        else:
            return self._handle_regular_message(processed_data, source)
    
    def _handle_command(self, processed_data: Dict[str, Any], source: Source) -> Dict[str, Any]:
        """Maneja comandos especiales como /resumen, /hoy, etc."""
        command_type = processed_data['command_type']
        recipient = processed_data['recipient']
        
        # Obtener estrategia para enviar respuesta
        strategy = self.strategy_factory.get_strategy(source)
        
        if command_type == '/resumen':
            response = self._generate_summary(recipient, 'all')
        elif command_type == '/hoy':
            response = self._generate_summary(recipient, 'today')
        elif command_type == '/semana':
            response = self._generate_summary(recipient, 'week')
        elif command_type == '/buscar':
            search_term = processed_data['content'].replace('/buscar', '').strip()
            response = self._search_messages(recipient, search_term)
        else:
            response = "Comando no reconocido."
        
        # Enviar respuesta
        strategy.send_response(recipient, response)
        
        return {
            'status': 'command_processed',
            'response': response,
            'command_type': command_type
        }
    
    def _handle_regular_message(self, processed_data: Dict[str, Any], source: Source) -> Dict[str, Any]:
        """Maneja mensajes regulares (almacenar idea)"""
        # Crear mensaje en la base de datos
        message = self.selector.create_message(
            content=processed_data['content'],
            source=source,
            recipient=processed_data['recipient'],
            is_command=False
        )
        
        # Obtener estrategia para enviar respuesta
        strategy = self.strategy_factory.get_strategy(source)
        
        # Enviar confirmación
        response = "Idea registrada."
        strategy.send_response(processed_data['recipient'], response)
        
        return {
            'status': 'message_stored',
            'message_id': str(message.id),
            'response': response
        }
    
    def _handle_file_message(self, processed_data: Dict[str, Any], source: Source) -> Dict[str, Any]:
        """Maneja mensajes con archivos (subir a Google Drive)"""
        try:
            # Obtener información del archivo
            file_url = processed_data.get('file_url')
            file_name = processed_data.get('file_name')
            file_type = processed_data.get('file_type')
            
            if not file_url or not file_name:
                raise ValueError("Información de archivo incompleta")
            
            # Subir archivo a Google Drive
            drive_service = GoogleDriveService()
            
            # Obtener credenciales de Twilio para autenticación
            account_sid = source.additional1  # type: ignore
            auth_token = source.additional2  # type: ignore
            
            file_info = drive_service.download_file_from_url(
                file_url=file_url,
                filename=file_name,
                date=datetime.now(),
                auth_username=account_sid,
                auth_password=auth_token
            )
            
            # Crear mensaje en la base de datos con información del archivo
            message = self.selector.create_message(
                content=processed_data['content'],
                source=source,
                recipient=processed_data['recipient'],
                is_command=False,
                is_file=True,
                file_type=file_type,
                file_name=file_name,
                file_url=file_url,
                google_drive_id=file_info['id'],
                google_drive_link=file_info['web_view_link']
            )
            
            # Obtener estrategia para enviar respuesta
            strategy = self.strategy_factory.get_strategy(source)
            
            # Enviar confirmación
            response = f"Archivo cargado exitosamente: {file_name}"
            strategy.send_response(processed_data['recipient'], response)
            
            return {
                'status': 'file_uploaded',
                'message_id': str(message.id),
                'file_info': file_info,
                'response': response
            }
            
        except Exception as e:
            # En caso de error, enviar mensaje de error
            strategy = self.strategy_factory.get_strategy(source)
            error_response = f"Error al cargar archivo: {str(e)}"
            strategy.send_response(processed_data['recipient'], error_response)
            
            return {
                'status': 'file_upload_error',
                'error': str(e),
                'response': error_response
            }
    
    def _generate_summary(self, recipient: str, period: str) -> str:
        """Genera un resumen estructurado"""
        from apps.memory_agent.services.summary_service import SummaryService
        
        summary_service = SummaryService()
        return summary_service.generate_summary(recipient, period)
    
    def _search_messages(self, recipient: str, search_term: str) -> str:
        """Busca mensajes por término"""
        from apps.memory_agent.services.summary_service import SummaryService
        
        summary_service = SummaryService()
        return summary_service.search_messages(recipient, search_term)
