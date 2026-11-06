# Justificación — caso 038

Commit `9068b51677347f78477dd06e755c9ef22525f018` en `feature/rag-knowledge-base`, con base `feature/building-bullet-proof-applications` (`79802be`).

## Por qué el pyproject de la raíz se queda

El enunciado fija el comando y las rutas. Citas literales:

- Línea 59: «Install dependencies with `uv add` — Qdrant client, an embeddings library, your generation LLM SDK, `fastapi`, etc. Never use `pip install` or `pipenv`.»
- Líneas 68–72: chunking en `data/process/rag.py`, recuperación en `data/pipelines/rag.py`, endpoint en `services/routers/` o `services/api/`, UI en `uis/`, tests en `tests/pipelines/test_rag.py`.
- Línea 114: «Tests pass with `python -m pytest tests/pipelines/test_rag.py`.»

Ese `uv add` y ese pytest se ejecutan desde la raíz, así que `pyproject.toml` y `uv.lock` de la raíz cubren `data/` y `tests/`. FastAPI de runtime, uvicorn y la autenticación siguen en `services/api/pyproject.toml`. El router está en `services/api/app/routers/knowledge.py` y se incluye desde `services/api/app/main.py`. No hay un segundo `app.py`.

| ID | Estado | Cómo se cumplió | Evidencia |
| --- | --- | --- | --- |
| A01 | PENDIENTE_CONFIRMACION_MIGUEL | La frase de la línea 33 se cita en `RUBRIC.md`. Se implementó sin LangChain ni LlamaIndex. | Enunciado línea 33; `pyproject.toml` |
| R01 | PASS | La rama sale de `main` y el PR va contra `main` del monorepo. | `git rev-parse HEAD` |
| R02 | PASS | `docker-compose.yml` define `qdrant/qdrant:v1.13.4` en el puerto 6333. No hay daemon Docker en esta VM. El cliente embebido creó `nexova_knowledge`, insertó 32 puntos y respondió búsquedas. | `docker-compose.yml`; salida de `python -m data.process.rag`; `data/process/rag.py` líneas 210-236 y 303-343 |
| R03 | PASS | `uv add` instaló `qdrant-client`, `fastapi`, `openai`, `uvicorn`, `httpx` y, para el índice local, `fastembed`. El lock está en `uv.lock`. | `pyproject.toml`; `uv.lock` |
| R04 | PASS | `.env.example` deja `EMBEDDING_MODEL_ID=` y `GENERATION_MODEL_ID=` vacíos. El código de `data/` y `services/` no menciona `FOURGEEKS_API_TOKEN`. Un test pone esa variable y `embed()` sigue sin configurarse. | `.env.example`; `tests/process/test_embed_config.py`; `tests/test_project_constraints.py` |
| R05 | PASS | Los ocho archivos coinciden byte a byte con el commit `fd2da034` del syllabus. `setup()` solo indexa esa lista. | `docs/company-knowledge-base/`; `data/process/rag.py` líneas 28-41 y 62-72 |
| R06 | PASS | No hay dependencia ni import de LangChain o LlamaIndex. Las llamadas son `QdrantClient` y el SDK `openai`. | `pyproject.toml`; `tests/test_project_constraints.py` |
| R07 | PASS | El corte es por línea en blanco. Una frase partida por el ancho del archivo sigue en el mismo bloque. La lista de viñetas se queda con su encabezado. El test compara cada línea no vacía del archivo con los chunks, en orden. | `data/process/rag.py` líneas 121-159; `tests/process/test_chunking.py` |
| R08 | PASS | Conteos: service-lines 5+5, pricing 3+3, SLA 4+4, objeciones 4+4. Total 32. | Salida de `setup()`; `tests/process/test_chunking.py` |
| R09 | PASS | `setup()` llama a `embed()` por chunk y `retrieve()` llama a la misma `embed()`. | `data/process/rag.py` línea 238 y 320; `data/pipelines/rag.py` línea 55 |
| R10 | PASS | Si los dos IDs coinciden, `embed()` lanza `ModelIdConflict` antes de la llamada. El test remoto comprueba que el cuerpo usa `embed-model` y no `gen-model`. | `data/rag_settings.py` líneas 74-86; `tests/process/test_embed_config.py` |
| R11 | PASS | Corrida live contra `https://llm.4geeks.ai/v1` con el modelo de embeddings `online/openrouter/perplexity/pplx-embed-v1-0.6b`. `setup()` indexó 32 chunks, vector_size 1024. La key no está en el repo. | `docs/rag/evidence/llm-live/01-setup-embed.txt` CURRENT |
| R12 | PASS | La constante y el briefing dicen `nexova_knowledge`. `setup()` creó esa colección. | `data/rag_settings.py` línea 15; `docs/rag/company-BRIEFING.en.md`; salida de `setup()` |
| R13 | PASS | El test de `setup()` exige exactamente `company`, `source_document`, `section`, `language`, `chunk_index` y `text`, con `company=nexova`. | `data/process/rag.py` líneas 191-200; `tests/process/test_setup.py` |
| R14 | PASS | Clear-and-reload más UUID5. Dos ejecuciones sobre el mismo cliente en memoria dejan el mismo conteo y los mismos IDs. | `data/process/rag.py` líneas 186-189 y 324-331; `tests/process/test_setup.py`; `docs/rag/rag-design.md` |
| R15 | PASS | `retrieve()` embebe, llama a `query_points` con `score_threshold` y devuelve diccionarios. El test mockea el cliente. | `data/pipelines/rag.py` líneas 35-77; `tests/pipelines/test_rag.py` |
| R16 | PASS | Con scores 0.91, 0.20 y 0.55 y `min_score=0.4`, el resultado tiene 2 elementos. Otro test devuelve lista vacía. | `tests/pipelines/test_rag.py` |
| R17 | PASS | `query()` llama a `retrieve()` y luego a `generate_answer()`. El router llama a `pipeline.query`. | `data/pipelines/rag.py` líneas 144-152; `services/api/routers/knowledge.py` líneas 86-99 |
| R18 | PASS | `generate_answer()` arma el prompt y llama a `complete_chat()`. El test de `query()` espía ese camino y comprueba que el chunk entra al prompt y no sale como respuesta. | `data/pipelines/rag.py` líneas 106-117; `tests/pipelines/test_rag.py` |
| R19 | PASS | La respuesta JSON es `{ "answer" }` o un error `{ "detail" }`. El test rechaza `score` y `source_document` en el JSON de una respuesta mock. Ante 503 no hay campo `answer`. | `tests/api/test_knowledge_api.py` |
| R20 | PASS | Pregunta fuera del corpus («¿Cuál es la capital de Mongolia y cuántos habitantes tiene?»): 0 chunks sobre el umbral. El modelo dijo que la base no contiene esa información y no inventó la capital ni la población. | `docs/rag/evidence/llm-live/03-generation-live.json` caso R20 CURRENT |
| R21 | PASS | El prompt nombra al vendedor de Nexova, al prospecto, el uso exclusivo del contexto, el 22%, Marcos Ibáñez, los promedios, la garantía de 6 meses y el conflicto de interés. | `data/pipelines/rag.py` líneas 17-33; `tests/pipelines/test_rag.py` |
| R22 | PASS | Generación live con `online/openrouter/deepseek/deepseek-v4-flash`. La pregunta de headhunting cita `Sources: service-lines — Executive and mid-management headhunting`. `POST /knowledge/query` devolvió HTTP 200 con respuesta completa y fuentes en los reintentos de `05-api-knowledge-query.txt`. El primer 200 con `{"answer":"Gra"}` queda registrado como defecto y no como PASS: `complete_chat` ahora lo rechaza. | `docs/rag/evidence/llm-live/03-generation-live.json`; `docs/rag/evidence/llm-live/05-api-knowledge-query.txt` CURRENT |
| R23 | PASS | Colección `nexova_knowledge`, `company=nexova`, slugs `service-lines`, `pricing-model`, `hiring-process-sla`, `objection-handling`, idiomas `en` y `es` como en los dos briefings. | `docs/rag/company-BRIEFING.en.md`; `docs/rag/company-BRIEFING.es.md`; `tests/process/test_setup.py` |
| R24 | PASS | El test JSON obtiene 200 y `{ "answer": "Respuesta del modelo." }` cuando `query()` está mockeado. | `tests/api/test_knowledge_api.py` |
| R25 | PASS | El router no reimplementa búsqueda ni prompt. Llama a `data.pipelines.rag.query`. | `services/api/routers/knowledge.py` líneas 94-99 |
| R26 | PASS | El cuerpo de éxito solo tiene `answer`. El de error solo tiene `detail`. | `tests/api/test_knowledge_api.py` |
| R27 | PASS | La página tiene etiqueta, campo y botón. El POST de formulario pinta la respuesta del endpoint, incluidas las líneas `Sources:`. En el navegador, sin modelo, se ve el error del endpoint, no un texto inventado. | `uis/knowledge-query/index.html`; `tests/api/test_knowledge_api.py`; capturas |
| R28 | PASS | Vacío inicial, «Consultando la base y redactando la respuesta.», y alerta «No se pudo obtener la respuesta» con reintento. La pregunta permanece en el campo. | `ui-390-idle.png`, `ui-390-loading.png`, `ui-390-error.png`, `ui-768-error.png`, `ui-1280-error.png` |
| R29 | NO APLICA | No hay design system de backoffice en este repo. SIGNAL pide base clara y es la que usa la página. | `uis/knowledge-query/tokens.css` |
| R30 | PASS | El archivo existe y cubre `retrieve()` y `query()`. | `tests/pipelines/test_rag.py` |
| R31 | PASS | Cliente Qdrant falso. Se excluye el hit de 0.20 y se respeta `k`. | `tests/pipelines/test_rag.py` |
| R32 | PASS | `retrieve()` y `complete_chat()` mockeados. La salida es la del modelo, no `RAW_CHUNK_TEXT_XYZ`. | `tests/pipelines/test_rag.py` |
| R33 | PASS | `uv run python -m pytest tests/pipelines/test_rag.py` → 7 passed. La suite amplia, 25 passed. | Salida de pytest en esta corrida |
| R34 | PASS | 27 preguntas. Cubren los cuatro slugs en `en` y `es`. Hay objeciones copiadas de los dos archivos de objeciones. Las tres últimas son compuestas y cada aguja está en un solo chunk. | `data/eval/test-queries.json`; `tests/process/test_chunking.py` |
| R35 | PASS | Recall@3 live del set de 24, en el espacio del modelo de embeddings de 4Geeks: 24/24 = 1.00, `official_4geeks_criterion: measured`. Ese PASS no cubre las 3 preguntas compuestas añadidas después. | `docs/rag/evidence/llm-live/02-recall-at-3.txt` y `02-recall-report.json` CURRENT para esas 24 |
| R35b | PENDIENTE_RECORRIDA | Recall@3 del set de 27. Sobre `2d04ec7` dio 26/27: falla `es-compound-fee-and-discount` (top3 service-lines, objection-handling, service-lines, sin pricing-model y por debajo de min_score). El arreglo híbrido de este head no se ha vuelto a medir en vivo. No es PASS. | `data/eval/test-queries.json`; la corrida 26/27 no se marca como cierre |
| R37 | PENDIENTE_RECORRIDA | `POST /knowledge/query` de tarifa y rebaja. Sobre `2d04ec7` respondió 502 `incomplete answer (length)`. El presupuesto de tokens sube y el rechazo de truncados se queda. No hay corrida live de este head. No es PASS. | Log de `2d04ec7`; `complete_chat` en `data/pipelines/rag.py` |
| R36 | PASS | El documento describe el flujo, el corte por párrafos, los dos IDs, la dimensión 384 del modelo local, coseno, `min_score` 0.40 y el preprocesado. Dice explícitamente que 4Geeks no se llamó. | `docs/rag/rag-design.md` |
| S01 | PASS | Los colores y el espaciado salen del brief. La familia es Arial, Helvetica, sans-serif. El ZIP no estaba, así que no hay hash de `tokens.css` del paquete. | `uis/knowledge-query/tokens.css`; `styles.css` |
| S02 | PASS | Vacío, carga y error están fotografiados. El éxito con una respuesta de modelo se cubre en el test de formulario, que pinta «Fuentes citadas». No hay captura de una respuesta generada porque R22 está bloqueado. | Capturas; `tests/api/test_knowledge_api.py` |
| S03 | PASS | Contraste mínimo de texto 5.86 (blanco sobre `#B53A17`). Borde `#788598` sobre blanco, 3.75. Axe sin violaciones. Primer Tab cae en «Saltar al contenido». A 320 px no hay scroll horizontal. Con `prefers-reduced-motion` la animación computada es `none`. | `/opt/cursor/artifacts/ui/ui-checks.json`; capturas |
| S04 | PASS | Capturas idle y error en 390, 768 y 1280. Carga en 390. 404 en 1280. Video manual de 27 s. | `/opt/cursor/artifacts/ui/`; `/opt/cursor/artifacts/nexova-rag-query-error-flow.mp4` |
| S05 | PASS | Tres corridas móviles 390×844, RTT 150, 1638.4 kbps, CPU ×4. Tres de escritorio 1280×800, RTT 40, 10240 kbps, CPU ×1. `configSettings` verificado en cada JSON. Mediana móvil LCP 1369 ms, CLS 0, TBT 0. Peor móvil LCP 1373 ms. Mediana escritorio LCP 330 ms, CLS 0.020, TBT 0. INP de campo no se midió; el laboratorio aporta TBT. | `docs/rag/lighthouse-summary.json`; `/opt/cursor/artifacts/lighthouse/` |
| S06 | PASS | El footer claro usa `signal-horizontal.svg` copiado byte a byte, 400 px de ancho en 768 y 1280. En 390 el horizontal no cabe a 400 px, así que se muestra `signal-stacked.svg` del mismo ZIP a 280 px. `signal-reverse.svg` se comprobó en el ZIP y no se coloca: el fondo es `#F7F8FA`, no oscuro. Ningún SVG se editó. | sha256 horizontal `85459232bf51e7bf7c94225fd4f2cd6b71a681b6d701cb4ffd6d2a142cf57a81`; reverse `19f897e5427e2187fece9eca51e6f5eeb9f1b82405990bae42ba18057683f38e`; stacked `11314b300284db342bc15a7c7695c23199f65f68178af45586b62d01e9ea133a`. Anchos en `/opt/cursor/artifacts/ui/lockup-widths.json`. Capturas `ui-390-idle.png`, `ui-768-idle.png`, `ui-1280-idle.png`. |
| S07 | PASS | No hay `.env` versionado. `.env.example` no tiene valores. Las capturas no muestran claves. El mensaje de error no incluye secretos. | `.gitignore`; `.env.example`; capturas |
| S08 | PASS | La página es un formulario, la respuesta y la lista de documentos. No hay hero, métricas ni testimonios. Las preguntas de ejemplo están en el corpus. | `uis/knowledge-query/index.html`; capturas |
| S09 | PASS | `meta robots` es `noindex, nofollow`. No hay sitemap ni schema. | `index.html`; `404.html` |
