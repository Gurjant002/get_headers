# 🚀 Plantilla FastAPI con SQLModel

Plantilla moderna de FastAPI lista para usar con SQLModel, autenticación JWT, logging avanzado y todas las mejores prácticas.

## ⚡ Arranque Rápido

### Opción A: Setup Automático (Recomendado)

**🪟 Windows:**
```bash
# Ej├── tests/                # 🧪 Tests
├── logs/                 # 📄 Archivos de log
├── setup.sh             # 🛠️ Script setup (Linux/macOS)
├── setup.bat            # 🛠️ Script setup (Windows)
├── .env                  # 🔑 Variables de entornotar script de configuración automática
setup.bat
```

**🐧 macOS/Linux:**
```bash
# Dar permisos de ejecución y ejecutar
chmod +x setup.sh
./setup.sh
```

**¿Qué hace el script automático?**
- ✅ Crea el entorno virtual automáticamente
- ✅ Instala todas las dependencias
- ✅ Crea el directorio de logs
- ✅ Genera las migraciones iniciales de BD
- ✅ Aplica las migraciones
- ✅ Te deja todo listo para ejecutar

Después del setup automático, solo ejecuta:
```bash
uvicorn app.main:app --reload
```

### Opción B: Setup Manual

### 1. Copiar la plantilla
```bash
# Copia toda la carpeta a tu nuevo proyecto
cp -r plantilla/fastApi mi-nuevo-proyecto
cd mi-nuevo-proyecto
```

### 2. Configurar entorno
```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate
# Activar (macOS/Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env
```

**Editar `.env` con tus valores:**
```env
# OBLIGATORIO: Cambiar en producción
SECRET_KEY=tu-clave-super-secreta-aqui

# Base de datos (SQLite por defecto)
DATABASE_URL=sqlite:///./app.db

# Aplicación
APP_NAME=Mi Aplicación API
DEBUG=True

# CORS - Ajustar según tu frontend
ALLOWED_ORIGINS=http://localhost:3000
```

### 4. Ejecutar
```bash
# Crear migraciones iniciales
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Ejecutar aplicación
uvicorn app.main:app --reload
```

**🎉 ¡Listo!** Tu API está corriendo en: http://localhost:8000

- **Documentación**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 🤔 ¿Qué método de setup elegir?

| Situación | Método Recomendado | Razón |
|-----------|-------------------|-------|
| **Primer uso** | 🤖 Setup Automático | Configura todo en un solo comando |
| **Desarrollo nuevo** | 🤖 Setup Automático | Menos propenso a errores |
| **CI/CD** | 📝 Manual | Mejor control de cada paso |
| **Debugging setup** | 📝 Manual | Permite ver qué paso falla |
| **Personalización avanzada** | 📝 Manual | Más flexibilidad |

**💡 Tip**: Si eres nuevo con FastAPI, usa el setup automático. Si necesitas personalizar el proceso, usa el manual.

## � Parámetros a Personalizar

### 📝 Variables de Entorno (`.env`)

| Variable | Descripción | Ejemplo | Obligatorio |
|----------|-------------|---------|-------------|
| `SECRET_KEY` | Clave secreta JWT | `mi-clave-muy-segura-123` | ✅ |
| `APP_NAME` | Nombre de tu aplicación | `Mi API Increíble` | ❌ |
| `DEBUG` | Modo desarrollo | `True`/`False` | ❌ |
| `DATABASE_URL` | URL de base de datos | `sqlite:///./app.db` | ❌ |
| `ALLOWED_ORIGINS` | Dominios permitidos CORS | `http://localhost:3000` | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración JWT | `30` | ❌ |

### 🏗️ Archivos a Modificar

#### 1. **`app/config.py`** - Configuración general
```python
class Settings(BaseSettings):
    # Cambiar valores por defecto
    app_name: str = "MI APLICACIÓN"
    app_version: str = "1.0.0"
    # ... resto igual
```

#### 2. **`app/models/__init__.py`** - Agregar tus modelos
```python
# Ejemplo: Agregar modelo Producto
class Product(SQLModel, table=True):
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price: float
    description: Optional[str] = None
```

#### 3. **`app/api/`** - Crear tus endpoints
```python
# Crear nuevo archivo: app/api/products.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/products")
async def get_products():
    return {"products": []}
```

#### 4. **`app/api/__init__.py`** - Registrar nuevas rutas
```python
from app.api import auth, users, products  # ← Agregar

api_router.include_router(products.router, prefix="/products", tags=["products"])
```

## 🔐 Sistema de Autenticación

