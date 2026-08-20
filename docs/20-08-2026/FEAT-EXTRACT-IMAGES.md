# Extracción de imágenes embebidas

**Estado:** ✅ | **Fecha:** 2026-08-20 | **Archivos clave:** `app/engines/docling_engine.py`, `app/engines/base.py`, `app/routes/convert.py`, `app/config.py`

## Contexto

`extract_images=true` en `POST /v1/convert` existía en el contrato desde v1
pero era un no-op documentado (`opts.generate_picture_images = False`
hardcodeado, con un comentario literal "Fase 4 del plan"). Esta feature lo
implementa: Docling detecta figuras/diagramas embebidos en un PDF y los
devuelve como assets en base64 junto con el Markdown.

## Cambios

### Spike (antes de escribir código productivo)

El plan asumía `doc.export_to_markdown(image_mode=REFERENCED,
artifacts_dir=...)`. Contra la versión real instalada (`docling==2.120.2`,
`docling-core==2.91.0`) eso **no existe** — `export_to_markdown()` no acepta
`artifacts_dir` (con `image_mode=REFERENCED` sin ese parámetro, produce
silenciosamente el mismo placeholder `<!-- image -->` que el modo default,
sin avisar del error). Solo `doc.save_as_markdown(filename=..., artifacts_dir=...)`
— que escribe a archivo, no devuelve string — soporta escribir las
imágenes a disco. Además, el path que deja en el Markdown es **absoluto**
(el de `artifacts_dir` tal cual), no relativo.

### `docling_engine.py`

- El converter ahora se cachea por `(do_ocr, extract_images)` en vez de
  solo `do_ocr` — antes la caché ignoraba el flag nuevo.
- `extract_images=true` solo tiene efecto en PDF (`generate_picture_images`
  vive en `PdfPipelineOptions`, que es lo único configurado en este
  servicio); para otros formatos se agrega un warning y se ignora, no se
  aborta la conversión.
- Cuando aplica: `save_as_markdown(artifacts_dir=<tempdir>,
  image_mode=REFERENCED)`, se leen los PNG del tempdir, se codifican en
  base64, y se reescribe en el Markdown el path absoluto por la convención
  `images/{filename}` (estable, no depende de dónde vive el tempdir de este
  proceso).
- Caps nuevos en `Settings` (`max_image_bytes=2MB`, `max_images_per_document=30`)
  — una imagen que excede el tamaño se omite con un warning (el Markdown
  sigue referenciándola, queda como link roto — decisión consciente, no se
  aborta toda la conversión por una imagen).

### Contrato HTTP

- `ConversionResult.assets` (antes `List[str]`, sin usar) pasa a
  `List[AssetItem]` (`filename`, `content_type`, `data_base64`) —
  `app/engines/base.py`.
- `ConvertResponse.assets` en la respuesta HTTP sigue el mismo cambio de
  tipo (`app/routes/convert.py`) — cambio de contrato interno seguro: el
  único consumidor es `backend_web_bot`, que se actualiza en el mismo
  sprint.

## Notas

- **Bug encontrado en el fixture de test, no en el código**: la primera
  versión de `build_pdf_with_image()` (solo un rectángulo de color, sin
  texto) daba `doc.pictures == 0` con Docling real, con o sin OCR — el
  layout model necesita algo de contraste con otro contenido en la página
  para segmentar una región como `Picture`. Corregido agregando texto
  debajo de la figura en el fixture; confirmado que entonces detecta 1
  imagen de forma consistente.
- `pillow` se agregó explícito a `requirements.txt` — ya llegaba transitivo
  vía `docling-slim`, pero el código ahora importa `PIL` directo (bueno
  tenerlo declarado, no depender de que otro paquete lo siga arrastrando).
- Validado con Docling real (no mockeado) vía tests `slow`:
  `test_convert_docling_extract_images` (assets poblados, Markdown con la
  convención `images/{filename}`, sin el path absoluto del tempdir) y
  `test_convert_docling_without_extract_images_has_no_assets` (comportamiento
  default sin cambios).
- Word/PowerPoint: no verificado si `generate_picture_images` aplica sin
  cambios adicionales (esos formatos no usan `PdfPipelineOptions`). Se deja
  como limitación conocida de v1, no bloqueante — ver
  [[FEAT-DOCUMENTOS-META-IMAGENES]] en `backend_web_bot` para el lado que sí
  se completó (PDF).
