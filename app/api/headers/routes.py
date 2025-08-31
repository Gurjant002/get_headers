from fastapi import APIRouter, FastAPI
from loguru import logger
from app.config.logging_config import log_business_event, log_error, log_request, log_response


router = APIRouter()

@router.get("/headers", response_model=dict, summary="Obtener Headers", tags=["Headers"])
async def get_headers():
    """
    Endpoint para obtener los headers de la solicitud.

    Returns:
        dict: Headers de la solicitud
    """
    log_request({"method": "GET", "url": "/headers", "headers": {}}, user_id=None)
    
    log_response({"headers": "Here are your headers!"}, 200, user_id=None)
    return {"headers": "Here are your headers!"}
