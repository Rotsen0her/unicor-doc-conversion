"""
Auth por API key interna. Servicio pensado para red interna (o mTLS más
adelante) — sin JWT de usuario, el backend RAG es el único caller.
"""
import logging

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import get_settings

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-Internal-Key", auto_error=False)


async def verify_internal_key(api_key: str = Security(api_key_header)) -> str:
    settings = get_settings()  # no cachear en el módulo: get_settings() ya es @lru_cache
    if not settings.internal_api_key:
        logger.warning("INTERNAL_API_KEY no configurada; permitiendo acceso sin autenticar")
        return "__unsecured_mode__"

    if not api_key or api_key != settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Internal-Key inválida o ausente",
        )
    return api_key
