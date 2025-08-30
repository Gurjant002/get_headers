"""
Middleware de logging para FastAPI.

Este módulo proporciona middleware personalizado para el logging automático de
requests y responses HTTP, incluyendo métricas de rendimiento y manejo de errores.

Clases:
- LoggingMiddleware: Middleware ASGI para logging a nivel de aplicación
- LoggingRoute: Route personalizada con logging a nivel de endpoint

El middleware captura automáticamente:
- Información del request (método, URL, headers, IP del cliente)
- Información del response (status code, tiempo de procesamiento, tamaño)
- Errores y excepciones con stack trace
"""
import time
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute
from loguru import logger


class LoggingMiddleware:
    """
    Middleware para logging automático de requests y responses.
    
    Este middleware intercepta todas las requests HTTP y registra automáticamente:
    - Información del request (método, URL, headers, IP)
    - Métricas de rendimiento (tiempo de procesamiento)
    - Status code y tamaño del response
    - Niveles de log apropiados según el status code
    """
    
    def __init__(self, app):
        """
        Inicializar el middleware.
        
        Args:
            app: Instancia de la aplicación ASGI
        """
        self.app = app

    async def __call__(self, scope, receive, send):
        """
        Procesar una request HTTP con logging.
        
        Args:
            scope: Información del scope ASGI
            receive: Callable para recibir mensajes ASGI
            send: Callable para enviar mensajes ASGI
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time.time()
        
        # Capturar información del request
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # Log del request (comentado temporalmente para evitar duplicación)
        # logger.info(
        #     f"{request.method} {request.url.path}",
        #     extra={
        #         "event_type": "request_start",
        #         "request_info": request_info,
        #         "timestamp": start_time
        #     }
        # )

        # Interceptar el response
        response_body = b""
        response_status_code = 200

        async def send_wrapper(message):
            """
            Wrapper para interceptar mensajes del response.
            
            Args:
                message: Mensaje ASGI del response
            """
            nonlocal response_body, response_status_code
            
            if message["type"] == "http.response.start":
                response_status_code = message["status"]
            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")
            
            await send(message)

        await self.app(scope, receive, send_wrapper)

        # Calcular duración
        process_time = time.time() - start_time
        
        # Log del response
        response_info = {
            "status_code": response_status_code,
            "process_time": round(process_time * 1000, 2),  # en ms
            "response_size": len(response_body)
        }
        
        # Nivel de log según status code
        if response_status_code >= 500:
            log_level = "error"
        elif response_status_code >= 400:
            log_level = "warning"
        else:
            log_level = "info"
            
        logger.log(
            log_level.upper(),
            f"{request.method} {request.url.path} - {response_status_code} ({process_time*1000:.2f}ms)",
            extra={
                "event_type": "request_complete",
                "request_info": request_info,
                "response_info": response_info
            }
        )


class LoggingRoute(APIRoute):
    """
    Route personalizada con logging automático a nivel de endpoint.
    
    Esta clase extiende APIRoute para agregar logging específico a cada endpoint,
    capturando información sobre la ejecución del handler y errores específicos.
    """
    
    def get_route_handler(self) -> Callable:
        """
        Obtener el handler de la ruta con logging integrado.
        
        Returns:
            Callable: Handler de la ruta con logging automático
        """
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # Log adicional a nivel de endpoint
            endpoint_info = {
                "endpoint": self.path,
                "name": self.name,
                "methods": list(self.methods)
            }
            
            logger.debug(
                f"Executing endpoint: {self.name}",
                extra={
                    "event_type": "endpoint_execution",
                    "endpoint_info": endpoint_info
                }
            )
            
            try:
                response = await original_route_handler(request)
                return response
            except Exception as e:
                logger.error(
                    f"Error in endpoint {self.name}: {str(e)}",
                    extra={
                        "event_type": "endpoint_error",
                        "endpoint_info": endpoint_info,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )
                raise

        return custom_route_handler
