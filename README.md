# 🧠 Agente de Memoria Digital

Un sistema inteligente que almacena ideas desde múltiples fuentes de mensajería (WhatsApp, Telegram) y genera resúmenes estructurados.

## 🚀 Características

- **Multi-fuente**: Soporte para WhatsApp y Telegram
- **Strategy Pattern**: Arquitectura extensible para nuevas fuentes
- **Resúmenes inteligentes**: Organización automática por temas
- **Comandos especiales**: `/resumen`, `/hoy`, `/semana`, `/buscar`
- **API REST**: Endpoints para integración
- **Docker**: Contenedorización completa

## 🏗️ Arquitectura

### Principios SOLID
- **Single Responsibility**: Cada clase tiene una responsabilidad específica
- **Open/Closed**: Fácil agregar nuevas fuentes sin modificar código existente
- **Liskov Substitution**: Las estrategias son intercambiables
- **Interface Segregation**: Interfaces específicas para cada responsabilidad
- **Dependency Inversion**: Dependencias inyectadas, no hardcodeadas

### Capas de la Arquitectura
```
┌─────────────────┐
│   APIView       │ ← Presentación (Views)
├─────────────────┤
│   Services      │ ← Lógica de Negocio
├─────────────────┤
│   Strategies    │ ← Strategy Pattern
├─────────────────┤
│   Selectors     │ ← Acceso a Datos
├─────────────────┤
│   Models        │ ← Entidades
└─────────────────┘
```

### Componentes
- **Models**: `Source`, `Message` (entidades de dominio)
- **Selectors**: `MessageSelector` (acceso a datos, Repository Pattern)
- **Services**: `MessageService`, `SummaryService` (lógica de negocio)
- **Strategies**: `WhatsAppStrategy`, `TelegramStrategy` (Strategy Pattern)
- **Views**: `AgentWebhookView`, `HealthCheckView` (APIView limpia)

### Flujo de Datos
```
1. Webhook → APIView (AgentWebhookView)
2. APIView → MessageService (lógica de negocio)
3. MessageService → MessageStrategy (procesamiento específico)
4. MessageService → MessageSelector (persistencia)
5. MessageService → SummaryService (si es comando)
6. MessageService → MessageStrategy (respuesta al usuario)
```

### Patrones de Diseño
- **Strategy Pattern**: Para manejar diferentes fuentes de mensajería
- **Repository Pattern**: Para abstraer el acceso a datos
- **Service Layer**: Para encapsular la lógica de negocio
- **Factory Pattern**: Para crear estrategias dinámicamente

## 📡 Endpoints

### Webhook
```
POST /api/v1/webhook/{source_name}/
```
Recibe mensajes desde diferentes fuentes. El `source_name` viene en el path de la URL.

**Headers:**
```
X-API-Key: tu_api_key_aqui
Content-Type: application/json
```

**URL Examples:**
- `POST /api/v1/webhook/WhatsApp/`
- `POST /api/v1/webhook/Telegram/`

**Payload:**
```json
{
  "data": {
    "Body": "Mi idea genial",
    "From": "+1234567890"
  }
}
```

### Health Check
```
GET /api/v1/health/
```

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd jr-echo-agent
```

### 2. Configurar variables de entorno
```bash
# Crear archivo .env
POSTGRES_DB=personal_finance
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=jr_echo_agent_db
```

### 3. Levantar con Docker
```bash
# Construir y levantar
make up-build

# O con Docker Compose
docker compose up --build
```

### 4. Configurar fuentes de mensajería
```bash
# Crear fuentes iniciales
docker compose run web python manage.py setup_sources

