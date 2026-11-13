# SOURCE — 027 almacenamiento de telemetría

Fecha de lectura: 2026-11-12.

## Enunciado

Syllabus `ai-eng-telemetry-storage` @ `fd2da034894ba93ba738559280ccde074ab1d953`.
Slug LMS `ai-eng-telemetry-storage`.

| Archivo | SHA256 | Contra PROVENANCE |
| --- | --- | --- |
| `source/OFFICIAL_README.md` | `a81f51aa28bf769c030b822a9e6c077e6529784c4b7ae05b23f594c02c4ab15d` | Coincide |
| `source/OFFICIAL_README.es.md` | `76263bdd1160bb90022417b6db0fca91a1eaa683840f5a7e0c239226a417abe4` | Coincide |
| `source/learn.json` | `ba75201ac75218417263b55531180670199ae2472a12fd010054605a5641a807` | Coincide |

## Contrato de la fase anterior

`docs/telemetry/telemetry-plan.md` y `docs/telemetry/event-schemas.json`.
La base de trabajo es `feature/telemetry-capture` @ `631e01a1fb640f7c0e2a894c2d4ee70f9e03cb8f` (PR #30).
Durante la ejecución esa rama avanzó a `6cc066f7bf61f42dbb7b32941aa166799f29e770`: el plan cuenta 20 eventos y el `$id` del esquema pasa a `event-envelope-1.1.0.json`. Se integró con un merge normal. El código abre `docs/telemetry/event-schemas.json` y no usa el `$id` como ruta.

## Briefing

Las dimensiones que el plan guarda en las órdenes son `office`, `product_category`, `programme_id` y `currency`. `programme_id` sigue en `unassigned` cuando el activo no tiene programa. No se inventan `b2b-sales` ni `liderazgo-basico`.

## Cláusula anti-IA

Se buscó en los dos README y en `learn.json`: «No utilices herramientas de IA», «Do not use AI tools», «write each one yourself», «escrito por ti». No aparece.

## Autoridad

El enunciado pide el PR contra `main`, el título `feat: telemetry event storage`, la tabla creada en Supabase y el merge tras la aprobación. Este encargo pide la rama `feature/telemetry-storage` contra `feature/telemetry-capture`, Postgres local para el bulk insert, y HITL cuando el criterio exige Supabase o el backoffice desplegado. No hay merge a `main`, ni force-push, ni envío al LMS, ni deploy. El conflicto queda escrito en la rúbrica.

SIGNAL se leyó. Esta entrega no toca UI. El lockup no se aplica.
