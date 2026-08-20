"""
POST /v1/convert — contrato exacto del plan (backend_web_bot docs, sección
"Servicio de conversión"): multipart file + engine/ocr/extract_images,
respuesta {markdown, engine_used, metadata, assets}.
"""
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from typing import List, Literal, Optional

from app.auth import verify_internal_key
from app.config import get_settings
from app.engines import DEFAULT_ENGINE, ENGINES

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["Conversión"])

EngineName = Literal["auto", "markitdown", "docling"]


class ConvertMetadata(BaseModel):
    pages: int
    headings: int
    tables: int
    warnings: List[str]


class ConvertResponse(BaseModel):
    markdown: str
    engine_used: str
    metadata: ConvertMetadata
    assets: List[str]


@router.get("/engines")
async def list_engines(_: str = Depends(verify_internal_key)):
    """Qué motores están instalados y cuál es el default."""
    return {
        "engines": list(ENGINES.keys()),
        "default": DEFAULT_ENGINE,
    }


@router.post("/convert", response_model=ConvertResponse)
async def convert(
    file: UploadFile = File(...),
    engine: EngineName = Form(default="auto"),
    ocr: bool = Form(default=True),
    extract_images: bool = Form(default=False),
    _: str = Depends(verify_internal_key),
):
    """
    Convierte un archivo a Markdown.

    `engine=auto` resuelve al motor por defecto (Docling) — no hay
    heurística de "si tiene tabla usar Docling": para el volumen de
    documentos de este proyecto no se justifica esa complejidad extra
    (correr un detector barato costaría casi lo mismo que convertir
    directo). Ver el spike para el razonamiento completo.
    """
    settings = get_settings()
    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=422, detail="El archivo está vacío")
    if len(data) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=422,
            detail=f"Archivo supera el máximo de {settings.max_file_size_mb} MB",
        )

    engine_name = DEFAULT_ENGINE if engine == "auto" else engine
    conversion_engine = ENGINES.get(engine_name)
    if conversion_engine is None:
        raise HTTPException(status_code=422, detail=f"Motor desconocido: {engine_name}")

    try:
        result = conversion_engine.convert(
            data, file.filename or "documento.pdf", ocr=ocr, extract_images=extract_images
        )
    except Exception as exc:
        logger.exception("Error convirtiendo %s con %s", file.filename, engine_name)
        raise HTTPException(status_code=500, detail=f"Error de conversión: {exc}")

    return ConvertResponse(
        markdown=result.markdown,
        engine_used=result.engine_used,
        metadata=ConvertMetadata(
            pages=result.pages,
            headings=result.headings,
            tables=result.tables,
            warnings=result.warnings,
        ),
        assets=result.assets,
    )
