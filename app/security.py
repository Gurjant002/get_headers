"""
Utilidades de seguridad y autenticación.

Este módulo contiene todas las funciones relacionadas con:
- Hash y verificación de contraseñas
- Creación y verificación de tokens JWT
- Configuración de contexto de contraseñas
"""

# from passlib.context import CryptContext
# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from typing import Optional
# from app.config import settings

# # Contexto para hash de contraseñas con bcrypt
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """
#     Verificar contraseña contra su hash.
    
#     Args:
#         plain_password: Contraseña en texto plano
#         hashed_password: Contraseña hasheada almacenada
        
#     Returns:
#         bool: True si la contraseña coincide, False en caso contrario
#     """
#     return pwd_context.verify(plain_password, hashed_password)


# def get_password_hash(password: str) -> str:
#     """
#     Generar hash de contraseña.
    
#     Args:
#         password: Contraseña en texto plano
        
#     Returns:
#         str: Contraseña hasheada con bcrypt
#     """
#     return pwd_context.hash(password)


# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     """
#     Crear token JWT de acceso.
    
#     Args:
#         data: Datos a incluir en el token (típicamente {"sub": username})
#         expires_delta: Tiempo de expiración personalizado (opcional)
        
#     Returns:
#         str: Token JWT codificado
        
#     Note:
#         Si no se especifica expires_delta, usa el valor por defecto
#         de la configuración (ACCESS_TOKEN_EXPIRE_MINUTES).
#     """
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
#     return encoded_jwt


# def verify_token(token: str) -> Optional[str]:
#     """
#     Verificar y decodificar token JWT.
    
#     Args:
#         token: Token JWT a verificar
        
#     Returns:
#         Optional[str]: Username extraído del token si es válido, None en caso contrario
        
#     Note:
#         Verifica la firma del token y que no haya expirado.
#         Extrae el username del campo "sub" del payload.
#     """
#     try:
#         payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
#         username: str = payload.get("sub")
#         if username is None:
#             return None
#         return username
#     except JWTError:
#         return None
