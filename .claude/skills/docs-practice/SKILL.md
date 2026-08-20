---
name: docs-practice
description: >
  Buenas prácticas de documentación de desarrollo para zervio-backend. Cubre dos flujos:
  (A) crear la documentación de una feature/bug/fix nueva siguiendo la convención real
  de este repo (`docs/Domains/<Nicho>/DD-MM-AAAA/` con índice maestro `FEATURES.md`), y
  (B) auditar la documentación de referencia (la que describe el estado actual del
  proyecto) contra el código real para mantenerla al día — incluye verificar enlaces
  relativos rotos tras mover/archivar documentación. Usar cuando el usuario invoca
  "/docs-practice", pide "documenta esta feature/bug/fix", "registra este cambio en el
  changelog de desarrollo", "revisa si la documentación está actualizada", "revisa que
  los enlaces no estén rotos", "compara la doc de referencia con el código" o equivalente.
---

# Docs Practice — Documentación de desarrollo (zervio-backend)

Esta skill agrupa la práctica de documentación del proyecto en dos direcciones:

- **A. Nueva feature/bug/fix** — documentar hacia adelante, cuando se implementa algo.
- **B. Auditoría de referencia y enlaces** — mirar hacia atrás, verificar que lo que dice
  la doc "vigente" siga siendo cierto en el código, y que los enlaces relativos entre
  documentos sigan resolviendo (crítico después de mover/archivar carpetas, ver sección
  B.3 — pasó de verdad el 03-08-2026: una reorganización manual del usuario rompió 69
  enlaces relativos).

Esta es la versión real del proyecto — tiene prioridad sobre cualquier versión global
genérica de esta skill.

---

## Estructura real de `docs/` en este repo

```
docs/
├── module-dependencies.md       # único doc que vive FUERA de Domains/ — cross-nicho
└── Domains/
    └── Restaurant/               # nicho "restaurants" (único nicho real hoy)
        ├── FEATURES.md            # índice maestro, orden cronológico DESCENDENTE
        ├── reflexion-synapzys.md  # notas de referencia sueltas (sin fecha de sprint)
        ├── NOTA_*.md              # ídem — notas puntuales sin carpeta de sprint
        ├── module-dependencies.md # (no existe acá — ver arriba, vive en docs/ raíz)
        ├── DD-MM-AAAA/            # una carpeta por sprint/día de trabajo
        │   ├── CAMBIOS_IMPLEMENTADOS.md   # índice del sprint
        │   ├── FEAT-NOMBRE.md             # feature nueva
        │   ├── BUG-NOMBRE.md              # corrección de un comportamiento incorrecto
        │   ├── FIX-NOMBRE.md              # ajuste puntual menor
        │   └── Frontend/                  # contratos de endpoints nuevos/modificados
        │       └── FEAT-NOMBRE.md         # mismo nombre base que el doc principal
        ├── backlogs/               # planeación PREVIA a implementar (no "ya hecho")
        │   ├── ROADMAP_PARIDAD_FUDO.md    # índice maestro de backlogs
        │   ├── Corto/                     # en diseño/construcción activa — normalmente
        │   │                              # vacía: al completarse, el archivo se mueve
        │   │                              # a Archivado/ (ver B.3), no se borra
        │   ├── Mediano/                   # prioridad media, sin fecha objetivo aún
        │   ├── Futuro/                    # ideas de largo plazo, sin compromiso
        │   └── pendiente/                 # bloqueado o esperando decisión — puede
        │       │                         # incluir sub-features ya con nombre FEAT-
        │       └── prerequisitos-skills/  # progreso real de OTRAS skills del repo
        │                                  # (arquitectura-modular.md,
        │                                  # multitenancy-buenas-practicas.md, etc.)
        ├── Archivado/              # backlogs completados/descartados y docs históricos
        │   └── DD-MM-AAAA/                # también puede tener sub-fechas propias
        ├── Desarrollo/             # guías de entorno (DESARROLLO_LOCAL.md, FLUJO_GIT.md,
        │                          # colección Postman) — no ligado a un sprint
        └── superadmin/             # pendientes específicos del panel super-admin
```

