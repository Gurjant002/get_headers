"""
Configuración de la aplicación FastAPI.

Este módulo contiene todas las configuraciones de la aplicación,
incluyendo configuración de base de datos, JWT, CORS, etc.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Union


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
    app_name: str = "get_headers"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # CORS - Usar string en lugar de lista para evitar problemas de parsing
    allowed_origins_str: str = "http://localhost:3000,http://localhost:8080"
    
    @property
    def allowed_origins(self) -> List[str]:
        """Convierte el string de orígenes a lista."""
        if not self.allowed_origins_str.strip():
            return []
        return [origin.strip() for origin in self.allowed_origins_str.split(',') if origin.strip()]

    class Config:
        """Configuración de Pydantic Settings."""
        env_file = ".env"


# Instancia global de configuración
settings = Settings()
