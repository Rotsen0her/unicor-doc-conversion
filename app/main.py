"""
Servicio de conversión PDF/Office → Markdown. Stateless, red interna,
consumido solo por el backend RAG (backend_web_bot) — nunca directamente
por el frontend. Ver docs/17-08-2026/ para el contexto completo del plan.
"""
import logging

from fastapi import FastAPI

from app.config import get_settings
from app.routes import convert_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Unicor Doc Conversion Service",
    description="Convierte PDF/Office a Markdown (MarkItDown / Docling) para el RAG de backend_web_bot",
    version="1.0.0",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
)

app.include_router(convert_router)


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
