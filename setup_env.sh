#!/bin/bash
# Script para configurar el entorno de desarrollo

# Configurar PYTHONPATH
export PYTHONPATH="/Users/rigobertoperez/Documents/fullstack/backend/jr-echo-agent:/Users/rigobertoperez/Documents/fullstack/backend/jr-echo-agent/apps:/Users/rigobertoperez/Documents/fullstack/backend/jr-echo-agent/utils:$PYTHONPATH"

# Activar entorno virtual
source ~/.pyenv/versions/echoagent/bin/activate

# Configurar Django
export DJANGO_SETTINGS_MODULE=core.settings

echo "Entorno configurado correctamente"
echo "PYTHONPATH: $PYTHONPATH"
echo "Django Settings: $DJANGO_SETTINGS_MODULE"
