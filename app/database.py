"""
Configuración y utilidades de base de datos.

Este módulo maneja la conexión a la base de datos y proporciona
las funciones necesarias para crear tablas y obtener sesiones.
"""

from sqlmodel import create_engine, SQLModel, Session
from app.config import settings

# Engine de SQLAlchemy/SQLModel
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)


def create_db_and_tables():
    """
    Crear todas las tablas de la base de datos.
    
    Esta función crea todas las tablas definidas en los modelos SQLModel.
    Se ejecuta típicamente al inicio de la aplicación.
    """
    SQLModel.metadata.create_all(engine)


def get_db():
    """
    Dependency para obtener sesión de base de datos.
    
    Genera una sesión de base de datos que se puede usar como dependency
    en endpoints de FastAPI. La sesión se cierra automáticamente.
    
    Yields:
        Session: Sesión de base de datos SQLModel
    """
    with Session(engine) as session:
        yield session
