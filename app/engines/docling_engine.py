"""
Motor Docling — calidad (tablas, headings, multi-columna, escaneados).
Motor por defecto de este servicio: ver docs/17-08-2026/SPIKE-CONVERSION-ENGINE.md
en backend_web_bot — sobre 10 PDFs reales del producto, Docling reconstruyó
correctamente tablas que MarkItDown rompía en listas desconectadas (riesgo
real de dato incorrecto, no solo estético) y detectó headings en el 100% de
los documentos vs 0% con MarkItDown.

Nota sobre `ocr`: mapea a `do_ocr` (correr OCR en regiones sin texto
extraíble). NO usa `force_full_page_ocr` — se probó contra un PDF real con
texto corrupto (fuente mal subseteada en el original) y no lo arregló, así
que prometerlo como fix generalizado sería engañoso. Ver el spike para el
detalle. Documentos con texto realmente corrupto necesitan corrección
manual en el editor (Fase 3 del plan), no un flag de conversión.
"""
import os
import tempfile
import time

os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("TORCH_COMPILE_DISABLE", "1")

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from app.engines.base import ConversionResult

_converter_cache: dict = {}


def _get_converter(do_ocr: bool) -> DocumentConverter:
    """Cachea el DocumentConverter por combinación de opciones — cargar
    los modelos de layout en cada request sería carísimo."""
    if do_ocr not in _converter_cache:
        opts = PdfPipelineOptions()
        opts.do_ocr = do_ocr
        opts.do_table_structure = True
        # Extracción de imágenes a storage es Fase 4 del plan, no v1 — no se
        # genera nada de eso acá todavía, se ignora `extract_images` por ahora.
        opts.generate_picture_images = False
        _converter_cache[do_ocr] = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
        )
    return _converter_cache[do_ocr]


class DoclingEngine:
    name = "docling"

    def convert(self, file_bytes: bytes, filename: str, *, ocr: bool, extract_images: bool) -> ConversionResult:
        warnings = []
        if extract_images:
            warnings.append(
                "extract_images=true todavía no está implementado (Fase 4 del plan) — "
                "se ignoraron las imágenes embebidas, no se generó ningún asset."
            )

        suffix = os.path.splitext(filename)[1] or ".pdf"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            converter = _get_converter(do_ocr=ocr)
            t0 = time.time()
            result = converter.convert(tmp_path)
            elapsed = time.time() - t0

            doc = result.document
            markdown = doc.export_to_markdown()
            n_pages = len(doc.pages) if hasattr(doc, "pages") else 0
            n_headings = sum(1 for line in markdown.splitlines() if line.strip().startswith("#"))
            n_tables = len(doc.tables) if hasattr(doc, "tables") else 0

            if elapsed > 30:
                warnings.append(f"Conversión lenta ({elapsed:.1f}s) — considerar el job async (Fase 1.5, no implementado).")

            return ConversionResult(
                markdown=markdown,
                engine_used=self.name,
                pages=n_pages,
                headings=n_headings,
                tables=n_tables,
                warnings=warnings,
                assets=[],
            )
        finally:
            os.unlink(tmp_path)
