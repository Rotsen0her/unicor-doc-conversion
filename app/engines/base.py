"""
Interfaz de motor de conversión. Cada engine (docling, markitdown, futuro
marker/otro) implementa esto — el HTTP nunca depende directamente de un
vendor específico, así se puede cambiar/agregar motores sin tocar routes/.
"""
from dataclasses import dataclass, field
from typing import List, Protocol


@dataclass
class AssetItem:
    """Imagen embebida extraída del documento — bytes en base64 porque el
    servicio es stateless, no persiste nada a disco entre requests."""
    filename: str
    content_type: str
    data_base64: str


@dataclass
class ConversionResult:
    markdown: str
    engine_used: str
    pages: int
    headings: int
    tables: int
    warnings: List[str] = field(default_factory=list)
    assets: List[AssetItem] = field(default_factory=list)


class ConversionEngine(Protocol):
    name: str

    def convert(self, file_bytes: bytes, filename: str, *, ocr: bool, extract_images: bool) -> ConversionResult:
        ...
