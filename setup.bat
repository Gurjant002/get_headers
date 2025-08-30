@echo off
REM Script de inicio rápido para FastAPI Template (Windows)
echo 🚀 Configurando FastAPI Template...

REM Crear directorio de logs
if not exist "logs" mkdir logs

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📚 Instalando dependencias...
pip install -r requirements.txt

REM Crear primera migración si no existe
if not exist "alembic\versions\*.py" (
    echo 🗄️  Creando migración inicial...
    alembic revision --autogenerate -m "Initial migration"
)

REM Aplicar migraciones
echo 🔄 Aplicando migraciones...
alembic upgrade head

echo ✅ Configuración completada!
echo.
echo 🎉 Para ejecutar la aplicación:
echo    uvicorn app.main:app --reload
echo.
echo 📖 Documentación disponible en:
echo    http://localhost:8000/docs

pause
