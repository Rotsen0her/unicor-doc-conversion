# Sprint 17-08-2026 — Servicio de conversión v1

Primer sprint de este proyecto, creado a partir de la Fase 0 (spike de motores) hecha en `backend_web_bot`.

## Features

1. [FEAT-CONVERSION-SERVICE-V1](./FEAT-CONVERSION-SERVICE-V1.md) ✅ — servicio FastAPI stateless, `POST /v1/convert`, Docling como motor por defecto.

## Estado general

Código completo, probado localmente (`pytest`) **y con Docker real**: `docker compose build` + `up` + una conversión real vía HTTP contra el contenedor, con el PDF crítico del spike (tabla de seguros) — resultado correcto confirmado de punta a punta, no solo en el venv.

En el camino se encontró y arregló un bug real de la imagen Docker (ver FEAT, sección Notas): `opencv-python` necesita libs de X11 que `python:3.11-slim` no trae por defecto, y eso solo se manifiesta en runtime al procesar el primer PDF, no en el build.

No comiteado a git todavía (no hay `git init` en este proyecto), no desplegado a un servidor real (sí probado local en Docker Desktop).

## Pendiente antes de conectar con backend_web_bot (Fase 2)

- `git init` + primer commit.
- Decidir hosting real (contenedor propio junto al backend, o aparte).
- Generar un `INTERNAL_API_KEY` real (hoy tiene el placeholder de `.env.example`) y ponerla en el `.env` de ambos proyectos.
- Backend RAG (`backend_web_bot`) todavía no tiene el modelo de documento nuevo (`source_md`, `index_status`, etc.) ni llama a este servicio — eso es la Fase 2, no arrancada.
