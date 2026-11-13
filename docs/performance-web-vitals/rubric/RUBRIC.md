# Rúbrica — 023 auditoría de rendimiento

Fuente: `OFFICIAL_README.es.md` del syllabus `ai-eng-performance-web-vitals` @ `fd2da034894ba93ba738559280ccde074ab1d953`. Required = cuenta para el cierre. HITL_ENVIO_MIGUEL no resta.

| ID | Required | Criterio |
| --- | --- | --- |
| R01 | sí | Lighthouse del sitio corporativo en escritorio y móvil, al menos el inicio y otra vista. Las cuatro puntuaciones. |
| R02 | sí | Lighthouse del backoffice, al menos el panel o la vista con más elementos. Las cuatro puntuaciones. |
| R03 | sí | También el portal Next de `uis/` (el proceso que el ticket llama website), en producción. |
| R04 | sí | Antes y después contra producción (`build` + `start`). El sitio estático no usa `next dev`. |
| R05 | sí | Capturas comprometidas en `/audit/before/`. |
| R06 | sí | `AUDIT.md` con puntuaciones iniciales, problemas y causa raíz, y el análisis de refactor. |
| R07 | sí | Al menos dos duplicados identificados, con la abstracción propuesta. |
| R08 | sí | Al menos un componente o hook extraído e integrado. |
| R09 | sí | Correcciones de causas reales (recurso bloqueante, consola, reserva de layout). Sin reescritura de arquitectura. |
| R10 | sí | Un problema por commit y nueva medición de la misma URL. |
| R11 | sí | Lighthouse final en los dos frentes, capturas en `/audit/after/`. |
| R12 | sí | `REPORT.md` con cada corrección, la comparativa y qué impactó más. |
| R13 | sí | Mejora medible de al menos una puntuación por frente (sitio y backoffice). |
| R14 | sí | Las suites que ya estaban siguen en verde. |
| R15 | no | Si se usa una skill de agente, hay evidencia. La instalación es opcional. |
| R16 | HITL_ENVIO_MIGUEL | Subir el monorepo y compartir la URL según el instructor. |
| X01 | extra | Galería `/audit/` antes/después por frente, con puntuaciones anotadas. |
| X02 | extra | Hook o componente de optimización con su test. |
