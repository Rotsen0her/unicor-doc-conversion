# Sprint 20-08-2026 — Extracción de imágenes (Fase 4 parte 2)

Continuación de la Fase 4 de `backend_web_bot` (historial de versiones,
sprint 19-08-2026) — la otra mitad diferida del plan original.

## Features

1. [FEAT-EXTRACT-IMAGES](./FEAT-EXTRACT-IMAGES.md) ✅ — `extract_images=true` en `POST /v1/convert` ahora funciona de verdad (antes era un no-op documentado).

## Estado general

Empezó con un spike corto (mismo criterio que Fase 0) porque el plan
original asumía un método de la API de Docling que no existe en la versión
instalada (`export_to_markdown(artifacts_dir=...)`) — se confirmó contra
Docling real que solo `save_as_markdown(artifacts_dir=...)` acepta ese
parámetro, y que el path que deja en el Markdown es absoluto, no relativo.

Validado con Docling real (no mockeado): `doc.pictures` detecta
correctamente una figura de prueba, `save_as_markdown(image_mode=REFERENCED)`
escribe el PNG a disco, y el servicio reescribe el path absoluto a la
convención `images/{filename}` antes de responder. Encontrado en el camino:
el fixture de test inicial (solo una figura, sin texto) daba `0` imágenes
detectadas — Docling necesita contraste con otro contenido en la página
para segmentar una región como `Picture`; el fixture real de los tests
tiene texto debajo de la figura.

9/9 tests pasan (2 nuevos, `slow`, con Docling real).

Comiteado, pusheado y desplegado en producción.

## Pendiente

- Extracción de imágenes en Word/PowerPoint (Excel/CSV no aplica) —
  `generate_picture_images` solo está cableado para el pipeline de PDF en
  este servicio; no verificado si aplica a los otros formatos sin cambios
  adicionales. Limitación conocida de v1, no bloqueante.
