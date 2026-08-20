"""
Registro de motores disponibles. `auto` no es un motor real — se resuelve
a `default_engine` (Docling) en app.routes.convert. Ver spike: para el
volumen de este proyecto no se justifica una heurística de detección de
tablas antes de convertir (costaría casi lo mismo que convertir directo
con Docling).
"""
from app.engines.base import ConversionEngine, ConversionResult
from app.engines.docling_engine import DoclingEngine
from app.engines.markitdown_engine import MarkItDownEngine

ENGINES: dict[str, ConversionEngine] = {
    "docling": DoclingEngine(),
    "markitdown": MarkItDownEngine(),
}

DEFAULT_ENGINE = "docling"

__all__ = ["ConversionEngine", "ConversionResult", "ENGINES", "DEFAULT_ENGINE"]
