"""
Motor MarkItDown — rápido, pero NO es el default de este servicio (ver
docs/17-08-2026/SPIKE-CONVERSION-ENGINE.md en backend_web_bot: 0 headings
detectados en 10/10 PDFs reales, y rompe tablas con datos monetarios en
listas desconectadas). Se deja disponible para casos donde la velocidad
importa más que la fidelidad, o para comparar manualmente.
"""
import io
import time

from markitdown import MarkItDown

from app.engines.base import ConversionResult

_md = MarkItDown()


class MarkItDownEngine:
    name = "markitdown"

    def convert(self, file_bytes: bytes, filename: str, *, ocr: bool, extract_images: bool) -> ConversionResult:
        warnings = ["MarkItDown no reconoce headings de forma confiable — ver spike."]
        if extract_images:
            warnings.append("extract_images no soportado con MarkItDown en este servicio.")

        t0 = time.time()
        result = _md.convert_stream(io.BytesIO(file_bytes), file_extension=_extension(filename))
        elapsed = time.time() - t0

        markdown = result.text_content
        n_headings = sum(1 for line in markdown.splitlines() if line.strip().startswith("#"))
        n_tables = markdown.count("|---") + markdown.count("| ---")

        if elapsed > 5:
            warnings.append(f"Conversión más lenta de lo esperado para MarkItDown ({elapsed:.1f}s).")

        return ConversionResult(
            markdown=markdown,
            engine_used=self.name,
            pages=0,  # MarkItDown no expone conteo de páginas
            headings=n_headings,
            tables=n_tables,
            warnings=warnings,
            assets=[],
        )


def _extension(filename: str) -> str:
    if "." in filename:
        return "." + filename.rsplit(".", 1)[-1]
    return ".pdf"
