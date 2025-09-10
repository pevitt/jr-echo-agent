from django.core.management.base import BaseCommand
from rest_framework_api_key.models import APIKey


class Command(BaseCommand):
    help = 'Crea una API Key para autenticación'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='Memory Agent API Key',
            help='Nombre para la API Key'
        )

    def handle(self, *args, **options):
        """Crea una nueva API Key"""
        
        name = options['name']
        
        # Crear API Key
        api_key, key = APIKey.objects.create_key(name=name)
        
        self.stdout.write(
            self.style.SUCCESS(f'API Key creada exitosamente:')  # type: ignore
        )
        self.stdout.write(f'Nombre: {name}')
        self.stdout.write(f'ID: {api_key.id}')
        self.stdout.write(f'Key: {key}')
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING('¡IMPORTANTE! Guarda esta key de forma segura. No se puede recuperar.')  # type: ignore
        )
        self.stdout.write('')
        self.stdout.write('Para usar la API Key, inclúyela en el header:')
        self.stdout.write('X-API-Key: ' + key)
