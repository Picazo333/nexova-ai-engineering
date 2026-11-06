# Rúbrica — análisis de incidencias Nexova

Fuente: enunciado `ai-eng-company-incidents-file-analyzer` y briefing `nexova-BRIEFING` (syllabus `content/contexts/incidents-file-analysis`). Empresa: Nexova, ya elegida en el Milestone 0. CSV: `scripts/incidents-nexova.csv` (SHA-256 `dadd5a0b65eebff2a395f672afb94c1d931db7918b711f98ee80e1319b5e8cb8`).

Implementación: commit `d7952db5a37fffeec3f98dedf9a8ec20da5cb95b`.

`required: true` bloquea la entrega académica. SIGNAL es obligatorio por la fase 2 salvo donde el propio SIGNAL dice NO APLICA.

| ID | Required | Criterio |
| --- | --- | --- |
| R01 | sí | `analyze.py` acepta la ruta del CSV por argumento y no hay que editar el código para cambiar de fichero. |
| R02 | sí | El script lee el CSV (UTF-8, cabecera, coma). |
| R03 | sí | Detecta, clasifica y muestra inválidos con el tipo de problema. |
| R04 | sí | Total procesado, válidos e inválidos por separado. |
| R05 | sí | Desglose por categoría sobre válidos. |
| R06 | sí | Desglose por estado. En Nexova: `OPEN`, `CLOSED`, `DISCARDED`. |
| R07 | sí | Media de satisfacción de los `CLOSED` válidos con puntuación. |
| R08 | sí | Consola legible: separadores, etiquetas, alineación. |
| R09 | sí | Pregunta `Export results to CSV? [y / n]`. |
| R10 | sí | Si la respuesta es afirmativa, escribe `results.csv` con una métrica por fila. |
| R11 | sí | Las cifras del CSV oficial coinciden con el briefing (100, 96, 4, categorías, estados, media 3.84). |
| R12 | sí | `POST /api/incidents/analyze` acepta CSV `multipart/form-data` y devuelve el resumen JSON. |
| R13 | sí | `GET /api/incidents/results/export` devuelve el último análisis como CSV descargable. |
| R14 | sí | Fichero vacío o formato incorrecto responde HTTP de error con mensaje. |
| R15 | sí | Hay una página de análisis accesible desde el menú. |
| R16 | sí | Se puede cargar el fichero desde la interfaz, sin terminal. |
| R17 | sí | La pantalla muestra métricas generales, categoría, estado y satisfacción. |
| R18 | sí | Hay un botón que descarga el CSV de resultados. |
| R19 | sí | Los inválidos se explican, con cuántos hay de cada tipo. |
| R20 | sí | La validación y el cálculo no están duplicados: script y API importan el mismo módulo. |
| R21 | sí | El código vive en `scripts/`, `services/api` y `uis/backoffice`. |
| R22 | sí | Campos, categorías y estados son los de Nexova. Ninguna salida imprime correos. |
| R23 | sí | El PR incluye captura de la consola con el CSV de 100 filas y captura de la interfaz con el análisis visible. |
| R24 | sí | El producto no envía el CSV a un servicio de IA. |
| R25 | sí | El enunciado pide merge a `main` tras aprobar el PR. |
| S01 | sí | Tokens y lockups de SIGNAL copiados sin cambiar bytes; hashes comprobados. |
| S02 | sí | Tipografía Arial/Helvetica, sin fuentes remotas. |
| S03 | sí | Pantalla operativa, sin hero comercial ni métricas inventadas. |
| S04 | sí | Estados vacío, carga, éxito y error, con reintento y sin perder el resultado anterior si el nuevo fichero falla. |
| S05 | sí | axe en Chrome sin violaciones serious/critical en inicio, resultado y privacidad. No es una certificación WCAG. |
| S06 | sí | Sin overflow de documento a 320, 390, 768, 1024, 1280 y 1440. |
| S07 | sí | Capturas reales a 390, 768 y 1280. |
| S08 | sí | Vídeo del recorrido real en el escritorio. |
| S09 | sí | `prefers-reduced-motion` deja el resultado en su estado final, sin animación. |
| S10 | sí | Lockup 4Geeks × Divinivid en el pie: horizontal ≥400px, apilado en estrecho ≥280px. |
| S11 | sí | El fichero se elige con teclado; arrastrar es adicional. |
| S12 | sí | Una ruta inexistente responde HTTP 404. |
| S13 | sí | App interna: `noindex`, sin sitemap ni dominio inventado. |
| S14 | sí | CSS gzip ≤40 KiB y JS gzip ≤170 KiB, medidos. |
| S15 | no | Laboratorio LCP/INP (390×844, CPU×4, red 150 ms, 3 corridas). |
| S16 | no | Firefox. |
| S17 | no | Safari. |
| S18 | no | Captura visual de forced-colors y pase manual de lector de pantalla. |
