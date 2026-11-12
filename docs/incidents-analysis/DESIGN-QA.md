# QA de diseño — backoffice de incidencias

Build: commit `d7952db5a37fffeec3f98dedf9a8ec20da5cb95b`.
Entorno: Chrome en Linux, Playwright headless para anchos fijos y una ventana de escritorio para el vídeo. Firefox y Safari no están instalados.

| ID | Regla | Ruta / estado / viewport | Resultado | Evidencia | Defecto |
| --- | --- | --- | --- | --- | --- |
| QA-01 | pytest | motor, CLI, API, hashes | PASS | 24 passed | |
| QA-02 | Hashes SIGNAL | tokens y lockups | PASS | `test_signal_asset_hashes` | |
| QA-03 | CSS/JS gzip | suma de hojas y scripts | PASS | `test_front_end_transfer_budgets` | |
| QA-04 | Overflow | idle 320/390/768/1024/1280/1440 | PASS | `report.json` overflow 0 | |
| QA-05 | Overflow | success 320/390/768/1280 | PASS | `report.json` | |
| QA-06 | Capturas | 390, 768, 1280 vacío y con resultado | PASS | `ui-idle-*`, `ui-success-*` | |
| QA-07 | axe | idle, success 1280, success 390, privacidad 390 | PASS | sin serious/critical | No certifica WCAG |
| QA-08 | Carga real | escritorio, CSV oficial | PASS | vídeo 66 s | Más largo que 10 s por el diálogo de fichero |
| QA-09 | Vacío | inicio sin análisis | PASS | `ui-idle-1280.png` | |
| QA-10 | Error | CSV vacío tras un análisis bueno | PASS | `ui-error-1280.png`; el resultado anterior sigue | |
| QA-11 | 404 | `/no/existe/ruta` | PASS | status 404, `ui-404-1280.png` | |
| QA-12 | Reduced motion | resultado | PASS | `animationName=none` | |
| QA-13 | Teclado | foco en el input de fichero | PASS | verificación Playwright | |
| QA-14 | Contraste de tokens usados como texto | pares medidos | PASS | muted sobre blanco 6.61; acción con texto blanco 5.86. El borde `#788598` no se usa como texto | |
| QA-15 | Lockup | pie 390 y 1280 | PASS | apilado y horizontal visibles, sin recorte | |
| QA-16 | Consola limpia al abrir `/` | tras favicon | PASS | segunda pasada: sin mensajes de consola | |
| QA-17 | Lighthouse LCP, CLS, TBT | `/`, móvil 390×844 y escritorio 1350×940, throttling simulado, 3 corridas cada uno | PASS | `lighthouse-summary.json`. Móvil mediana LCP 904 ms, CLS 0, TBT 0 ms. Escritorio mediana LCP 904 ms, CLS 0, TBT 0 ms | La UI no tiene bundler: el build de producción es el proceso uvicorn sin recarga sirviendo los ficheros del commit |
| QA-18 | Firefox y Safari | — | NO EJECUTADO | no instalados | |
| QA-19 | forced-colors y lector de pantalla | — | NO EJECUTADO | hay CSS de forced-colors; no hay captura ni pase manual | |
| QA-20 | Zoom CSS 200% a 390 | overflow | PASS | `zoom200-390` = 0. No es el zoom del navegador | |

## Motion

Un solo efecto: el bloque de resultado pasa de fondo `--color-selected` a transparente en 180 ms (`--motion-state`), para marcar que el cálculo acaba de llegar. El texto se lee desde el primer frame. Con `prefers-reduced-motion` y con `data-motion=reduced` la animación no corre. No hay puntero perseguido ni bucle.

## Copy por bloque

| Bloque | Para quién | Pregunta | Hecho | Siguiente acción |
| --- | --- | --- | --- | --- |
| Título y lead | Supervisión de soporte | Qué hace esta pantalla | El CSV del helpdesk no va a una IA | Elegir el fichero |
| Carga | Quien trae el export | Cómo entra el fichero | Columnas del briefing | Analizar fichero |
| Resultado | Quien lee el resumen | Cuántos válidos, inválidos y qué satisfacción | Cifras del CSV cargado | Descargar results.csv |
| Inválidos | Quien tiene que corregir el export | Qué fila falla y por qué regla | Línea, ticket, regla; sin correo | Volver al helpdesk |
| Privacidad | Quien duda del correo | Qué se guarda | Solo el resumen agregado | Volver al análisis |

## Combinación con el monorepo

El sitio público de la raíz usa Tailwind y no es el design system que este enunciado pida respetar. El backoffice aplica SIGNAL entero y no mezcla ese tema.
