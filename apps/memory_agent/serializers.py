from rest_framework import serializers
from apps.memory_agent.models import Source, Message


class SourceSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Source"""
    
    class Meta:
        model = Source
        fields = [
            'id', 'name', 'api_key', 'url', 
            'additional1', 'additional2', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Message"""
    source_name = serializers.CharField(source='source.name', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'content', 'source', 'source_name', 'recipient',
            'is_command', 'command_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear mensajes desde webhooks"""
    
    class Meta:
        model = Message
        fields = ['content', 'source', 'recipient', 'is_command', 'command_type']


class WebhookSerializer(serializers.Serializer):
    """Serializer para recibir webhooks de diferentes fuentes"""
    data = serializers.JSONField(required=False)  # type: ignore
    
    def to_internal_value(self, data):
        """Convierte form-data de Twilio al formato esperado"""
        # Si viene como form-data (Twilio), convertir a JSON
        if isinstance(data, dict) and 'data' not in data:
            # Es form-data de Twilio, envolver en 'data'
            return {'data': data}
        # Si ya viene como JSON con 'data', usar tal como está
        return super().to_internal_value(data)


class SummaryRequestSerializer(serializers.Serializer):
    """Serializer para solicitudes de resumen"""
    recipient = serializers.CharField(max_length=100)
    source_name = serializers.CharField(max_length=100)
    period = serializers.ChoiceField(
        choices=['today', 'week', 'month', 'all'],
        default='all'
    )
    search_term = serializers.CharField(required=False, allow_blank=True)
