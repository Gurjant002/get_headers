"""
Configuración del sistema de logging usando Loguru.

Este módulo configura un sistema de logging avanzado que:
- Integra Loguru con el logging estándar de Python
- Configura rotación automática de archivos en producción
- Proporciona funciones especializadas para diferentes tipos de eventos
- Intercepta logs de librerías externas como uvicorn y FastAPI

Funciones principales:
- setup_logging(): Configura el sistema completo
- log_business_event(): Para eventos de negocio importantes
- log_security_event(): Para eventos de seguridad
- log_error(): Para manejo centralizado de errores
"""
import sys
import logging
from typing import Any, Dict
from loguru import logger
from app.config.config import settings


class InterceptHandler(logging.Handler):
    """
    Intercepta logs de otras librerías y los redirige a Loguru.
    
    Esta clase permite que todas las librerías que usan el logging estándar
    de Python (como uvicorn, sqlalchemy, etc.) sean manejadas por Loguru,
    manteniendo un formato consistente en toda la aplicación.
    """
    
    def emit(self, record):
        """
        Procesa un record de logging y lo envía a Loguru.
        
        Args:
            record: Record de logging del módulo logging estándar
        """
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """
    Configurar el sistema de logging completo de la aplicación.
    
    Configura Loguru como el manejador principal de logs con:
    - Handler de consola para desarrollo con colores
    - Handler de archivos rotativos para producción
    - Interceptor para librerías externas
    - Configuración de niveles por librería
    
    Returns:
        logger: Instancia configurada de Loguru
    """
    
    # Remover TODOS los handlers existentes de loguru
    logger.remove()
    
    # Limpiar todos los handlers del logging estándar
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configurar formato de logs
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Agregar handler para consola
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if settings.debug else "INFO",
        colorize=True,
        backtrace=True,
        diagnose=True,
        filter=lambda record: not record["name"].startswith("uvicorn.access")  # Filtrar logs de acceso
    )
    
    # Agregar handler para archivo (solo en producción)
    if not settings.debug:
        logger.add(
            "logs/app.log",
            format=log_format,
            level="INFO",
            rotation="1 day",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=False,  # No mostrar variables en producción por seguridad
        )
        
        # Archivo separado para errores
        logger.add(
            "logs/errors.log",
            format=log_format,
            level="ERROR",
            rotation="1 week",
            retention="1 month",
            compression="zip",
            backtrace=True,
            diagnose=False,
        )
    
    # Interceptar logs de otras librerías
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Configurar niveles específicos para librerías
    for logger_name in ["uvicorn", "uvicorn.error", "fastapi"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False  # ← AGREGAR ESTA LÍNEA
    
    # Reducir verbosidad de algunas librerías
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # CRÍTICO: Desactivar propagación del logger raíz
    logging.getLogger().handlers.clear()  # ← NUEVA LÍNEA
    logging.getLogger().addHandler(InterceptHandler())  # ← NUEVA LÍNEA
    logging.getLogger().propagate = False  # ← NUEVA LÍNEA
    
    return logger


def log_request(request_data: Dict[str, Any], user_id: str = None):
    """
    Log de requests HTTP con información contextual.
    
    Args:
        request_data: Diccionario con datos del request (método, URL, headers, etc.)
        user_id: ID del usuario que hace el request (opcional)
    """
    logger.info(
        "Request received",
        extra={
            "request_data": request_data,
            "user_id": user_id,
            "event_type": "request"
        }
    )


def log_response(response_data: Dict[str, Any], status_code: int, user_id: str = None):
    """
    Log de responses HTTP.
    
    Args:
        response_data: Diccionario con datos del response
        status_code: Código de estado HTTP de la respuesta
        user_id: ID del usuario que recibe el response (opcional)
    """
    logger.info(
        f"Response sent with status {status_code}",
        extra={
            "response_data": response_data,
            "status_code": status_code,
            "user_id": user_id,
            "event_type": "response"
        }
    )


def log_error(error: Exception, context: Dict[str, Any] = None, user_id: str = None):
    """
    Log de errores con contexto detallado.
    
    Args:
        error: Excepción que se produjo
        context: Información adicional sobre el contexto del error (opcional)
        user_id: ID del usuario relacionado con el error (opcional)
    """
    logger.error(
        f"Error occurred: {str(error)}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "user_id": user_id,
            "event_type": "error"
        }
    )


def log_business_event(event_name: str, data: Dict[str, Any] = None, user_id: str = None):
    """
    Log de eventos de negocio importantes.
    
    Usar para eventos significativos como: creación de pedidos, pagos,
    cambios de estado importantes, etc.
    
    Args:
        event_name: Nombre del evento de negocio
        data: Datos específicos del evento (opcional)
        user_id: ID del usuario que generó el evento (opcional)
    """
    logger.info(
        f"Business event: {event_name}",
        extra={
            "event_name": event_name,
            "event_data": data or {},
            "user_id": user_id,
            "event_type": "business"
        }
    )


def log_security_event(event_type: str, details: Dict[str, Any] = None, user_id: str = None):
    """
    Log de eventos de seguridad.
    
    Usar para eventos como: intentos de login fallidos, accesos no autorizados,
    cambios de permisos, etc.
    
    Args:
        event_type: Tipo de evento de seguridad
        details: Detalles específicos del evento (opcional)
        user_id: ID del usuario relacionado con el evento (opcional)
    """
    logger.warning(
        f"Security event: {event_type}",
        extra={
            "security_event_type": event_type,
            "details": details or {},
            "user_id": user_id,
            "event_type": "security"
        }
    )


# Inicializar logging al importar el módulo
setup_logging()
