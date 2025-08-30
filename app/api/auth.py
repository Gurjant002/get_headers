"""
Endpoints de autenticación.

Este módulo contiene todos los endpoints relacionados con autenticación:
- Login con JWT
- Registro de usuarios
- Información del usuario actual
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from datetime import timedelta
from typing import List

from app.database import get_db
from app.services import UserService
from app.security import create_access_token
from app.models import Token, UserCreate, UserRead
from app.dependencies import get_current_active_user
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Iniciar sesión con username y password.
    
    Args:
        form_data: Formulario con username y password
        db: Sesión de base de datos
        
    Returns:
        Token: Token JWT de acceso y tipo de token
        
    Raises:
        HTTPException: 401 si las credenciales son incorrectas
        
    Note:
        - Acepta tanto username como email en el campo username
        - El token expira según ACCESS_TOKEN_EXPIRE_MINUTES
        - Registra eventos de seguridad automáticamente
    """
    user_service = UserService(db)
    user = user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserRead)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar nuevo usuario.
    
    Args:
        user: Datos del nuevo usuario (email, username, password)
        db: Sesión de base de datos
        
    Returns:
        UserRead: Datos del usuario creado (sin contraseña)
        
    Raises:
        HTTPException: 400 si el email o username ya existen
        
    Note:
        - Valida que email y username sean únicos
        - Hashea automáticamente la contraseña
        - Registra evento de negocio automáticamente
    """
    user_service = UserService(db)
    
    # Verificar si el usuario ya existe
    if user_service.get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if user_service.get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    return user_service.create_user(user)


@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: UserRead = Depends(get_current_active_user)
):
    """
    Obtener información del usuario actual.
    
    Args:
        current_user: Usuario autenticado (inyectado automáticamente)
        
    Returns:
        UserRead: Información del usuario actual
        
    Note:
        - Requiere token JWT válido
        - Solo devuelve información del usuario autenticado
        - No incluye información sensible como contraseñas
    """
    return current_user