### Endpoints disponibles:
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión  
- `GET /api/v1/auth/me` - Usuario actual
- `GET /api/v1/users/` - Lista usuarios (admin)
- `PUT /api/v1/users/{id}` - Actualizar usuario

### Usar autenticación en tus endpoints:
```python
from app.dependencies import get_current_active_user
from app.models import UserRead

@router.get("/mi-endpoint-protegido")
async def mi_endpoint(current_user: UserRead = Depends(get_current_active_user)):
    return {"message": f"Hola {current_user.username}"}
```

## 📊 Sistema de Logging

### Logging automático incluido:
- ✅ Todas las requests/responses
- ✅ Errores con stack trace
- ✅ Eventos de autenticación
- ✅ Archivos rotativos en producción

### Agregar logs personalizados:
```python
from loguru import logger
from app.logging_config import log_business_event

# Log básico
logger.info("Mi evento personalizado")

# Log de evento de negocio
log_business_event("order_created", {"order_id": "123"}, user_id="user_456")
```

## �️ Base de Datos

### SQLite (desarrollo)
```env
DATABASE_URL=sqlite:///./app.db
```

### PostgreSQL (producción)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Migraciones
```bash
# Crear migración después de cambiar modelos
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Ver historial
alembic history
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=app

# Test específico
pytest tests/test_auth.py
```

## � Despliegue en Producción

### 1. Variables críticas:
```env
SECRET_KEY=clave-super-segura-generada-aleatoriamente
DEBUG=False
DATABASE_URL=postgresql://...
ALLOWED_ORIGINS=https://mi-dominio.com
```

### 2. Comando de producción:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📂 Estructura del Proyecto

```
mi-proyecto/
├── app/
│   ├── api/                 # 📁 Endpoints de la API
│   │   ├── auth.py         # 🔐 Autenticación
│   │   ├── users.py        # 👥 Gestión usuarios
│   │   └── __init__.py
│   ├── middleware/         # 🔧 Middleware personalizado
│   ├── models/             # 🗃️ Modelos SQLModel
│   ├── services/           # 💼 Lógica de negocio
│   ├── config.py          # ⚙️  Configuración
│   ├── database.py        # 🗄️  Conexión DB
│   ├── dependencies.py    # 🔗 Dependencias FastAPI
│   ├── logging_config.py  # 📝 Configuración logging
│   ├── main.py           # 🚀 Aplicación principal
│   └── security.py       # 🔒 Utilidades JWT
├── alembic/              # 📋 Migraciones
├── tests/                # � Tests
├── logs/                 # 📄 Archivos de log
├── .env                  # 🔑 Variables de entorno
└── requirements.txt      # 📦 Dependencias
```

## ✨ Características Incluidas

- ✅ **SQLModel** - ORM moderno y tipado
- ✅ **Autenticación JWT** completa
- ✅ **Logging avanzado** con Loguru
- ✅ **Validación** con Pydantic
- ✅ **Migraciones** con Alembic
- ✅ **CORS** configurado
- ✅ **Testing** setup completo
- ✅ **Documentación** automática
- ✅ **Manejo de errores** centralizado
- ✅ **Scripts de setup** automático (Windows y Unix)

## 🆘 Solución de Problemas

### Problemas con Scripts de Setup

#### Script no ejecuta (Linux/macOS)
```bash
# Dar permisos de ejecución
chmod +x setup.sh
```

#### Error: "Python no encontrado"
```bash
# Verificar instalación de Python
python --version
# o
python3 --version

# Si no está instalado, instalar Python 3.8+
```

#### Error en creación de entorno virtual
```bash
# Limpiar directorio y reintentar
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# Luego ejecutar setup nuevamente
```

#### Migraciones fallan
```bash
# Limpiar migraciones y recrear
rm alembic/versions/*.py  # Linux/macOS
del alembic\versions\*.py  # Windows

# Ejecutar setup nuevamente
```

### Problemas Generales

### Error: Import "sqlmodel" could not be resolved
```bash
pip install sqlmodel
```

### Error: ModuleNotFoundError
```bash
# Asegúrate de estar en el directorio correcto y con el venv activado
source venv/bin/activate  # o venv\Scripts\activate en Windows
```

### Error de base de datos
```bash
# Recrear migraciones
rm alembic/versions/*.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

**💡 Consejo**: Una vez que tengas tu proyecto funcionando, personaliza este README con información específica de tu aplicación.

**🤝 ¿Necesitas ayuda?** Esta plantilla está diseñada para ser simple pero completa. Modifica solo lo que necesites y mantén el resto igual.