**Diferencias clave vs. una convención genérica:**
- La raíz no es `docs/` ni `docs/API/` — es `docs/Domains/<Nicho>/` (hoy solo
  `Restaurant`; si se activa un segundo nicho de negocio, ver skill
  `arquitectura-modular`, tendría su propia raíz `docs/Domains/<OtroNicho>/`).
- `docs/module-dependencies.md` es la única excepción — vive en la raíz de `docs/`
  porque es cross-nicho por diseño (mapea dependencias entre módulos de
  `app/domains/<nicho>/`, ver skill `mapa-dependencias-modulos`).
- No hay carpeta `Referencia/` separada — las notas "vigentes" sin fecha de sprint
  (`reflexion-synapzys.md`, `NOTA_*.md`) viven sueltas en la raíz de
  `docs/Domains/Restaurant/`.
- `backlogs/` es planeación **antes** de implementar (roadmap, decisiones de diseño);
  las carpetas `DD-MM-AAAA/` son el registro **después** de implementar. No confundir
  un backlog con un `FEAT-`: si el archivo describe qué se *va a* construir y por qué,
  es un backlog (`backlogs/{Corto,Mediano,Futuro,pendiente}/`); si describe qué se
  construyó, es un `FEAT-`/`FIX-`/`BUG-` en una carpeta `DD-MM-AAAA/`.

---

## A. Documentar una feature/bug/fix nueva

### 1. Confirmar la raíz

Para este repo la raíz ya está fijada: `docs/Domains/Restaurant/`, índice maestro
`FEATURES.md`. No propongas una estructura nueva ni preguntes — ya existe y está en uso
activo. (Si en el futuro se activa un segundo nicho, ver skill `arquitectura-modular`
para cuándo corresponde crear `docs/Domains/<OtroNicho>/` con su propio `FEATURES.md`.)

### 2. Prefijos y estados

| Prefijo | Cuándo usarlo |
|---|---|
| `FEAT-` | Feature nueva |
| `BUG-` | Corrección de un comportamiento incorrecto |
| `FIX-` | Ajuste puntual menor |

| Estado | Significado |
|---|---|
| ✅ | Implementado |
| ⏳ / 📋 Pendiente | Pendiente |
| 🚫 | Bloqueado (va en `backlogs/pendiente/`) |
| 🔄 | Reemplazado/Superado |
| 🟡 | Parcial (ver el propio archivo para el detalle) |

### 3. Plantilla de archivo individual

```markdown
# <Título descriptivo>

**Estado:** ✅ | **Fecha:** DD-MM-AAAA | **Archivos clave:** ruta/archivo1.py, ruta/archivo2.py

## Contexto
<Por qué se hace este cambio, qué problema resuelve>

## Cambios
<Qué se modificó/añadió, a alto nivel>

## Notas
<Decisiones, casos borde, pendientes>
```

Para un `FIX-` puntual, la plantilla puede simplificarse a Contexto/Diagnóstico/Fix/
Validado (ver `FIX-WEBSOCKET-SEGUIMIENTO-PEDIDO-COCINA.md` como ejemplo real) — no es
obligatorio forzar las 3 secciones si el cambio es chico.

### 4. Pasos

1. Calcular la carpeta de hoy `docs/Domains/Restaurant/DD-MM-AAAA/`. Si no existe,
   créala junto con `CAMBIOS_IMPLEMENTADOS.md` (índice con el título del sprint,
   inicialmente vacío).
2. Determinar el prefijo (`FEAT-`/`BUG-`/`FIX-`) según lo que describa el usuario; si
   no es obvio, preguntar.
