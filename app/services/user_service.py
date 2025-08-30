"""
Servicios de lógica de negocio para usuarios.

Este módulo contiene toda la lógica de negocio relacionada con usuarios,
incluyendo operaciones CRUD, autenticación y logging de eventos.
"""

from sqlmodel import Session, select
from typing import List, Optional
from loguru import logger
from app.models import User, UserCreate, UserUpdate
from app.security import get_password_hash, verify_password
from app.logging_config import log_business_event, log_security_event, log_error


class UserService:
    """
    Servicio para operaciones de usuario.
    
    Encapsula toda la lógica de negocio relacionada con usuarios,
    incluyendo CRUD, autenticación y logging automático.
    
    Attributes:
        db: Sesión de base de datos SQLModel
    """
    
    def __init__(self, db: Session):
        """
        Inicializar el servicio de usuarios.
        
        Args:
            db: Sesión de base de datos SQLModel
        """
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtener usuario por ID.
        
        Args:
            user_id: ID único del usuario
            
        Returns:
            Optional[User]: Usuario encontrado o None si no existe
        """
        statement = select(User).where(User.id == user_id)
        return self.db.exec(statement).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Obtener usuario por email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Optional[User]: Usuario encontrado o None si no existe
        """
        statement = select(User).where(User.email == email)
        return self.db.exec(statement).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Obtener usuario por username.
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Optional[User]: Usuario encontrado o None si no existe
        """
        statement = select(User).where(User.username == username)
        return self.db.exec(statement).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Obtener lista paginada de usuarios.
        
        Args:
            skip: Número de registros a saltar (para paginación)
            limit: Número máximo de registros a retornar
            
        Returns:
            List[User]: Lista de usuarios
        """
        statement = select(User).offset(skip).limit(limit)
        return self.db.exec(statement).all()

    def create_user(self, user: UserCreate) -> User:
        """
        Crear nuevo usuario.
        
        Args:
            user: Datos del usuario a crear
            
        Returns:
            User: Usuario creado con ID asignado
            
        Raises:
            Exception: Si ocurre un error durante la creación
            
        Note:
            - Hashea automáticamente la contraseña
            - Registra evento de negocio
            - Hace rollback automático en caso de error
        """
        try:
            hashed_password = get_password_hash(user.password)
            db_user = User(
                email=user.email,
                username=user.username,
                hashed_password=hashed_password,
                is_active=user.is_active
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            log_business_event(
                "user_created", 
                {"user_id": db_user.id, "username": db_user.username, "email": db_user.email},
                user_id=str(db_user.id)
            )
            logger.info(f"New user created: {db_user.username}")
            
            return db_user
        except Exception as e:
            self.db.rollback()
            log_error(e, {"operation": "create_user", "email": user.email})
            raise

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Autenticar usuario con credenciales.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Optional[User]: Usuario autenticado o None si las credenciales son inválidas
            
        Note:
            - Registra eventos de seguridad para intentos fallidos
            - Registra evento de negocio para autenticación exitosa
            - Verifica tanto existencia del usuario como contraseña
        """
        user = self.get_user_by_username(username)
        if not user:
            log_security_event(
                "login_failed_user_not_found",
                {"username": username}
            )
            return None
            
        if not verify_password(password, user.hashed_password):
            log_security_event(
                "login_failed_invalid_password",
                {"username": username, "user_id": user.id}
            )
            return None
            
        log_business_event(
            "user_authenticated",
            {"username": username, "user_id": user.id},
            user_id=str(user.id)
        )
        logger.info(f"User authenticated successfully: {username}")
        
        return user

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        Actualizar información de usuario.
        
        Args:
            user_id: ID del usuario a actualizar
            user_update: Datos a actualizar (solo campos no nulos)
            
        Returns:
            Optional[User]: Usuario actualizado o None si no existe
            
        Note:
            - Solo actualiza campos que no son None en user_update
            - Hashea automáticamente la contraseña si se incluye
            - Actualiza el timestamp updated_at automáticamente
        """
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int) -> bool:
        """
        Eliminar usuario.
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False si no existe
            
        Warning:
            Esta operación es permanente y no se puede deshacer.
            Considera usar soft delete (is_active=False) en su lugar.
        """
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
