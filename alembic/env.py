"""
Configuración de Alembic para migraciones de base de datos.

Este módulo configura Alembic para trabajar con SQLModel y proporciona
las funciones necesarias para ejecutar migraciones tanto en modo offline
como online.

Características:
- Configurado para trabajar con SQLModel en lugar de SQLAlchemy puro
- Importa automáticamente todos los modelos de la aplicación
- Usa la configuración de base de datos desde app.config
- Soporta tanto migraciones offline como online

Para crear una nueva migración:
    alembic revision --autogenerate -m "Descripción del cambio"

Para aplicar migraciones:
    alembic upgrade head
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.models import *  # Importar todos los modelos SQLModel
from sqlmodel import SQLModel
from app.config import settings

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = SQLModel.metadata

# Configurar la URL de la base de datos
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """
    Ejecutar migraciones en modo 'offline'.
    
    En modo offline, Alembic no se conecta a la base de datos sino que
    genera scripts SQL que pueden ejecutarse posteriormente. Útil para
    generar migraciones sin acceso directo a la base de datos.
    
    El modo offline:
    - No requiere conexión activa a la base de datos
    - Genera scripts SQL estáticos
    - Es útil para revisar cambios antes de aplicarlos
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Ejecutar migraciones en modo 'online'.
    
    En modo online, Alembic se conecta directamente a la base de datos
    y ejecuta las migraciones inmediatamente. Es el modo más común y
    el que se usa cuando ejecutas 'alembic upgrade head'.
    
    El modo online:
    - Requiere conexión activa a la base de datos
    - Ejecuta migraciones directamente en la BD
    - Proporciona feedback inmediato sobre errores
    - Es el modo por defecto para operaciones normales
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