3. Crear `<PREFIJO>-<NOMBRE>.md` con la plantilla de la sección 3. Si está bloqueada,
   créala en `backlogs/pendiente/` con `**Estado:** 🚫` y una línea explicando el
   bloqueo — enlázala igual desde `FEATURES.md`.
4. Añadir una entrada en `CAMBIOS_IMPLEMENTADOS.md` del sprint, enlazando al archivo
   nuevo con ruta relativa correcta (ver checklist de enlaces en B.3 antes de dar por
   terminado).
5. Añadir/actualizar la sección del sprint en `FEATURES.md` (siempre arriba del todo,
   orden cronológico descendente) con el enlace a `CAMBIOS_IMPLEMENTADOS.md` y la nueva
   entrada con su estado.
6. Marcar `**Estado: ✅**` solo cuando la implementación esté realmente terminada, no al
   crear el archivo.
7. Si la feature/fix crea o modifica endpoints, crear además
   `DD-MM-AAAA/Frontend/<PREFIJO>-<NOMBRE>.md` (mismo nombre base que el doc principal)
   con el contrato para consumo desde el frontend: método + ruta, auth/rol requerido,
   body de request, body de response (con ejemplo — JSON real, no solo tipos), errores
   esperados y un ejemplo de uso (ej. snippet TypeScript). Enlazarlo desde el archivo
   individual de la feature con "Contrato de endpoints en
   [Frontend/<PREFIJO>-<NOMBRE>.md](Frontend/<PREFIJO>-<NOMBRE>.md)." — ver
   `24-07-2026/FEAT-ADICIONES-PRODUCTO.md` y su `Frontend/` como ejemplo real.
8. Si el fix corrige o completa una afirmación desactualizada en un doc `Frontend/`
   existente (de otra fecha, no solo el de hoy), corrígela ahí también en vez de dejar
   la corrección solo en el doc nuevo — ver B.2, "código tiene algo nuevo que el doc no
   cubre" aplica igual a contratos de frontend ya publicados.
9. Si el hallazgo justifica cerrar/actualizar un backlog relacionado en
   `backlogs/{Corto,Mediano,Futuro,pendiente}/`, añadir ahí una sección "Actualización
   DD-MM-AAAA" (no reescribir el contenido original — es historial útil, ver ejemplo en
   `Archivado/BACKLOG_VARIANTES_PRODUCTO.md`) enlazando al nuevo `FEAT-`/`FIX-`.
10. No archivar documentación existente como parte de este flujo — el archivado
    (mover un backlog completado de `backlogs/Corto/` a `Archivado/`) es una tarea
    aparte y manual; si se hace, seguir el checklist de la sección B.3.

---

## B. Auditar documentación de referencia, vigencia y enlaces

### B.1 Identificar el alcance

1. Revisa `docs/Domains/Restaurant/FEATURES.md` y `backlogs/ROADMAP_PARIDAD_FUDO.md`
   para ubicar qué documentos aplican.
2. Si el usuario pidió un documento o carpeta específica, audita solo eso.
3. Si no especificó, pregunta qué quiere auditar (auditar todo de golpe genera ruido).

### B.2 Para cada documento — drift de contenido vs. código

1. Lee el documento completo.
2. Extrae **afirmaciones verificables**: endpoints y métodos HTTP, nombres de
   campos/schemas, reglas de negocio (fórmulas, umbrales, constantes), variables de
   entorno, nombres de tablas/columnas, rutas de archivo citadas, nombres de
   funciones/clases.
3. Busca el código correspondiente (routers, modelos, servicios, schemas) con
   Grep/Glob — no asumas que las rutas citadas en el doc siguen existiendo.
4. Compara cada afirmación:
   - **Coincide** → no tocar.
   - **Desactualizado** (campo renombrado, endpoint movido, regla cambiada, ruta de
     archivo que ya no existe) → corregir, preferiblemente con una nota "Actualización
     DD-MM-AAAA" que preserve el texto original con contexto (no borrar sin más — ver
     ejemplo real en `26-07-2026/Frontend/FEAT-ESTADO-PUBLICO-PEDIDO.md`, sección
     "Actualización 2026-08-03").
   - **Código tiene algo nuevo que el doc no cubre** → anotar como posible adición
     (preguntar antes de expandir mucho el doc si es un cambio grande).
   - **Ambiguo** (intención de negocio no verificable solo leyendo código) → no tocar.

