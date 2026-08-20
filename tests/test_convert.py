"""
Tests del endpoint /v1/convert. El engine markitdown corre siempre
(rápido, sin descargas). El de docling se marca `slow` porque la primera
vez descarga modelos de layout — correr con `pytest -m "not slow"` para
saltarlo en un entorno sin esos modelos cacheados.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import build_minimal_pdf

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_convert_requires_auth(monkeypatch):
    from app.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("INTERNAL_API_KEY", "secreto-de-prueba")
    get_settings.cache_clear()

    pdf = build_minimal_pdf()
    resp = client.post(
        "/v1/convert",
        files={"file": ("test.pdf", pdf, "application/pdf")},
        data={"engine": "markitdown"},
    )
    assert resp.status_code == 401
    get_settings.cache_clear()


def test_convert_rejects_empty_file():
    resp = client.post(
        "/v1/convert",
        files={"file": ("empty.pdf", b"", "application/pdf")},
        data={"engine": "markitdown"},
    )
    assert resp.status_code == 422


def test_convert_with_markitdown():
    """
    No se exige que el texto aparezca literal en el markdown: MarkItDown usa
    pdfminer por debajo, que es más estricto que pypdf con la estructura
    mínima de build_minimal_pdf() y a veces no extrae nada de ella (no es un
    bug de este servicio — ver el spike para la fragilidad real de MarkItDown
    contra PDFs reales, no solo sintéticos). Lo que valida este test es el
    cableado HTTP: status, shape de la respuesta, motor correcto.
    """
    pdf = build_minimal_pdf("Reglamento de matricula")
    resp = client.post(
        "/v1/convert",
        files={"file": ("reglamento.pdf", pdf, "application/pdf")},
        data={"engine": "markitdown"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["engine_used"] == "markitdown"
    assert isinstance(body["markdown"], str)
    assert body["assets"] == []


def test_convert_unknown_engine_rejected():
    pdf = build_minimal_pdf()
    resp = client.post(
        "/v1/convert",
        files={"file": ("test.pdf", pdf, "application/pdf")},
        data={"engine": "marker"},
    )
    assert resp.status_code == 422


def test_list_engines():
    resp = client.get("/v1/engines")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body["engines"]) == {"docling", "markitdown"}
    assert body["default"] == "docling"


@pytest.mark.slow
def test_convert_with_docling_default_engine():
    """
    engine=auto debe resolver a docling (el default), no a markitdown.
    No se compara texto exacto: Docling reconstruye espaciado desde la
    posición de los glifos en el PDF y a veces mete espacios dobles entre
    palabras (visto también en los PDFs reales del spike) — el contrato
    real que importa acá es que markdown no viene vacío y el motor usado
    es el correcto, no una comparación carácter a carácter.
    """
    pdf = build_minimal_pdf("Contenido de prueba para docling")
    resp = client.post(
        "/v1/convert",
        files={"file": ("prueba.pdf", pdf, "application/pdf")},
        data={"engine": "auto"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["engine_used"] == "docling"
    assert len(body["markdown"].strip()) > 0
    assert "contenido" in body["markdown"].lower()
