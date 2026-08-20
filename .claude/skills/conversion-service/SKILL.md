---
name: conversion-service
description: >
  Patrones reales de unicor-doc-conversion — servicio FastAPI stateless
  (sin DB, sin Redis, sin JWT de usuario) que convierte PDF/Office a
  Markdown con Docling (default) o MarkItDown. Usar cuando: (1) se agrega
  un motor de conversión nuevo (interfaz app/engines/base.py), (2) se toca
  el contrato de POST /v1/convert, (3) se debuggea por qué Docling es
  lento o falla en Windows (torch.compile), (4) se decide si algo va acá
  o en backend_web_bot (RAG).
---

# unicor-doc-conversion — patrones reales

Este servicio es deliberadamente distinto al resto de proyectos de
`ProyectosProgramacion/` (zervio-backend, synapzys-backend,
backend_web_bot): **no tiene base de datos, no tiene caché, no tiene
usuarios.** Es un conversor puro — recibe bytes, devuelve Markdown. Si
estás por agregar un modelo SQLAlchemy o una tabla acá, para: no es ese
tipo de proyecto. Si necesitas persistir algo (el `.md` editado, el
`source_md` de un documento), eso vive en `backend_web_bot`, no acá.

## Por qué existe separado del backend RAG

Ver `backend_web_bot/docs/17-08-2026/SPIKE-CONVERSION-ENGINE.md` para la
investigación completa. Resumen: Docling arrastra PyTorch — no debe vivir
en el mismo proceso que sirve el chat. El backend RAG llama acá por HTTP
interno (`X-Internal-Key`, nunca JWT de usuario), nunca al revés.

## Motor por defecto: Docling, no MarkItDown

`app/engines/__init__.py: DEFAULT_ENGINE = "docling"`. Es una decisión
tomada con evidencia sobre 10 PDFs reales del producto (no genéricos), no
la heurística `auto` (tabla→Docling, si no→MarkItDown) que proponía el
plan original — para el volumen de este proyecto, correr un detector de
tablas antes de convertir costaría casi lo mismo que convertir directo
con Docling. Si el volumen crece mucho, revisar esta decisión — no antes.

## Interfaz de motor (`app/engines/base.py`)

```python
class ConversionEngine(Protocol):
    name: str
    def convert(self, file_bytes: bytes, filename: str, *, ocr: bool, extract_images: bool) -> ConversionResult: ...
```

Agregar un motor nuevo (ej. Marker) = una clase nueva implementando esto +
una línea en `ENGINES` (`app/engines/__init__.py`). El HTTP (`app/routes/convert.py`)
nunca importa un vendor directamente.

## Docling en Windows: `torch.compile` rompe sin MSVC

Docling intenta compilar su modelo de layout con `torch.compile`/Inductor,
que en Windows necesita `cl.exe` (Visual Studio Build Tools). Sin eso,
**falla el 100% de las conversiones** con `InvalidCxxCompiler`. Se
resuelve con variables de entorno, sin instalar Visual Studio — ya seteadas
por defecto en `app/engines/docling_engine.py` y en el `Dockerfile`:

```python
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("TORCH_COMPILE_DISABLE", "1")
```

En la imagen Docker (Linux) probablemente no haría falta — se deja como
defensivo, para no depender de que la imagen base tenga gcc/g++.

## `ocr=true` NO es un fix mágico para texto corrupto

Se probó `force_full_page_ocr=True` contra un PDF real con la capa de
texto corrupta (fuente mal subseteada en el original — "C6RDOBA" en vez
de "CÓRDOBA") y **no lo arregló**. El parámetro `ocr` de este servicio
mapea a `do_ocr` (correr OCR solo en regiones sin texto extraíble) — no a
`force_full_page_ocr`. Para documentos con texto ya corrupto en el
original, la única corrección real es manual, en el editor del panel
(Fase 3 del plan) — no prometas en el contrato HTTP algo que el spike ya
demostró que no funciona.

## `extract_images` todavía no hace nada

Aceptado en el contrato de `POST /v1/convert` por compatibilidad con el
plan original, pero **no implementado** — `assets` siempre vuelve `[]` y
se agrega un warning si el caller lo pide. Extraer imágenes a storage y
referenciarlas en el `.md` es explícitamente Fase 4 del plan, no v1.
No lo implementes por adelantado sin que backend_web_bot ya tenga dónde
guardarlas (su `storage_service.py` de Spaces, reusable para esto cuando
llegue el momento).

## Caché de `DocumentConverter`

`docling_engine.py` cachea el `DocumentConverter` por combinación de
opciones (`_converter_cache`) — instanciarlo carga los modelos de layout
en memoria, hacerlo por request sería carísimo. Si agregas una opción
nueva al pipeline, asegúrate de que entre en la key del caché o vas a
reusar un converter con las opciones equivocadas.

## `cv2` necesita libs de X11 aunque corra headless — falla en runtime, no en el build

`opencv-python` (dependencia transitiva de `docling_ibm_models`, usada para
reconstruir tablas) está compilado contra librerías gráficas de X11.
`python:3.11-slim` no las trae. El síntoma es engañoso: `pip install`
**funciona bien**, la imagen se construye sin errores — recién falla al
procesar el primer PDF real, con `ImportError: libxcb.so.1: cannot open
shared object file`. El `Dockerfile` ya instala lo necesario
(`apt-get install libgl1 libglib2.0-0 libsm6 libxext6 libxrender1
libxcb1` antes del `pip install`) — si algún día se cambia la imagen base
o se quita esa capa, este es el primer lugar a mirar si "compiló bien pero
truena en el primer request".

## Tests: `docling` es lento, márcalo `slow`

La primera conversión con Docling descarga modelos de HuggingFace/RapidOCR
si no están cacheados (`~/.cache/huggingface`, `~/.cache/docling` según
versión). Los tests que usan el engine `docling` van con
`@pytest.mark.slow` (`pytest.ini`) — correr `pytest -m "not slow"` en un
entorno sin esos modelos cacheados para no bloquear el CI en la primera
corrida.
