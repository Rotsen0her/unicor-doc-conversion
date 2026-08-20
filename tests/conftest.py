import pytest


@pytest.fixture
def anyio_backend():
    return "asyncio"


def build_minimal_pdf(text: str = "Hello World") -> bytes:
    """PDF de una página válido, hecho a mano (xref con offsets reales) —
    mismo patrón que backend_web_bot/tests/test_pdf_processor.py."""
    content_stream = f"BT /F1 24 Tf 10 100 Td ({text}) Tj ET".encode()
    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/MediaBox[0 0 200 200]/Contents 5 0 R>>",
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
        b"<</Length " + str(len(content_stream)).encode() + b">>\nstream\n" + content_stream + b"\nendstream",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj".encode() + obj + b"endobj\n"

    xref_offset = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer<</Size {len(objects) + 1}/Root 1 0 R>>\nstartxref\n{xref_offset}\n%%EOF".encode()
    return bytes(out)


def build_pdf_with_image() -> bytes:
    """PDF de una página con una figura (rectángulo de color) y texto
    debajo — Docling la detecta como PictureItem separado del texto (ver
    spike de extract_images). Generado con Pillow, no con texto real
    seleccionable (por eso no se usa build_minimal_pdf acá).

    El texto NO es cosmético: confirmado en el spike que sin texto en la
    página, el layout model de Docling no segmenta el rectángulo como
    Picture (0 elementos detectados) — necesita contraste con otro
    contenido para clasificar la región como figura."""
    from io import BytesIO

    from PIL import Image, ImageDraw

    img = Image.new("RGB", (1000, 1400), color="white")
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 900, 500], fill=(200, 50, 50))
    draw.text((120, 550), "Texto de prueba debajo de la figura", fill="black")
    buf = BytesIO()
    img.save(buf, "PDF")
    return buf.getvalue()
