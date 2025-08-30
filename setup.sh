#!/bin/bash

# Script de inicio rápido para FastAPI Template
echo "🚀 Configurando FastAPI Template..."

# Crear directorio de logs
mkdir -p logs

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Crear primera migración si no existe
if [ ! "$(ls -A alembic/versions)" ]; then
    echo "🗄️  Creando migración inicial..."
    alembic revision --autogenerate -m "Initial migration"
fi

# Aplicar migraciones
echo "🔄 Aplicando migraciones..."
alembic upgrade head

echo "✅ Configuración completada!"
echo ""
echo "🎉 Para ejecutar la aplicación:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "📖 Documentación disponible en:"
echo "   http://localhost:8000/docs"
