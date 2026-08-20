# unicor-doc-conversion

Servicio de conversión PDF/Office → Markdown para el RAG de
[`backend_web_bot`](../backend_web_bot). Stateless, sin base de datos, sin
caché, sin usuarios — recibe bytes, devuelve Markdown.

Ver `docs/17-08-2026/FEAT-CONVERSION-SERVICE-V1.md` para el detalle
completo, y `backend_web_bot/docs/17-08-2026/SPIKE-CONVERSION-ENGINE.md`
para por qué Docling es el motor por defecto (no MarkItDown).

## Desarrollo local

> ⚠️ **Windows: el venv NO puede vivir dentro de esta carpeta.** `torch`
> (dependencia de Docling) trae archivos de licencia con rutas anidadas
> tan largas que Windows falla con `WinError 206` si el venv está a más
> de ~4 niveles de profundidad. Usar una ruta corta fuera del proyecto,
> ej. `C:\Users\<tu_usuario>\.venvs\unicor-doc-conversion\`.

```bash
python -m venv C:\Users\<tu_usuario>\.venvs\unicor-doc-conversion
C:\Users\<tu_usuario>\.venvs\unicor-doc-conversion\Scripts\pip install -r requirements-dev.txt
copy .env.example .env   # y setear INTERNAL_API_KEY

C:\Users\<tu_usuario>\.venvs\unicor-doc-conversion\Scripts\uvicorn app.main:app --reload --port 8100
```

(En Linux/Docker no aplica esta limitación — el `Dockerfile` no la necesita.)

## Tests

```bash
# Rápido (sin Docling, sin descargar modelos)
C:\Users\<tu_usuario>\.venvs\unicor-doc-conversion\Scripts\pytest -m "not slow"

# Completo (primera vez descarga modelos de layout, puede tardar)
C:\Users\<tu_usuario>\.venvs\unicor-doc-conversion\Scripts\pytest
```

## Endpoints

- `POST /v1/convert` — `multipart/form-data`: `file`, `engine` (`auto`|`markitdown`|`docling`, default `auto`→`docling`), `ocr` (bool, default `true`), `extract_images` (bool, default `false`, no implementado todavía)
- `GET /v1/engines` — motores instalados y el default
- `GET /health`

Todo excepto `/health` requiere header `X-Internal-Key` (compartida con `backend_web_bot`, ver `.env.example`).

## Docker

```bash
docker build -t unicor-doc-conversion .
docker run -p 8100:8100 --env-file .env unicor-doc-conversion
```

## Licencia

[MIT](./LICENSE)
