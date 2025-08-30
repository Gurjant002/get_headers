"""
Modelos de datos de la aplicación.

Este módulo contiene todos los modelos SQLModel que definen:
- Estructura de las tablas de la base de datos
- Schemas para validación de entrada/salida de la API
- Modelos para autenticación y JWT
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class UserBase(SQLModel):
    """
    Modelo base para Usuario.
    
    Contiene los campos comunes que se utilizan en diferentes
    operaciones relacionadas con usuarios.
    
    Attributes:
        email: Email único del usuario
        username: Nombre de usuario único
        is_active: Si el usuario está activo
        is_superuser: Si el usuario tiene privilegios de administrador
    """
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)


class User(UserBase, table=True):
    """
    Modelo de Usuario para la base de datos.
    
    Representa la tabla 'users' en la base de datos con todos
    los campos necesarios para almacenar información del usuario.
    
    Attributes:
        id: ID único del usuario (clave primaria)
        hashed_password: Contraseña hasheada
        created_at: Timestamp de creación
        updated_at: Timestamp de última actualización
    """
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class UserCreate(UserBase):
    """
    Schema para crear usuario.
    
    Utilizado cuando se registra un nuevo usuario.
    Incluye la contraseña en texto plano que será hasheada.
    
    Attributes:
        password: Contraseña en texto plano
    """
    password: str


class UserUpdate(SQLModel):
    """
    Schema para actualizar usuario.
    
    Permite actualizar campos específicos del usuario.
    Todos los campos son opcionales.
    
    Attributes:
        email: Nuevo email (opcional)
        username: Nuevo username (opcional)
        password: Nueva contraseña (opcional)
        is_active: Nuevo estado activo (opcional)
    """
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """
    Schema para leer usuario (respuesta API).
    
    Utilizado para devolver información del usuario en las APIs.
    No incluye información sensible como contraseñas.
    
    Attributes:
        id: ID del usuario
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserReadWithPassword(UserRead):
    """
    Schema interno con password hash.
    
    Utilizado internamente cuando se necesita acceso a la contraseña
    hasheada. NO debe usarse en respuestas de API públicas.
    
    Attributes:
        hashed_password: Contraseña hasheada
    """
    hashed_password: str


# Schemas para autenticación
class Token(SQLModel):
    """
    Schema para token de autenticación.
    
    Respuesta del endpoint de login con el token JWT.
    
    Attributes:
        access_token: Token JWT
        token_type: Tipo de token (siempre "bearer")
    """
    access_token: str
    token_type: str


class TokenData(SQLModel):
    """
    Schema para datos del token.
    
    Utilizado para extraer información del token JWT.
    
    Attributes:
        username: Username extraído del token
    """
    username: Optional[str] = None


# Schema general para mensajes
class Message(SQLModel):
    """
    Schema para mensajes de respuesta.
    
    Utilizado para respuestas simples que solo contienen un mensaje.
    
    Attributes:
        message: Mensaje de respuesta
    """
    message: str
