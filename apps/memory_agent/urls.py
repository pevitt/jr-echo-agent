from django.urls import path
from apps.memory_agent.views import AgentWebhookView, HealthCheckView

app_name = 'memory_agent'

urlpatterns = [
    # Webhook para recibir mensajes de diferentes fuentes
    # El source viene en el path: /api/v1/webhook/{source_name}/
    path('webhook/<str:source_name>/', AgentWebhookView.as_view(), name='webhook_receiver'),
    
    # Endpoint de salud
    path('health/', HealthCheckView.as_view(), name='health_check'),
]
