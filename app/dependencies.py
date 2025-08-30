"""
Dependencias de FastAPI para autenticación y autorización.

Este módulo contiene dependencias que se inyectan en los endpoints
para manejar autenticación JWT y verificación de permisos.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.database import get_db
from app.services import UserService
from app.security import verify_token
from app.models import User

# Esquema OAuth2 para extraer token Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtener usuario actual desde el token JWT.
    
    Args:
        token: Token JWT extraído del header Authorization
        db: Sesión de base de datos
        
    Returns:
        User: Usuario autenticado
        
    Raises:
        HTTPException: 401 si el token es inválido o el usuario no existe
        
    Note:
        - Verifica la validez y firma del token JWT
        - Busca el usuario en la base de datos
        - Se usa como dependency en otros endpoints
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(token)
    if username is None:
        raise credentials_exception
    
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Obtener usuario activo actual.
    
    Args:
        current_user: Usuario obtenido de get_current_user
        
    Returns:
        User: Usuario activo autenticado
        
    Raises:
        HTTPException: 400 si el usuario no está activo
        
    Note:
        - Verifica que el usuario tenga is_active=True
        - Se usa para endpoints que requieren usuarios activos
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Obtener superusuario actual.
    
    Args:
        current_user: Usuario obtenido de get_current_user
        
    Returns:
        User: Superusuario autenticado
        
    Raises:
        HTTPException: 403 si el usuario no es superusuario
        
    Note:
        - Verifica que el usuario tenga is_superuser=True
        - Se usa para endpoints que requieren permisos de administrador
        - Solo superusuarios pueden acceder a endpoints protegidos con esta dependency
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
