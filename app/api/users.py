"""
Endpoints de gestión de usuarios.

Este módulo contiene endpoints CRUD para usuarios:
- Listar usuarios (solo admin)
- Obtener usuario por ID
- Actualizar usuario
- Eliminar usuario (solo admin)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.database import get_db
from app.services import UserService
from app.models import UserRead, UserUpdate, Message
from app.dependencies import get_current_active_user, get_current_superuser

router = APIRouter()


@router.get("/", response_model=List[UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_superuser)
):
    """
    Obtener lista paginada de usuarios (solo administradores).
    
    Args:
        skip: Número de registros a saltar (para paginación)
        limit: Número máximo de registros a retornar (máx. 100)
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser superuser)
        
    Returns:
        List[UserRead]: Lista de usuarios (sin contraseñas)
        
    Raises:
        HTTPException: 403 si el usuario no es administrador
        
    Note:
        - Solo usuarios con is_superuser=True pueden acceder
        - Implementa paginación para mejor rendimiento
        - No retorna información sensible como contraseñas
    """
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user)
):
    """
    Obtener usuario por ID.
    
    Args:
        user_id: ID del usuario a obtener
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        
    Returns:
        UserRead: Información del usuario (sin contraseña)
        
    Raises:
        HTTPException: 403 si no tiene permisos para ver este usuario
        HTTPException: 404 si el usuario no existe
        
    Note:
        - Los usuarios pueden ver solo su propia información
        - Los administradores pueden ver cualquier usuario
    """
    user_service = UserService(db)
    
    # Los usuarios solo pueden ver su propia información o admin puede ver cualquiera
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user)
):
    """
    Actualizar información de usuario.
    
    Args:
        user_id: ID del usuario a actualizar
        user_update: Campos a actualizar (solo los no nulos)
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        
    Returns:
        UserRead: Usuario actualizado
        
    Raises:
        HTTPException: 403 si no tiene permisos para actualizar este usuario
        HTTPException: 404 si el usuario no existe
        
    Note:
        - Los usuarios pueden actualizar solo su propia información
        - Los administradores pueden actualizar cualquier usuario
        - Solo se actualizan los campos incluidos en user_update
        - Las contraseñas se hashean automáticamente
    """
    user_service = UserService(db)
    
    # Los usuarios solo pueden actualizar su propia información o admin puede actualizar cualquiera
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = user_service.update_user(user_id, user_update)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}", response_model=Message)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_superuser)
):
    """
    Eliminar usuario (solo administradores).
    
    Args:
        user_id: ID del usuario a eliminar
        db: Sesión de base de datos
        current_user: Usuario actual (debe ser superuser)
        
    Returns:
        Message: Mensaje de confirmación
        
    Raises:
        HTTPException: 403 si el usuario no es administrador
        HTTPException: 404 si el usuario no existe
        
    Warning:
        Esta operación es permanente y no se puede deshacer.
        Considera implementar soft delete (is_active=False) para casos de uso reales.
        
    Note:
        - Solo usuarios con is_superuser=True pueden eliminar usuarios
        - La eliminación es física (hard delete)
    """
    user_service = UserService(db)
    
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}
