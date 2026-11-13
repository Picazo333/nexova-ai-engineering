# SOURCE — 026 captura de telemetría

Fecha de lectura: 2026-11-12.

## Enunciado

Syllabus `ai-eng-telemetry-capture` @ `fd2da034894ba93ba738559280ccde074ab1d953`.
Slug LMS `ai-eng-telemetry-capture`.

| Archivo | SHA256 | Contra PROVENANCE |
| --- | --- | --- |
| `source/OFFICIAL_README.md` | `d4c6d2b76c7f4b580e04c568e0fa8a6ec64bbac0dcfd54e8e0cad4113cb67159` | Coincide |
| `source/OFFICIAL_README.es.md` | `493fc02d6c75d3b4ed234cd363bafe2ad643fe2ae7a95dbabb01773358cbe514` | Coincide |
| `source/learn.json` | `5eeef669427526dc6ff8fa66b76346b183d32ae90f5f2d84be5095aa576cdb65` | Coincide |

## Contrato de la fase anterior

`docs/telemetry/telemetry-plan.md` y `docs/telemetry/event-schemas.json` partieron de `feature/telemetry-plan` @ `da3525b9cf1e6fedfd158f2200eb1371227261e1`. En 1.1.0 se añade `web_vital_recorded` sin cambiar las claves de los eventos anteriores. El `$id` del esquema es `event-envelope-1.1.0.json`.

## Briefing

El plan ya fijó los cinco `event_type` obligatorios del briefing de Nexova. Esta entrega no renombra métricas ni inventa programas (`b2b-sales`, `liderazgo-basico`). `programme_id` sigue en `unassigned` y va acompañado de `catalogue_gap_recorded`.

## Cláusula anti-IA

Se buscó en los dos README y en `learn.json`: «No utilices herramientas de IA», «Do not use AI tools», «write each one yourself», «escrito por ti». No aparece.

## Autoridad

El enunciado pide el PR contra `main`, el título `feat: telemetry event capture` y el merge. Este encargo pide la rama `feature/telemetry-capture` contra `feature/telemetry-plan` (head `da3525b`, PR #29), sin merge, sin force-push y sin LMS. Se sigue el encargo y se conserva el título del enunciado. El conflicto queda escrito.

El enunciado también pide, como actividad adicional, eventos de Web Vitals. El mismo enunciado dice que el esquema aprobado es el contrato y que un `event_type` fuera de ese catálogo no se acepta. No se añade un evento nuevo. `page_load_recorded` es la métrica de carga del plan.

## Base de código

`feature/telemetry-plan` @ `da3525b9cf1e6fedfd158f2200eb1371227261e1`. Rama de trabajo: `feature/telemetry-capture`. Sin merge. Sin force-push. Sin envío al LMS.

SIGNAL se leyó. El backoffice ya tenía tokens y lockup. El indicador de desarrollo usa esos tokens. No se regeneran SVG.
