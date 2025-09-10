from django.core.management.base import BaseCommand
from apps.memory_agent.models import Source


class Command(BaseCommand):
    help = 'Configura las fuentes de mensajería iniciales'

    def handle(self, *args, **options):
        """Crea las fuentes de mensajería por defecto"""
        
        sources_data = [
            {
                'name': 'WhatsApp',
                'api_key': 'your_twilio_account_sid_here',
                'url': 'https://api.twilio.com/2010-04-01/Accounts/',
                'additional1': 'twilio_account_sid',
                'additional2': 'twilio_auth_token',
                'is_active': True
            },
            {
                'name': 'Twilio',
                'api_key': 'your_twilio_account_sid_here',
                'url': 'https://api.twilio.com/2010-04-01/Accounts/',
                'additional1': 'twilio_account_sid',
                'additional2': 'twilio_auth_token',
                'is_active': True
            },
            {
                'name': 'Telegram',
                'api_key': 'your_telegram_bot_token_here',
                'url': 'https://api.telegram.org/bot',
                'additional1': 'webhook_url',
                'additional2': 'allowed_updates',
                'is_active': True
            }
        ]
        
        for source_data in sources_data:
            source, created = Source.objects.get_or_create(  # type: ignore
                name=source_data['name'],
                defaults=source_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Fuente "{source.name}" creada exitosamente')  # type: ignore
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Fuente "{source.name}" ya existe')  # type: ignore
                )
        
        self.stdout.write(
            self.style.SUCCESS('Configuración de fuentes completada')  # type: ignore
        )
