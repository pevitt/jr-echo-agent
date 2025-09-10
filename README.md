# 🧠 Agente de Memoria Digital

Un sistema inteligente que almacena ideas desde múltiples fuentes de mensajería (WhatsApp, Telegram) y genera resúmenes estructurados.

## 🚀 Características

- **Multi-fuente**: Soporte para WhatsApp y Telegram
- **Strategy Pattern**: Arquitectura extensible para nuevas fuentes
- **Resúmenes inteligentes**: Organización automática por temas
- **Comandos especiales**: `/resumen`, `/hoy`, `/semana`, `/buscar`
- **Gestión de archivos**: Subida automática a Google Drive organizados por fecha
- **Respuestas automáticas**: Confirmación de mensajes y archivos cargados
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
- **Services**: `MessageService`, `SummaryService`, `GoogleDriveService`, `TwilioService` (lógica de negocio)
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

### Gestión de archivos
1. Envía una foto, video o documento por WhatsApp
2. El sistema detecta automáticamente el archivo
3. Lo sube a Google Drive organizado por fecha (mes/día)
4. Responde: "Archivo cargado exitosamente: nombre_archivo.jpg"
5. El archivo queda disponible en Google Drive con enlace directo

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

## 📁 Configuración de Google Drive

### 1. Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Haz clic en **"Seleccionar proyecto"** → **"Nuevo proyecto"**
3. Nombre: `Memory Agent Drive` (o el que prefieras)
4. Haz clic en **"Crear"**

### 2. Habilitar Google Drive API

1. En el menú lateral, ve a **"APIs y servicios"** → **"Biblioteca"**
2. Busca **"Google Drive API"**
3. Haz clic en **"Google Drive API"**
4. Haz clic en **"Habilitar"**

### 3. Crear Credenciales OAuth 2.0

1. Ve a **"APIs y servicios"** → **"Credenciales"**
2. Haz clic en **"+ CREAR CREDENCIALES"** → **"ID de cliente OAuth 2.0"**
3. Tipo de aplicación: **"Aplicación de escritorio"**
4. Nombre: `Memory Agent`
5. Haz clic en **"Crear"**

### 4. Configurar Pantalla de Consentimiento

1. Ve a **"APIs y servicios"** → **"Pantalla de consentimiento OAuth"**
2. Tipo de usuario: **"Externo"**
3. Completa la información básica:
   - **Nombre de la aplicación**: `Memory Agent`
   - **Correo electrónico de soporte**: Tu email
   - **Dominio autorizado**: `localhost`
4. En **"Scopes"**, agrega: `https://www.googleapis.com/auth/drive.file`
5. En **"Usuarios de prueba"**, agrega tu email
6. Haz clic en **"Guardar y continuar"**

### 5. Descargar Credenciales

1. Se abrirá una ventana con las credenciales
2. Haz clic en **"DESCARGAR JSON"**
3. Renombra el archivo a `credentials.json`
4. Colócalo en la raíz de tu proyecto

### 6. Configurar Variables de Entorno

Crea o actualiza tu archivo `.env`:

```bash
# Database Configuration
POSTGRES_DB=echo_agent_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=jr_echo_agent_db

# Django Configuration
DEBUG=True
SECRET_KEY=tu-secret-key-aqui

# Twilio Configuration
TWILIO_ACCOUNT_SID=AC1234567890abcdef
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Google Drive Configuration
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials.json
GOOGLE_DRIVE_TOKEN_PATH=token.json
```

### 7. Configurar Google Drive en Docker

#### **Opción A: Con servidor local (si tienes navegador)**
```bash
# Copiar credenciales al contenedor
docker cp credentials.json jr_echo_agent_web:/app/credentials.json

# Ejecutar autenticación
docker compose run web python manage.py setup_google_drive
```

#### **Opción B: Con URL manual (recomendada para Docker)**
```bash
# Ejecutar autenticación
docker compose run web python manage.py setup_google_drive
```

El comando te mostrará:
1. Una URL para autorizar la aplicación
2. Te pedirá que copies el código de autorización
3. Guardará el token automáticamente

#### **Proceso de Autorización Manual**

Cuando ejecutes el comando, verás algo como:
```
🔗 Por favor, visita esta URL para autorizar la aplicación:
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=...

Después de autorizar, copia el código de autorización.
Ingresa el código de autorización: [aquí pegas el código]
✅ Autorización exitosa!
Token guardado en: token.json
✅ Conexión con Google Drive exitosa!
🎉 Google Drive configurado exitosamente!
```

#### **Copiar Token al Host**
```bash
# Copiar token del contenedor al host
docker cp jr_echo_agent_web:/app/token.json ./token.json
```

### 8. Estructura de Archivos Final

```
jr-echo-agent/
├── credentials.json     ← De Google Cloud Console
├── token.json          ← Generado automáticamente
├── .env               ← Variables de entorno
├── .gitignore         ← Con token.json y credentials.json
├── manage.py
└── ...
```

### 9. Configurar .gitignore

Asegúrate de que tu `.gitignore` incluya:
```gitignore
# Credenciales y tokens
credentials.json
token.json
*.env
.envrc
```

### 10. Probar la Configuración

```bash
# Test con archivo simulado
curl -X POST http://localhost:8000/api/v1/webhook/WhatsApp/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-API-Key: tu_api_key_aqui" \
  -d "NumMedia=1&MediaContentType0=image/jpeg&MediaUrl0=https://example.com/image.jpg&From=whatsapp%3A%2B1234567890"
```

### 11. Verificar en Google Drive

1. Ve a [Google Drive](https://drive.google.com/)
2. Busca las carpetas creadas automáticamente:
   - `Junio/25/` (o el mes/día actual)
   - Los archivos subidos aparecerán ahí

## ⚠️ Solución de Problemas

### **Error: "could not locate runnable browser"**
- Usa la **Opción B** (URL manual) para Docker
- El comando manejará automáticamente la autenticación sin navegador

### **Error: "401 Client Error: Unauthorized"**
- Verifica que las credenciales de Twilio estén configuradas en el admin
- Asegúrate de que `additional1` tenga el Account SID y `additional2` tenga el Auth Token

### **Error: "Memory Agent has not completed the Google verification process"**
- Agrega tu email en **"Usuarios de prueba"** en Google Cloud Console
- Asegúrate de usar el mismo email para autorizar la aplicación

### **Error: "No se encontró archivo de credenciales"**
- Verifica que `credentials.json` esté en la raíz del proyecto
- Revisa la variable `GOOGLE_DRIVE_CREDENTIALS_PATH` en `.env`

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