# Crear API Key para autenticación
docker compose run web python manage.py create_api_key --name="Memory Agent API"
```

## 📱 Uso

### Comandos disponibles
- `/resumen` - Resumen general de todas las ideas
- `/hoy` - Ideas del día actual
- `/semana` - Ideas de la última semana
- `/buscar [término]` - Buscar ideas por término

### Ejemplo de uso
1. Envía un mensaje a tu bot: "Tengo una idea para una app móvil"
2. El sistema responde: "Idea registrada."
3. Usa `/resumen` para ver todas tus ideas organizadas

## 🔧 Desarrollo

### Estructura del proyecto
```
jr-echo-agent/
├── apps/
│   ├── utils/                    # BaseModel con UUID
│   └── memory_agent/             # App principal
│       ├── selectors/            # Acceso a datos (Repository Pattern)
│       │   └── message_selector.py
│       ├── services/             # Lógica de negocio
│       │   ├── message_service.py
│       │   └── summary_service.py
│       ├── strategies/           # Strategy Pattern
│       │   └── message_strategies.py
│       ├── views/                # APIView limpia
│       │   └── agent_views.py
│       ├── models.py             # Entidades de dominio
│       └── management/           # Comandos Django
├── core/                        # Configuración Django
├── docker-compose.yml           # Servicios Docker
├── Dockerfile                  # Imagen de la aplicación
└── Makefile                   # Comandos de desarrollo
```

### Comandos útiles
```bash
# Desarrollo
make up              # Levantar servicios
make migrate         # Aplicar migraciones
make shell           # Shell de Django
make create-superuser # Crear superusuario

# Docker
make build           # Construir imagen
make up-d            # Levantar en segundo plano
make stop            # Parar servicios
```

## 🔐 Configuración de Fuentes

### WhatsApp (Twilio)
1. Crear cuenta en Twilio
2. Obtener Account SID y Auth Token
3. Configurar webhook en Twilio
4. Actualizar `Source` en el admin

### Telegram
1. Crear bot con @BotFather
2. Obtener token del bot
3. Configurar webhook
4. Actualizar `Source` en el admin

## 🚀 Agregar Nueva Fuente de Mensajería

Para agregar una nueva fuente (ej: Discord, Slack), sigue estos pasos:

### 1. Crear nueva estrategia
```python
# apps/memory_agent/strategies/message_strategies.py
class DiscordStrategy(MessageStrategy):
    def process_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementar procesamiento específico de Discord
        pass
    
    def send_response(self, recipient: str, message: str) -> bool:
        # Implementar envío específico de Discord
        pass
```

### 2. Actualizar factory
```python
# En MessageStrategyFactory.get_strategy()
elif source_name == 'discord':
    return DiscordStrategy(source)
```

### 3. Crear fuente en admin
- Ir a `/admin/`
- Crear nueva `Source` con nombre "Discord"
- Configurar API key y URL

¡Listo! La nueva fuente funcionará automáticamente.

## 📊 Admin Panel

Accede a `/admin/` para:
- Gestionar fuentes de mensajería
- Ver todos los mensajes almacenados
- Configurar parámetros del sistema

## 🧪 Testing

### Ejecutar tests
```bash
# Tests unitarios
make test

# Tests con cobertura
make test ARGS=--cov=apps.memory_agent
```

### Estructura de tests
```
apps/memory_agent/tests/
├── test_selectors/
├── test_services/
├── test_strategies/
└── test_views/
```

## 🔧 Mantenimiento

### Logs
```bash
# Ver logs de la aplicación
make logs

# Ver logs de base de datos
docker compose logs db
```

### Backup de datos
```bash
# Exportar datos
make dump-data output=backup.json model=memory_agent

# Importar datos
make load-fixtures ARGS=backup.json
```

### Monitoreo
- **Health Check**: `GET /api/v1/health/`
- **Admin Panel**: `GET /admin/`
- **Logs**: Docker logs

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Sigue los principios SOLID
4. Añade tests para nueva funcionalidad
5. Commit tus cambios
6. Push a la rama
7. Abre un Pull Request

### Guías de contribución
- Usa type hints en Python
- Documenta funciones públicas
- Sigue la arquitectura de capas
- Mantén cobertura de tests > 80%

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
