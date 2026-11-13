# SOURCE — 025 telemetría

Fecha de lectura: 2026-11-12.

## Enunciado

Syllabus `ai-eng-telemetry-plan` @ `fd2da034894ba93ba738559280ccde074ab1d953`.
Slug LMS `ai-eng-telemetry-plan`.

| Archivo | SHA256 | Contra PROVENANCE |
| --- | --- | --- |
| `source/OFFICIAL_README.md` | `a742b60ff0108eab8455af9498e9636e2e1059b0912fef1fe10f29b956349b77` | Coincide |
| `source/OFFICIAL_README.es.md` | `ba3e2ad246cb250d45e236bb8b668f5b9739cc063d6ef9d8ef085fbca8a3c588` | Coincide |
| `source/learn.json` | `6c4786a7fcee2bbb8703c6595502b43736e0baf82d19717293eb78f510130c4b` | Coincide |

## Briefing de Nexova

El enunciado manda leer el briefing de `content/contexts/06-telemetry-data-pipelines/telemetry` antes de nombrar métricas.

| Archivo | SHA256 |
| --- | --- |
| `source/nexova-BRIEFING.md` | `b9aee8a9dfde725d75d695f08f1027e14d635edeb6782f23d884987c0b72e097` |
| `source/nexova-BRIEFING.es.md` | `c0d3e6db92867fdb4575d5e993cebce5e95982e7cc76c8c6dd486254aa45afa8` |

Los cinco `event_type` coinciden en los dos idiomas. Los ejemplos de `programme_id` no: inglés `b2b-sales` y `basic-leadership`; español `ventas-b2b` y `liderazgo-basico`. El plan no asigna ninguno a un SKU.

## Cláusula anti-IA

Se buscó en los dos README, en `learn.json` y en los dos briefings: «No utilices herramientas de IA», «Do not use AI tools», «write each one yourself», «escrito por ti», «sin copiar», «no uses ChatGPT». No aparece.

## Autoridad

Enunciado 4Geeks, luego el briefing de telemetría de Nexova, luego este encargo. El enunciado pide el PR contra `main` y el merge. Este encargo pide la rama `feature/telemetry-plan` contra `feature/caching-optimisation` (head `3be83a0`, PR #26), sin merge y sin LMS. Se sigue el encargo de la ejecución y se deja el conflicto escrito.

SIGNAL se leyó. No hay UI nueva. El lockup no se copia. `reference-code/` no se usa.

## Base de código

`feature/caching-optimisation` @ `3be83a02252f2de46e57e67b52194bd70eff9d7d`. Rama de trabajo: `feature/telemetry-plan`. Sin merge. Sin force-push. Sin envío al LMS.
