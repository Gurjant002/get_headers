# 🚀 CONFIGURACIÓN RÁPIDA - LEE ESTO PRIMERO

## ✅ Lista de Verificación para Nuevo Proyecto

### 1. Variables de Entorno (.env)
```bash
cp .env.example .env
```
**Edita `.env` y cambia:**
- [ ] `SECRET_KEY` - ⚠️ OBLIGATORIO para seguridad
- [ ] `APP_NAME` - Nombre de tu aplicación
- [ ] `DATABASE_URL` - Si usas PostgreSQL
- [ ] `ALLOWED_ORIGINS` - Dominio de tu frontend

### 2. Configuración de la Aplicación
**Edita `app/config.py`:**
- [ ] `app_name` - Nombre por defecto
- [ ] `app_version` - Versión inicial

### 3. Instalar y Ejecutar
```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear base de datos
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 4. Ejecutar
uvicorn app.main:app --reload
```

### 4. URLs Importantes
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Personalización por Proyecto

### Agregar Nuevos Modelos
1. **Edita `app/models/__init__.py`**:
```python
class MiModelo(SQLModel, table=True):
    __tablename__ = "mi_tabla"
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
```

2. **Crear migración**:
```bash
alembic revision --autogenerate -m "Add MiModelo"
alembic upgrade head
```

### Agregar Nuevos Endpoints
1. **Crear `app/api/mi_endpoint.py`**:
```python
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def get_items():
    return {"items": []}
```

2. **Registrar en `app/api/__init__.py`**:
```python
from app.api import mi_endpoint
api_router.include_router(mi_endpoint.router, prefix="/items", tags=["items"])
```

## 🚨 Seguridad - IMPORTANTE

### Producción:
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` único y seguro
- [ ] Base de datos PostgreSQL
- [ ] HTTPS habilitado
- [ ] CORS configurado correctamente

### Generar SECRET_KEY segura:
```python
import secrets
print(secrets.token_urlsafe(32))
```

## 📝 Después de Configurar

1. **Elimina este archivo** (`SETUP.md`)
2. **Actualiza README.md** con info específica de tu proyecto
3. **Commit inicial**:
```bash
git init
git add .
git commit -m "Initial commit from FastAPI template"
```

¡Tu API está lista! 🎉
