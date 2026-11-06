# Rúbrica — 040 ai-eng-langgraph-agent-tools

Fuente: `OFFICIAL_README.md` / `OFFICIAL_README.es.md` del syllabus `ai-eng-langgraph-agent-tools` (sha `fd2da034894ba93ba738559280ccde074ab1d953`). `learn.json` describe el mismo alcance. No hay cláusula que prohíba herramientas de IA («No utilices herramientas de IA», «write each one yourself», «sin copiar»). Se ejecutó la solución.

Orden de autoridad: enunciado 4Geeks > SIGNAL. Hay UI en `/agente`, así que SIGNAL aplica a esa pantalla.

`required` = el enunciado lo exige para aceptar la entrega. `cuenta` = entra en el 100% implementable. `BLOCKED_HITL`, `HITL_MIGUEL`, `HITL_ENVIO_MIGUEL` y `NO_APLICA` no restan de ese 100%.

| ID | Required | Cuenta | Criterio |
| --- | --- | --- | --- |
| R01 | sí | sí | Se construye sobre el monorepo existente, desde la rama de la parte 1, no en un repositorio nuevo. |
| R02 | sí | sí | La tool de tickets tiene un contrato tipado de entrada y de salida con los campos públicos del gestor. |
| R03 | sí | sí | La tool lee el gestor de incidentes real (HTTP o en proceso). No hay un dataset paralelo ni respuestas hardcodeadas. |
| R04 | sí | sí | Si el servicio pide autenticación, la tool pasa credenciales desde el entorno o la petición, nunca un token escrito en el código. Si no hubiera auth, el PR lo diría. |
| R05 | sí | sí | La tool es de solo lectura. No crea, no actualiza y no borra incidencias. |
| R06 | sí | sí | El grafo tiene un nodo para la tool y una arista condicional que decide cuándo usarla en lugar del RAG o además del RAG. |
| R07 | sí | sí | Hay un timeout explícito y numérico (banda de ejemplo 3–5 s). Si el gestor no responde, el grafo no se queda colgado. |
| R08 | sí | sí | Hay una ruta de fallback verificable si la tool agota el tiempo, falla o el ticket no existe. La respuesta no inventa un estado. |
| R09 | no | no | Tool de inventario, solo si el gestor de inventario ya existe. Mismas reglas de contrato, timeout y fallback. |
| R10 | sí | sí | El agente decide solo, por el texto de la pregunta, si necesita el RAG, la tool o ambos. El usuario no nombra la fuente. |
| R11 | sí | sí | Cada tool hace una sola cosa. Tickets e inventario no comparten tool. |
| R12 | sí | sí | La traza de cada corrida muestra si se usó el RAG, la tool o ambos, y en qué orden. |
| R13 | sí | sí | Hay al menos dos evals nuevos de enrutamiento en `tests/pipelines/`: una pregunta de tool y una de RAG. El fallback es el tercero, opcional en el enunciado. |
| R14 | sí | sí | El código nuevo vive en `services/<agent-service>/` y los evals en `tests/pipelines/`. |
| L01 | sí | sí | La generación en vivo del RAG, anclada al briefing, con el modelo de 4Geeks. Un doble no es PASS. |
| L02 | sí | sí | La recuperación en vivo con el embedder de 4Geeks. Un doble o fastembed no es PASS. |
| D01 | sí | no | Enviar el proyecto al LMS o compartir el enlace de entrega con el instructor. |
| D02 | sí | no | Merge del PR a `main` después de la aprobación. El enunciado lo pide; esta ejecución no lo hace. |
| D03 | sí | sí | Pull Request propio, separado del de la parte 1, con la traza de la tool, la traza del RAG y la salida de los evals. |
| U01 | sí | sí | La pantalla usa los tokens SIGNAL, Arial/Helvetica, y estados idle, loading, success, empty y error. |
| U02 | sí | sí | Capturas reales a 390, 768 y 1280 px. |
| U03 | sí | sí | Vídeo corto real del recorrido, entre 5 y 10 s. |
| U04 | sí | sí | `prefers-reduced-motion` deja la pantalla en el estado final, sin animación. |
| U05 | sí | sí | Lockup oficial en el footer. Horizontal mínimo 400 px; en móvil, el apilado mínimo 280 px. Hash del horizontal verificado. |
| U06 | sí | sí | Lighthouse en el proceso de producción, tres corridas móvil y tres de escritorio, con la configuración pedida. |
| U07 | sí | sí | Skip link, etiquetas visibles, foco, `noindex`, axe sin hallazgos serious/critical. |
| U08 | sí | sí | Sin desbordamiento horizontal del documento en 390, 768 y 1280. |

Extras de excelencia (no sustituyen filas): página de trazas lado a lado (visible) y la batería de timeout, fallback y enrutamiento por encima del mínimo de dos evals (técnico). Están en `quality/EXCELLENCE_REVIEW.md`.
