from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404

from apps.memory_agent.serializers import WebhookSerializer
from apps.memory_agent.services.message_service import MessageService
from apps.memory_agent.models import Source


class AgentWebhookView(APIView):
    """
    Vista para recibir webhooks de diferentes fuentes de mensajería
    Sigue principios SOLID: Single Responsibility, Open/Closed
    """
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message_service = MessageService()
    
    def post(self, request, source_name):
        """Procesa mensajes entrantes desde webhooks"""
        # Validar que la fuente exista y esté activa
        try:
            source = get_object_or_404(Source, name=source_name, is_active=True)
        except Exception:
            return Response({
                'status': 'error',
                'message': f"Source '{source_name}' not found or inactive"
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = WebhookSerializer(data=request.data)

        
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Delegar procesamiento al servicio
            result = self.message_service.process_message(
                source_name=source_name,
                data=serializer.validated_data['data']  # type: ignore
            )
            
            return Response({
                'status': 'success',
                'message': 'Message processed successfully',
                'result': result
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'Internal server error',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """
    Vista para verificar el estado del servicio
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Health check endpoint"""
        return Response({
            'status': 'healthy',
            'service': 'Memory Agent',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0'
        }, status=status.HTTP_200_OK)
