"""
Configuración del middleware personalizado.

Este módulo exporta todas las clases de middleware personalizado
disponibles en la aplicación, facilitando su importación desde
otros módulos.

Middleware disponible:
- LoggingMiddleware: Middleware ASGI para logging automático de requests/responses
- LoggingRoute: Route personalizada con logging específico por endpoint

Uso:
    from app.middleware import LoggingMiddleware
    app.add_middleware(LoggingMiddleware)
"""
from .logging_middleware import LoggingMiddleware, LoggingRoute

__all__ = ["LoggingMiddleware", "LoggingRoute"]
