"""
Ejemplos de uso del sistema de logging avanzado

Este archivo muestra cómo usar las diferentes funciones de logging
disponibles en la plantilla FastAPI.
"""

from loguru import logger
from app.config.logging_config import (
    log_request, 
    log_response, 
    log_error, 
    log_business_event, 
    log_security_event
)

# ========================================
# EJEMPLOS DE LOGGING BÁSICO CON LOGURU
# ========================================

def ejemplos_logging_basico():
    """Ejemplos de logging básico con diferentes niveles"""
    
    # Logs de diferentes niveles
    logger.debug("Información de debug - solo se ve en desarrollo")
    logger.info("Información general")
    logger.warning("Advertencia sobre algo")
    logger.error("Error que necesita atención")
    logger.critical("Error crítico del sistema")
    
    # Logs con contexto adicional
    logger.info("Usuario realizó acción", extra={
        "user_id": 123,
        "action": "login",
        "ip_address": "192.168.1.1"
    })


# ========================================
# EJEMPLOS DE LOGGING ESTRUCTURADO
# ========================================

def ejemplos_logging_estructurado():
    """Ejemplos de logging con estructura específica"""
    
    # Log de evento de negocio
    log_business_event(
        event_name="order_created",
        data={
            "order_id": "ORD-12345",
            "amount": 99.99,
            "currency": "USD",
            "items_count": 3
        },
        user_id="user_123"
    )
    
    # Log de evento de seguridad
    log_security_event(
        event_type="suspicious_activity",
        details={
            "ip_address": "192.168.1.100",
            "failed_attempts": 5,
            "time_window": "5_minutes"
        },
        user_id="user_456"
    )
    
    # Log de request (normalmente automático)
    log_request(
        request_data={
            "method": "POST",
            "path": "/api/v1/orders",
            "user_agent": "Mozilla/5.0...",
            "ip": "192.168.1.1"
        },
        user_id="user_123"
    )
    
    # Log de response (normalmente automático)
    log_response(
        response_data={"order_id": "ORD-12345"},
        status_code=201,
        user_id="user_123"
    )


# ========================================
# EJEMPLOS DE LOGGING DE ERRORES
# ========================================

def ejemplos_logging_errores():
    """Ejemplos de logging de errores con contexto"""
    
    try:
        # Simular una operación que falla
        result = 1 / 0
    except Exception as e:
        # Log del error con contexto
        log_error(
            error=e,
            context={
                "operation": "calculate_discount",
                "order_id": "ORD-12345",
                "user_id": "user_123"
            },
            user_id="user_123"
        )


# ========================================
# EJEMPLOS EN ENDPOINTS DE FASTAPI
# ========================================

"""
Ejemplo de uso en un endpoint de FastAPI:

from fastapi import APIRouter, Depends
from loguru import logger
from app.logging_config import log_business_event, log_security_event

router = APIRouter()

@router.post("/orders")
async def create_order(order_data: OrderCreate, current_user = Depends(get_current_user)):
    try:
        # Log del inicio de la operación
        logger.info(f"Creating order for user {current_user.id}")
        
        # Tu lógica de negocio aquí
        order = create_order_logic(order_data)
        
        # Log del evento de negocio
        log_business_event(
            event_name="order_created",
            data={
                "order_id": order.id,
                "amount": order.total_amount,
                "items_count": len(order.items)
            },
            user_id=str(current_user.id)
        )
        
        return order
        
    except ValidationError as e:
        # Log de error de validación
        log_error(e, {"user_id": current_user.id, "order_data": order_data})
        raise HTTPException(status_code=400, detail="Invalid order data")
    
    except PaymentError as e:
        # Log de error de pago
        log_business_event(
            event_name="payment_failed",
            data={
                "user_id": current_user.id,
                "amount": order_data.total_amount,
                "error": str(e)
            },
            user_id=str(current_user.id)
        )
        raise HTTPException(status_code=402, detail="Payment failed")


@router.post("/auth/login")
async def login(credentials: LoginCredentials):
    user = authenticate_user(credentials.username, credentials.password)
    
    if not user:
        # Log de intento de login fallido
        log_security_event(
            event_type="login_failed",
            details={
                "username": credentials.username,
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent")
            }
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Log de login exitoso
    log_business_event(
        event_name="user_login",
        data={
            "username": user.username,
            "last_login": user.last_login.isoformat() if user.last_login else None
        },
        user_id=str(user.id)
    )
    
    return {"access_token": create_access_token(user)}
"""


# ========================================
# CONFIGURACIÓN PERSONALIZADA
# ========================================

def configuracion_logging_personalizada():
    """Ejemplo de configuración personalizada de logging"""
    
    # Agregar un sink personalizado para errores críticos
    logger.add(
        "logs/critical_errors.log",
        level="CRITICAL",
        rotation="1 day",
        retention="90 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        filter=lambda record: record["level"].name == "CRITICAL"
    )
    
    # Agregar sink para eventos de negocio específicos
    logger.add(
        "logs/business_events.log",
        level="INFO",
        rotation="1 day",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {extra[event_name]} | {message}",
        filter=lambda record: record["extra"].get("event_type") == "business"
    )


# ========================================
# MEJORES PRÁCTICAS
# ========================================

"""
MEJORES PRÁCTICAS PARA LOGGING:

1. **Usa niveles apropiados**:
   - DEBUG: Información detallada para debugging
   - INFO: Eventos normales del sistema
   - WARNING: Algo inesperado pero no crítico
   - ERROR: Error que necesita atención
   - CRITICAL: Error que puede detener la aplicación

2. **Incluye contexto relevante**:
   - user_id para trazabilidad
   - request_id para seguir requests
   - Datos relevantes del negocio

3. **No loggees información sensible**:
   - Contraseñas
   - Tokens de acceso completos
   - Información personal sensible

4. **Usa logging estructurado**:
   - Consistencia en el formato
   - Fácil parsing y análisis
   - Mejor para herramientas de monitoreo

5. **Rotar logs apropiadamente**:
   - Por tamaño o tiempo
   - Mantener solo los necesarios
   - Comprimir logs antiguos

6. **Monitorea los logs**:
   - Alertas para errores críticos
   - Análisis de patrones
   - Dashboards de métricas
"""

print("Ejecutando ejemplos de logging...")
print("Logs básicos:")
ejemplos_logging_basico()
print("\nLogs estructurados:")
ejemplos_logging_estructurado()
print("\nLogs de errores:")
ejemplos_logging_errores()
print("\nConfiguración personalizada de logging:")
configuracion_logging_personalizada()