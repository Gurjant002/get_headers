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

api_router = APIRouter()

