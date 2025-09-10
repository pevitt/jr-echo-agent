from django.apps import AppConfig


class MemoryAgentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "apps.memory_agent"
