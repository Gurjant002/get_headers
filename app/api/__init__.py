"""
Configuración del router principal de la API.

Este módulo configura el router principal que agrupa todos los endpoints
de la aplicación bajo el prefijo /api/v1. Aquí se registran todos los
sub-routers de los diferentes módulos de la API.

Para agregar nuevos endpoints:
1. Crear el archivo del router en app/api/
2. Importarlo aquí
3. Registrarlo con api_router.include_router()

Ejemplo:
    from app.api import products
    api_router.include_router(products.router, prefix="/products", tags=["products"])
"""
from fastapi import APIRouter
from app.api import auth, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
