# Justificación de la rúbrica

Commit de implementación: `d7952db5a37fffeec3f98dedf9a8ec20da5cb95b`. Pruebas: `python -m pytest -q` → 24 passed. Navegador: Chrome, Playwright, más un recorrido en el escritorio.

| ID | Estado | Cómo se cumple | Evidencia |
| --- | --- | --- | --- |
| R01 | PASS | `scripts/analyze.py` toma `csv_path` y flags opcionales. El test llama al script con la ruta absoluta del CSV oficial. | `scripts/analyze.py` líneas 28-36. `packages/incident_analysis/tests/test_cli.py` `test_script_prints_briefing_figures_and_prompts`. |
| R02 | PASS | `analyze_bytes` decodifica UTF-8 con BOM y usa `csv.DictReader`. | `packages/incident_analysis/engine.py` líneas 198-221 y 223-247. |
| R03 | PASS | Diez reglas, contadas por separado. La consola lista las que se activan y resume en una línea las que quedan a 0. | `engine.py` `_flags` líneas 333-360 y `_console` 431-516. Test `test_each_invalid_rule_and_a_row_with_two_rules`. |
| R04 | PASS | `total_records`, `valid_records`, `invalid_records`. | Consola: `TOTAL RECORDS IN FILE 100`, válidos 96, inválidos 4. Test `test_official_file_matches_briefing_figures`. |
| R05 | PASS | TECHNICAL 28, BILLING 18, ACCESS 21, HR_QUERY 17, COMPLAINT 12, con porcentajes half-up. | Mismas líneas de consola que el briefing. Test de porcentajes 29.2, 18.8, 21.9, 17.7, 12.5. |
| R06 | PASS | OPEN 27, CLOSED 56, DISCARDED 13. | Test de `status_counts` y líneas de consola. |
| R07 | PASS | Solo CLOSED válidos. Media 215/56 = 3.84 half-up. Un OPEN con puntuación no entra en la media. | `engine.py` `_average` líneas 401-405. Tests oficial y `test_open_ticket_score_is_not_part_of_the_average`. |
| R08 | PASS | El bloque del briefing (separador, árbol, porcentajes) sale tal cual, más la línea de reglas a 0. | `test_official_console_contains_briefing_lines`. Artifact `cli-output.txt`. |
| R09 | PASS | El texto de la pregunta es el del briefing. También se acepta `s`. | `scripts/analyze.py` líneas 61-73. Test de CLI con stdin `n`. |
| R10 | PASS | `results.csv` en el directorio actual, columnas `metric,label,value`, una fila por métrica. | `engine.py` `csv_text` líneas 121-128. Test `test_export_is_one_metric_per_row` y `test_script_exports_one_row_per_metric`. |
| R11 | PASS | Ejecutado sobre el CSV oficial, no sobre cifras escritas a mano. Coinciden 100 / 96 / 4, las cinco categorías, los tres estados, la distribución 2-5-10-22-17 y la media 3.84. Los cuatro inválidos son NXV-000017, NXV-000043, NXV-000086 y NXV-000090. | Tests de motor. Salida en `/opt/cursor/artifacts/cli-output.txt`. |
| R12 | PASS | `POST /api/incidents/analyze`, campo `file`. JSON con los mismos números. | `services/api/app/routers/incidents.py` líneas 16-45. `test_analyze_json_matches_briefing`. |
| R13 | PASS | `GET /api/incidents/results/export`, `Content-Disposition: attachment; filename="results.csv"`. | `incidents.py` líneas 48-65. `test_export_after_analyze_is_the_csv`. Descarga real: `downloaded-results.csv`. |
| R14 | PASS | Vacío y sin filas → 400. Sin campo → 400. Por encima del tope → 413. Sin análisis previo → 404. El mensaje no copia celdas. | `test_input_errors_use_client_status_codes`. |
| R15 | PASS | Menú de cabecera y de pie: «Análisis de incidencias» apunta a `/`. | `uis/backoffice/partials/layout.html`. |
| R16 | PASS | Selector de fichero y zona para soltar. El envío va a la API. Recorrido de escritorio: diálogo de fichero, `incidents-nexova.csv`, botón Analizar. | `partials/home.html`. Vídeo `incidents-backoffice-upload.mp4`. |
| R17 | PASS | Tablas de totales, categoría, estado y satisfacción, más la frase con 96 y 3.84. | Playwright `summary 96 valid`. Capturas `ui-success-390.png`, `ui-success-768.png`, `ui-success-1280.png`. |
| R18 | PASS | Enlace «Descargar resultados CSV». En el escritorio la descarga figura como hecha. | `pages.py` enlace `data-export`. Test de descarga. Vídeo. |
| R19 | PASS | Tabla de reglas con el conteo de cada una, y detalle por línea y ticket, sin correo. | `pages.py` `_rules` y `_details`. Captura de escritorio `ui-desktop-results.png`. |
| R20 | PASS | Una sola implementación en `packages/incident_analysis`. El script y el router la importan. | `scripts/analyze.py` línea 26. `incidents.py` línea 13. |
| R21 | PASS | Script y CSV en `scripts/`. API en `services/api`. UI en `uis/backoffice`. | Árbol del commit `d7952db`. |
| R22 | PASS | Categorías, estados y formatos `NXV-XXXXXX`, `AGT-XX`, `YYYY-MM-DD` salen del briefing. Los tests recorren los correos del CSV oficial y fallan si aparecen en consola, JSON, CSV o HTML. | `test_official_output_never_contains_customer_email` y `test_saved_analysis_has_no_email`. |
| R23 | PASS | Captura de la salida real del script y capturas de la interfaz con el análisis. | `/opt/cursor/artifacts/cli-stdout.png`, `cli-output.txt`, `ui-success-1280.png`, `ui-desktop-results.png`. |
| R24 | PASS | No hay cliente de IA. El cálculo es Python local. El README lo dice y la página de privacidad también. | `services/api/README.md`. `partials/privacy.html`. |
| R25 | BLOCKED | El enunciado pide merge a `main`. La orden de esta ejecución prohíbe el merge y deja el estado en revisión del orquestador. El PR queda abierto. | Esta justificación y el cuerpo del PR. |
| S01 | PASS | Siete ficheros de SIGNAL comparados con el manifiesto. Test `test_signal_asset_hashes`. | `services/api/tests/test_assets.py`. |
| S02 | PASS | `tokens.css` fija Arial, Helvetica, sans-serif. No hay `@import` de fuentes. | `uis/backoffice/tokens/tokens.css`. |
| S03 | PASS | Título de la tarea, carga, tablas y detalle. Sin tres tarjetas decorativas, sin hero, sin cifras que no salgan del CSV. | Capturas idle y success. |
| S04 | PASS | Vacío inicial, texto de carga, resultado, error de fichero vacío conservando el análisis anterior. | `ui-idle-1280.png`, `ui-error-1280.png`, test `previous result kept`. |
| S05 | PASS | axe sin violaciones en idle-1280, success-1280, success-390 y privacy-390. | `/tmp/evidence/report.json` clave `axe`. |
| S06 | PASS | `scrollWidth - clientWidth` = 0 en esas anchuras, en vacío y con resultado. | `report.json` clave `overflow`. |
| S07 | PASS | PNG headless de Chrome a 390, 768 y 1280, vacío y con resultado. | Artifacts `ui-idle-*` y `ui-success-*`. |
| S08 | PASS | Vídeo de escritorio de 66 s: diálogo de fichero, análisis, tablas y descarga. Dura más de 10 s porque el diálogo nativo entra en la toma. | `incidents-backoffice-upload.mp4`. |
| S09 | PASS | Contexto `reduced_motion=reduce`: `data-motion=reduced` y `animationName=none`. | Test del script de verificación. `ui-reduced-1280.png`. |
| S10 | PASS | `<picture>` cambia a 639 px. CSS: 400 px y 280 px, `height: auto`. | `layout.html` y `css/app.css`. Visible en idle-1280 e idle-390. |
| S11 | PASS | El foco llega a `#csv-file`. El arrastre no es el único camino. | Verificación Playwright `file input focusable`. |
| S12 | PASS | `GET /no/existe/ruta` → 404 con el texto de ruta no encontrada. `<script>` en la ruta se escapa. | `test_pages_statuses_and_static_lockup`. `ui-404-1280.png`. |
| S13 | PASS | `meta robots noindex, nofollow`. Sin canonical, sitemap ni schema. SEO de landing pública: NO APLICA, es un backoffice. | `layout.html`. |
| S14 | PASS | Test `test_front_end_transfer_budgets`. | `test_assets.py`. |
| S15 | NO EJECUTADO | No se midió LCP ni INP con el perfil de laboratorio pedido. No se afirma un tiempo. | — |
| S16 | NO EJECUTADO | Firefox no está instalado en esta máquina. | — |
| S17 | NO EJECUTADO | Safari no está disponible. | — |
| S18 | NO EJECUTADO | Hay reglas `forced-colors` en CSS, pero no hay captura de ese modo ni pase de lector de pantalla. axe no sustituye ese pase. | `css/app.css` al final del fichero. |
