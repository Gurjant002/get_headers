"""
Aplicación principal FastAPI.

Este módulo contiene la configuración y creación de la aplicación FastAPI,
incluyendo middleware, manejo de errores, eventos de lifecycle y endpoints básicos.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger

from app.config import settings
from app.database import create_db_and_tables
from app.api import api_router
from app.middleware import LoggingMiddleware
from app.logging_config import setup_logging, log_business_event, log_error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Eventos de inicio y cierre de la aplicación.
    
    Maneja la inicialización y limpieza de recursos cuando
    la aplicación inicia y se detiene.
    
    Args:
        app: Instancia de la aplicación FastAPI
        
    Note:
        - Crea tablas de base de datos al inicio
        - Registra eventos de startup/shutdown
        - Se ejecuta una vez por ciclo de vida de la aplicación
    """
    # Startup
    setup_logging()  # ← AGREGAR ESTA LÍNEA
    logger.info("🚀 Starting FastAPI application...")
    create_db_and_tables()
    log_business_event("application_startup", {"version": settings.app_version})
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down FastAPI application...")
    log_business_event("application_shutdown")
    logger.info("✅ Application shutdown complete")


def create_application() -> FastAPI:
    """
    Factory para crear la aplicación FastAPI.
    
    Configura todos los aspectos de la aplicación incluyendo:
    - Middleware (CORS, Logging)
    - Rutas y endpoints
    - Manejo de errores
    - Documentación automática
    
    Returns:
        FastAPI: Instancia configurada de la aplicación
        
    Note:
        - La documentación se habilita solo en modo debug
        - CORS se configura según las variables de entorno
        - Todos los errores se registran automáticamente
    """
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Logging middleware
    app.add_middleware(LoggingMiddleware)

    # Include routers
    app.include_router(api_router, prefix="/api/v1")

    # Exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        """
        Manejo de excepciones HTTP.
        
        Intercepta todas las HTTPException y las registra
        antes de devolver la respuesta al cliente.
        """
        log_error(exc, {"url": str(request.url), "method": request.method})
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """
        Manejo de excepciones generales no controladas.
        
        Captura cualquier excepción no manejada, la registra
        y devuelve un error 500 genérico al cliente.
        
        Note:
            - Evita que errores internos se expongan al cliente
            - Registra el error completo para debugging
        """
        log_error(exc, {"url": str(request.url), "method": request.method})
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    return app


# Instancia global de la aplicación
app = create_application()


@app.get("/")
async def root():
    """
    Endpoint raíz de la aplicación.
    
    Returns:
        dict: Mensaje de bienvenida con nombre y versión de la aplicación
        
    Note:
        - Endpoint público accesible sin autenticación
        - Útil para verificar que la aplicación está corriendo
    """
    logger.info("Root endpoint accessed")
    return {"message": f"Welcome to {settings.app_name} v{settings.app_version}"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint para monitoreo.
    
    Returns:
        dict: Estado de la aplicación y versión
        
    Note:
        - Endpoint público para health checks
        - Útil para load balancers y herramientas de monitoreo
        - Retorna 200 OK si la aplicación está funcionando
    """
    logger.debug("Health check performed")
    return {"status": "healthy", "version": settings.app_version}
