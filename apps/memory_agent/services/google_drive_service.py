import os
import io
from datetime import datetime
from typing import Optional, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Scopes necesarios para Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveService:
    """Servicio para manejar archivos en Google Drive"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Inicializa el servicio de Google Drive
        
        Args:
            credentials_path: Ruta al archivo de credenciales JSON
        """
        self.credentials_path = credentials_path or getattr(settings, 'GOOGLE_DRIVE_CREDENTIALS_PATH', None)
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica con Google Drive API"""
        try:
            creds = None
            
            # Verificar si existe token guardado
            token_path = getattr(settings, 'GOOGLE_DRIVE_TOKEN_PATH', 'token.json')
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # Si no hay credenciales válidas, solicitar autorización
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_path:
                        logger.error("No se encontró archivo de credenciales de Google Drive")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    
                    # Para Docker/entornos sin navegador, usar URL manual
                    try:
                        creds = flow.run_local_server(port=0)
                    except Exception as e:
                        logger.warning(f"No se pudo usar servidor local: {str(e)}")
                        logger.info("Generando URL de autorización...")
                        
                        # Generar URL de autorización
                        auth_url, _ = flow.authorization_url(prompt='consent')
                        logger.info(f"Por favor, visita esta URL para autorizar la aplicación:")
                        logger.info(f"{auth_url}")
                        logger.info("Después de autorizar, copia el código de autorización.")
                        
                        # Solicitar código de autorización
                        auth_code = input("Ingresa el código de autorización: ")
                        flow.fetch_token(code=auth_code)
                        creds = flow.credentials
                
                # Guardar credenciales para próximas ejecuciones
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Autenticación con Google Drive exitosa")
            
        except Exception as e:
            logger.error(f"Error en autenticación con Google Drive: {str(e)}")
            self.service = None
    
    def create_folder_structure(self, date: datetime) -> str:
        """
        Crea la estructura de carpetas basada en la fecha
        
        Args:
            date: Fecha del archivo
            
        Returns:
            str: ID de la carpeta del día
        """
        if not self.service:
            raise Exception("Servicio de Google Drive no inicializado")
        
        try:
            # Crear carpeta del mes si no existe
            month_name = date.strftime('%B')  # Junio, Julio, etc.
            month_folder_id = self._get_or_create_folder(month_name, 'root')
            
            # Crear carpeta del día si no existe
            day_name = date.strftime('%d')  # 25, 26, etc.
            day_folder_id = self._get_or_create_folder(day_name, month_folder_id)
            
            return day_folder_id
            
        except Exception as e:
            logger.error(f"Error creando estructura de carpetas: {str(e)}")
            raise
    
    def _get_or_create_folder(self, folder_name: str, parent_id: str = 'root') -> str:
        """
        Obtiene o crea una carpeta
        
        Args:
            folder_name: Nombre de la carpeta
            parent_id: ID de la carpeta padre
            
        Returns:
            str: ID de la carpeta
        """
        try:
            # Buscar carpeta existente
            query = f"name='{folder_name}' and parents in '{parent_id}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(q=query).execute()
            items = results.get('files', [])
            
            if items:
                return items[0]['id']
            
            # Crear nueva carpeta
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            logger.info(f"Carpeta '{folder_name}' creada con ID: {folder.get('id')}")
            return folder.get('id')
            
        except Exception as e:
            logger.error(f"Error obteniendo/creando carpeta '{folder_name}': {str(e)}")
            raise
    
    def upload_file(self, file_content: bytes, filename: str, date: datetime, 
                   mime_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Sube un archivo a Google Drive
        
        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre del archivo
            date: Fecha del archivo
            mime_type: Tipo MIME del archivo
            
        Returns:
            Dict con información del archivo subido
        """
        if not self.service:
            raise Exception("Servicio de Google Drive no inicializado")
        
        try:
            # Crear estructura de carpetas
            folder_id = self.create_folder_structure(date)
            
            # Preparar metadatos del archivo
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Crear objeto de media
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mime_type or 'application/octet-stream',
                resumable=True
            )
            
            # Subir archivo
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,size'
            ).execute()
            
            logger.info(f"Archivo '{filename}' subido exitosamente. ID: {file.get('id')}")
            
            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'web_view_link': file.get('webViewLink'),
                'size': file.get('size'),
                'folder_id': folder_id
            }
            
        except Exception as e:
            logger.error(f"Error subiendo archivo '{filename}': {str(e)}")
            raise
    
    def download_file_from_url(self, file_url: str, filename: str, date: datetime, 
                              auth_username: Optional[str] = None, auth_password: Optional[str] = None) -> Dict[str, Any]:
        """
        Descarga un archivo desde una URL y lo sube a Google Drive
        
        Args:
            file_url: URL del archivo
            filename: Nombre del archivo
            date: Fecha del archivo
            auth_username: Usuario para autenticación HTTP (opcional)
            auth_password: Contraseña para autenticación HTTP (opcional)
            
        Returns:
            Dict con información del archivo subido
        """
        import requests
        
        try:
            # Preparar headers y autenticación
            headers = {}
            auth = None
            
            if auth_username and auth_password:
                auth = (auth_username, auth_password)
            
            # Descargar archivo
            response = requests.get(file_url, stream=True, auth=auth, headers=headers)
            response.raise_for_status()
            
            # Obtener tipo MIME
            content_type = response.headers.get('content-type', 'application/octet-stream')
            
            # Leer contenido
            file_content = response.content
            
            # Subir a Google Drive
            return self.upload_file(file_content, filename, date, content_type)
            
        except Exception as e:
            logger.error(f"Error descargando archivo desde URL: {str(e)}")
            raise
    
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        Obtiene información de un archivo
        
        Args:
            file_id: ID del archivo en Google Drive
            
        Returns:
            Dict con información del archivo
        """
        if not self.service:
            raise Exception("Servicio de Google Drive no inicializado")
        
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id,name,size,createdTime,modifiedTime,webViewLink,mimeType'
            ).execute()
            
            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'size': file.get('size'),
                'created_time': file.get('createdTime'),
                'modified_time': file.get('modifiedTime'),
                'web_view_link': file.get('webViewLink'),
                'mime_type': file.get('mimeType')
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo información del archivo: {str(e)}")
            raise