### B.3 Verificar enlaces relativos rotos (obligatorio tras mover/archivar docs)

Este proyecto reorganiza su documentación manualmente de vez en cuando (mover carpetas
`DD-MM-AAAA/`, archivar backlogs completados a `Archivado/`, aplanar una jerarquía). Los
enlaces `[texto](ruta/relativa.md)` **no se actualizan solos** cuando eso pasa — la
reorganización del 03-08-2026 rompió 69 enlaces de una sola vez, principalmente por
estos 3 patrones recurrentes:

1. **Profundidad de anidamiento cambiada**: un archivo que antes vivía en
   `docs/Domains/Restaurant/pendiente/X.md` y ahora vive en
   `docs/Domains/Restaurant/backlogs/pendiente/X.md` necesita un `../` extra en cada
   enlace relativo que sale de esa carpeta — y los archivos que enlazaban *hacia* él
   necesitan agregar el segmento `backlogs/` que faltaba.
2. **El archivo destino se movió a otro lado** (ej. de `backlogs/Corto/` a
   `Archivado/` al completarse) — el enlace sigue apuntando a la ruta vieja aunque la
   estructura alrededor no haya cambiado.
3. **Nombre de carpeta con typo/variante** (`Archivados` plural vs. `Archivado`
   singular real, o mayúscula/minúscula) — consistencia de nombre, no solo de ruta.

**Cómo verificar (script rápido, no hay tooling dedicado en el repo):**

```python
import re, os, urllib.parse
DOCS = "docs"  # o la subcarpeta específica si el alcance es menor
LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
for dirpath, _, filenames in os.walk(DOCS):
    for fn in filenames:
        if not fn.lower().endswith(".md"):
            continue
        fpath = os.path.join(dirpath, fn)
        content = open(fpath, encoding="utf-8", errors="replace").read()
        for m in LINK_RE.finditer(content):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = urllib.parse.unquote(target.split("#", 1)[0].split(' "')[0])
            if path_part and not os.path.exists(os.path.normpath(os.path.join(dirpath, path_part))):
                print(f"{os.path.relpath(fpath, DOCS)} -> {target}")
```

Para cada enlace roto reportado:
1. Busca el **basename** del archivo destino en todo `docs/` (Glob `**/<basename>`).
2. Si hay **un solo match**, es mecánico: recalcula la ruta relativa correcta desde el
   archivo origen y corrígela.
3. Si hay **más de un match** (típico: el mismo nombre existe tanto en
   `DD-MM-AAAA/FEAT-X.md` como en `DD-MM-AAAA/Frontend/FEAT-X.md`), **lee el contexto
   del enlace roto** (el texto alrededor, no solo el href) para decidir cuál de los dos
   es el destino correcto — no asumas, la mayoría de las veces el propio texto del link
   ya lo dice (ej. "ver docs/28-07-2026/Frontend/FEAT-X.md" es inequívoco).
4. Si el destino **ya no existe en ningún lado** (basename con cero matches), es
   probablemente un archivo eliminado hace tiempo en un doc archivado/histórico — no
   inventes un destino nuevo. Repórtalo como enlace muerto sin solución mecánica y
   déjalo, salvo que el usuario pida investigar más a fondo qué pasó con ese archivo.
5. Aplica las correcciones y vuelve a correr el script para confirmar 0 rotos (aparte
   de los del punto 4, que quedan documentados como conocidos).

No modifiques código como parte de esta skill — solo documentación. Si detectas un bug
real durante la auditoría, repórtalo aparte; no lo arregles en silencio acá.
