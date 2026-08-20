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
import base64
import os
import tempfile
import time
from pathlib import Path

os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("TORCH_COMPILE_DISABLE", "1")

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode

from app.config import get_settings
from app.engines.base import AssetItem, ConversionResult

_converter_cache: dict = {}

# Prefijo con el que se reescribe en el Markdown el path absoluto que deja
# Docling en artifacts_dir — así el Markdown que sale de este servicio es
# estable/portable en vez de depender del tempdir local de este proceso.
_ASSET_PATH_PREFIX = "images/"


def _get_converter(do_ocr: bool, extract_images: bool) -> DocumentConverter:
    """Cachea el DocumentConverter por combinación de opciones — cargar
    los modelos de layout en cada request sería carísimo. `extract_images`
    entra en la key porque cambia `generate_picture_images` del pipeline."""
    key = (do_ocr, extract_images)
    if key not in _converter_cache:
        opts = PdfPipelineOptions()
        opts.do_ocr = do_ocr
        opts.do_table_structure = True
        opts.generate_picture_images = extract_images
        _converter_cache[key] = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
        )
    return _converter_cache[key]


class DoclingEngine:
    name = "docling"

    def convert(self, file_bytes: bytes, filename: str, *, ocr: bool, extract_images: bool) -> ConversionResult:
        warnings = []
        suffix = os.path.splitext(filename)[1] or ".pdf"
        is_pdf = suffix.lower() == ".pdf"

        # generate_picture_images (el pipeline que lo soporta) solo está
        # configurado para PDF acá — Word/PPT/Excel/CSV usan los pipelines
        # default de Docling para esos formatos, sin este ajuste. Limitación
        # conocida de v1 (ver plan Fase 4), no bloquea el resto del flujo.
        extract_images_effective = extract_images and is_pdf
        if extract_images and not is_pdf:
            warnings.append(
                f"extract_images=true no está soportado todavía para archivos {suffix} "
                "(solo PDF) — no se generó ningún asset."
            )

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            converter = _get_converter(do_ocr=ocr, extract_images=extract_images_effective)
            t0 = time.time()
            result = converter.convert(tmp_path)
            elapsed = time.time() - t0

            doc = result.document
            n_pages = len(doc.pages) if hasattr(doc, "pages") else 0
            n_tables = len(doc.tables) if hasattr(doc, "tables") else 0

            assets: list = []
            if extract_images_effective and doc.pictures:
                markdown, assets, image_warnings = self._export_with_images(doc)
                warnings.extend(image_warnings)
            else:
                markdown = doc.export_to_markdown()

            n_headings = sum(1 for line in markdown.splitlines() if line.strip().startswith("#"))

            if elapsed > 30:
                warnings.append(f"Conversión lenta ({elapsed:.1f}s) — considerar el job async (Fase 1.5, no implementado).")

            return ConversionResult(
                markdown=markdown,
                engine_used=self.name,
                pages=n_pages,
                headings=n_headings,
                tables=n_tables,
                warnings=warnings,
                assets=assets,
            )
        finally:
            os.unlink(tmp_path)

    def _export_with_images(self, doc):
        """Exporta a Markdown con las imágenes escritas a un tempdir
        (`save_as_markdown` es el único método que soporta `artifacts_dir`
        — `export_to_markdown` no lo acepta, confirmado contra la versión
        real instalada) y las devuelve en base64 junto con el Markdown, con
        los paths absolutos reescritos a la convención `images/{filename}`.
        """
        settings = get_settings()
        warnings: list = []
        assets: list = []

        with tempfile.TemporaryDirectory() as tmp_dir:
            md_path = Path(tmp_dir) / "out.md"
            artifacts_dir = Path(tmp_dir) / "artifacts"
            doc.save_as_markdown(filename=md_path, artifacts_dir=artifacts_dir, image_mode=ImageRefMode.REFERENCED)

            markdown = md_path.read_text(encoding="utf-8")
            markdown = markdown.replace(str(artifacts_dir) + os.sep, _ASSET_PATH_PREFIX)

            image_files = sorted(artifacts_dir.glob("*")) if artifacts_dir.exists() else []
            for img_path in image_files:
                if len(assets) >= settings.max_images_per_document:
                    warnings.append(
                        f"Se alcanzó el máximo de {settings.max_images_per_document} imágenes por "
                        "documento — el resto se omitió (el Markdown las sigue referenciando)."
                    )
                    break
                data = img_path.read_bytes()
                if len(data) > settings.max_image_bytes:
                    warnings.append(
                        f"Imagen '{img_path.name}' omitida por tamaño "
                        f"({len(data)} bytes > {settings.max_image_bytes})."
                    )
                    continue
                assets.append(AssetItem(
                    filename=img_path.name,
                    content_type="image/png",
                    data_base64=base64.b64encode(data).decode("ascii"),
                ))

        return markdown, assets, warnings
