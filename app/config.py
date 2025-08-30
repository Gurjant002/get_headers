"""
Configuración de la aplicación FastAPI.

Este módulo contiene todas las configuraciones de la aplicación,
incluyendo configuración de base de datos, JWT, CORS, etc.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Configuración principal de la aplicación.
    
    Utiliza Pydantic Settings para cargar configuración desde variables
    de entorno y valores por defecto.
    
    Attributes:
        database_url: URL de conexión a la base de datos
        secret_key: Clave secreta para JWT y criptografía
        algorithm: Algoritmo usado para JWT
        access_token_expire_minutes: Tiempo de expiración del token en minutos
        app_name: Nombre de la aplicación
        app_version: Versión de la aplicación
        debug: Modo debug activado/desactivado
        allowed_origins: Lista de orígenes permitidos para CORS
    """
    
    # Base de datos
    database_url: str = "sqlite:///./app.db"
    
    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App
    app_name: str = "FastAPI Template"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    class Config:
        """Configuración de Pydantic Settings."""
        env_file = ".env"


# Instancia global de configuración
settings = Settings()
