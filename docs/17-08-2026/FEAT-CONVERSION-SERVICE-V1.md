# Servicio de conversión v1 (Fase 1 del plan)

**Estado:** ✅ | **Fecha:** 2026-08-17 | **Archivos clave:** `app/main.py`, `app/routes/convert.py`, `app/engines/`, `Dockerfile`

## Contexto

Fase 1 del plan "PDF → Markdown como fuente de verdad del RAG" (ver `backend_web_bot/docs/17-08-2026/`). Fase 0 (spike, mismo repo backend_web_bot) comparó MarkItDown vs Docling sobre 10 PDFs reales del producto y recomendó Docling como motor por defecto — esta fase construye el servicio HTTP alrededor de esa decisión.

Proyecto nuevo y separado de `backend_web_bot` a propósito — ver sección 1 del plan original (reuso, aislamiento del proceso de chat, Docling arrastra PyTorch, swap de motor sin tocar el contrato HTTP).

## Cambios

- Servicio FastAPI stateless: `POST /v1/convert` (multipart: `file`, `engine`, `ocr`, `extract_images`), `GET /v1/engines`, `GET /health`.
- Interfaz `ConversionEngine` (`app/engines/base.py`) — dos implementaciones: `DoclingEngine` (default) y `MarkItDownEngine` (disponible, no default).
- Auth por `X-Internal-Key` (mismo patrón que `verify_admin_key` de backend_web_bot, pero pensado para servicio-a-servicio, no para operaciones de plataforma humanas).
- Respuesta exacta al contrato del plan: `{markdown, engine_used, metadata: {pages, headings, tables, warnings}, assets}`.
- `engine=auto` resuelve directo a Docling — **no** se implementó la heurística "si tiene tabla → Docling" del plan original (ver spike para el porqué: no se justifica la complejidad para el volumen de este proyecto).
- `extract_images` aceptado en el contrato pero no implementado (es Fase 4) — si se pide, devuelve warning y `assets: []`.
- `ocr` mapea a `do_ocr` de Docling (OCR solo en regiones sin texto), no a `force_full_page_ocr` — se probó ese flag contra un PDF real con texto corrupto y no lo arregló, documentado en la skill del proyecto para no prometerlo de más.
- Dockerfile con `TORCHDYNAMO_DISABLE=1`/`TORCH_COMPILE_DISABLE=1` — necesarios en Windows (sin MSVC, Docling falla el 100% de las conversiones sin esto), defensivos en la imagen Linux.

## Notas

- **Validado con Docker real, no solo el venv local.** `docker compose build` + `up` + una conversión real vía HTTP contra el PDF de la póliza de seguro (el caso crítico del spike) — misma corrección de la tabla (`AUXILIO FUNERARIO | $ 3.300.000,00`) confirmada a través del servicio contenedorizado completo.
- **Bug real encontrado y arreglado en el Dockerfile:** `opencv-python` (dependencia transitiva de `docling_ibm_models` para reconstruir tablas) está compilado contra librerías gráficas de X11 aunque corra headless. `python:3.11-slim` no las trae → `ImportError: libxcb.so.1: cannot open shared object file` **en runtime, al procesar el primer PDF**, no al hacer `pip install` (por eso no se detectó hasta la prueba real en contenedor). Se agregó `apt-get install libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 libxcb1` antes del `pip install`.
- Primera conversión real dentro de un contenedor recién arrancado incluye la descarga de los modelos de layout/tabla desde HuggingFace (no vienen pre-horneados en la imagen) — ese request específico tarda más (~54s en la prueba real) que los siguientes, que reusan el `DocumentConverter` cacheado en memoria. Si esto importa para production, valdría la pena un healthcheck/warm-up que dispare una conversión dummy al arrancar, o hornear los modelos en la imagen — no implementado, es una mejora futura, no bloqueante para v1.

- No hay base de datos, caché ni auth de usuario en este proyecto — es intencional, ver skill `conversion-service` (`.claude/skills/conversion-service/SKILL.md`).
- `DocumentConverter` de Docling se cachea por combinación de opciones (`docling_engine.py`) — instanciarlo carga modelos de layout en memoria, hacerlo por request sería carísimo.
- Tests: `pytest -m "not slow"` corre rápido sin tocar Docling; el suite completo (`pytest`) incluye un test con Docling real, más lento y depende de que los modelos de layout estén cacheados localmente (se descargan la primera vez).
- **No desplegado todavía.** Falta: crear `INTERNAL_API_KEY` compartida con `backend_web_bot`, decidir dónde se hostea (mismo servidor, contenedor aparte — el `docker-compose.yml` de backend_web_bot no lo incluye todavía), y la Fase 2 (que `backend_web_bot` efectivamente lo llame).
- Próximo paso natural: Fase 2 — persistir `source_md` en `backend_web_bot` y que `upload_document` llame a este servicio en vez de ir directo a chunk+embed.
