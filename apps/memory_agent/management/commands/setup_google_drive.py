from django.core.management.base import BaseCommand
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json

# Scopes necesarios para Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class Command(BaseCommand):
    help = 'Configura la autenticación inicial con Google Drive'

    def handle(self, *args, **options):
        """Configura Google Drive para primera vez"""
        
        credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH', 'credentials.json')
        token_path = os.getenv('GOOGLE_DRIVE_TOKEN_PATH', 'token.json')
        
        if not os.path.exists(credentials_path):
            self.stdout.write(
                self.style.ERROR(f'No se encontró el archivo de credenciales: {credentials_path}')
            )
            self.stdout.write(
                self.style.WARNING('Por favor, coloca el archivo credentials.json en la raíz del proyecto')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('Iniciando configuración de Google Drive...')
        )
        
        try:
            creds = None
            
            # Verificar si existe token guardado
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
                self.stdout.write('Token existente encontrado.')
            
            # Si no hay credenciales válidas, solicitar autorización
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    self.stdout.write('Refrescando token expirado...')
                    creds.refresh(Request())
                else:
                    self.stdout.write('Iniciando proceso de autorización...')
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, SCOPES)
                    
                    # Intentar servidor local primero
                    try:
                        self.stdout.write('Intentando autorización con servidor local...')
                        creds = flow.run_local_server(port=0)
                        self.stdout.write('✅ Autorización exitosa con servidor local!')
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'No se pudo usar servidor local: {str(e)}')
                        )
                        self.stdout.write('Generando URL de autorización manual...')
                        
                        # Generar URL de autorización
                        auth_url, _ = flow.authorization_url(prompt='consent')
                        self.stdout.write('')
                        self.stdout.write(
                            self.style.SUCCESS('🔗 Por favor, visita esta URL para autorizar la aplicación:')
                        )
                        self.stdout.write(f'{auth_url}')
                        self.stdout.write('')
                        self.stdout.write('Después de autorizar, copia el código de autorización.')
                        
                        # Solicitar código de autorización
                        auth_code = input('Ingresa el código de autorización: ')
                        flow.fetch_token(code=auth_code)
                        creds = flow.credentials
                        self.stdout.write('✅ Autorización exitosa!')
                
                # Guardar credenciales para próximas ejecuciones
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                self.stdout.write(f'Token guardado en: {token_path}')
            
            # Probar la conexión
            self.stdout.write('Probando conexión con Google Drive...')
            service = build('drive', 'v3', credentials=creds)
            
            # Hacer una consulta simple para verificar
            results = service.files().list(pageSize=1).execute()
            self.stdout.write('✅ Conexión con Google Drive exitosa!')
            
            self.stdout.write(
                self.style.SUCCESS('🎉 Google Drive configurado exitosamente!')
            )
            self.stdout.write('El token de autorización se ha guardado en token.json')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('Asegúrate de que:')
            )
            self.stdout.write('1. El archivo credentials.json esté en la raíz del proyecto')
            self.stdout.write('2. Hayas configurado correctamente el proyecto en Google Cloud Console')
            self.stdout.write('3. Hayas agregado tu email en "Usuarios de prueba"')
            self.stdout.write('4. La aplicación tenga permisos para Google Drive API')
