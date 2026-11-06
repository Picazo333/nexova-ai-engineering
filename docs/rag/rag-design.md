# Diseño RAG — Nexova

La base responde preguntas de un SDR antes o durante una llamada con un prospecto. La voz pedida por el briefing es la de un vendedor de Nexova: segura, orientada a cerrar, y limitada a los documentos comerciales. La colección se llama `nexova_knowledge`.

## Proceso

1. Los ocho archivos oficiales de `docs/company-knowledge-base/` se leen en `setup()`. Son las cuatro fuentes del briefing (`service-lines`, `pricing-model`, `hiring-process-sla`, `objection-handling`) en inglés y en español, copiadas de `00-general-contexts/nexova/` sin reescribirlas.
2. `setup()` las parte en bloques semánticos y llama a `embed()` una vez por bloque.
3. Qdrant guarda cada bloque como un punto. La estrategia de idempotencia es clear-and-reload: si la colección existe, se borra y se vuelve a crear. El ID de cada punto es un UUID5 de `nexova | source_document | language | chunk_index`, así que el mismo bloque conserva el mismo ID.
4. En una consulta, `retrieve()` vuelve a usar `embed()` con la pregunta, pide los `k` vecinos (por defecto 5) y descarta los que no llegan a `min_score`. Si la pregunta tiene dos cláusulas unidas por «y» / «o» (cada una de al menos cuatro palabras), busca cada cláusula por separado y las mezcla en round-robin, con tope `k`. Así una pregunta compuesta no deja fuera un documento porque el vector mezclado se fue hacia el otro tema. Una pregunta fuera del corpus sigue sin vecinos por encima del umbral: las dos cláusulas vuelven vacías.
5. `generate_answer()` arma el prompt con la pregunta y esos payloads, y llama al modelo de generación.
6. `query()` es exactamente `retrieve()` seguido de `generate_answer()`. El endpoint `POST /knowledge/query` solo llama a `query()` y devuelve `{ "answer" }`.

```text
docs/company-knowledge-base
        │
        ▼
     setup() ── embed(chunk) ──► Qdrant nexova_knowledge
                                      │
pregunta ── embed(pregunta) ── retrieve() ── generate_answer() ── query() ── POST /knowledge/query
```

## Chunking

Los archivos oficiales separan las ideas con una línea en blanco. Un salto de línea a mitad de frase no es un corte: la frase sigue en el mismo bloque. Una lista de viñetas se queda con el párrafo que la introduce. El título Markdown se queda con el primer bloque para no crear un chunk que solo sea el título.

Eso encaja con este corpus porque cada archivo ya está escrito por unidades: una línea de servicio, un bloque de tarifa, una regla del SLA o una objeción con su respuesta. No se usa un tamaño fijo de caracteres.

Conteo tras `setup()`: 32 fragmentos. Cada archivo produce al menos 3.

| Documento | en | es |
| --- | --- | --- |
| service-lines | 5 | 5 |
| pricing-model | 3 | 3 |
| hiring-process-sla | 4 | 4 |
| objection-handling | 4 | 4 |

El payload de cada punto lleva `company=nexova`, `source_document` con el slug del briefing, `section`, `language` (`en` o `es`), `chunk_index` y `text`.

## Embeddings

`embed(text) -> list[float]` es la única función que convierte texto en vector. Se usa al indexar y al buscar.

Hay dos ranuras de modelo y no pueden compartir ID:

- Embeddings: `EMBEDDING_MODEL_ID`, `EMBEDDING_BASE_URL`, `EMBEDDING_API_KEY`. La llamada es `embeddings.create` del SDK de OpenAI contra esa base URL.
- Generación: `GENERATION_MODEL_ID`, `GENERATION_BASE_URL`, `GENERATION_API_KEY`. La llamada es `chat.completions.create` con temperatura 0.2.

En `.env.example` los dos IDs están vacíos y son variables distintas. Este código no lee `FOURGEEKS_API_TOKEN`.

En esta ejecución no hay clave ni ID de 4Geeks. `embed()` y `generate_answer()` se niegan a simular esa llamada. Para poder indexar y medir el recuperador en local existe `RAG_EMBED_BACKEND=fastembed`, que usa `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Es un modelo abierto, dimensión 384, y no sustituye al modelo de 4Geeks. Los vectores se normalizan L2 antes de guardarlos. Qdrant usa distancia coseno, así que el score es similitud: más alto es más cercano.

El texto no se pasa a minúsculas ni se le quitan acentos. El cuerpo del chunk conserva los saltos de línea del archivo oficial.

## Umbral

`min_score` por defecto es 0.40 (`RAG_MIN_SCORE` lo puede cambiar). `retrieve()` puede devolver menos de `k`, o cero.

El valor se eligió con el modelo local, no con el de 4Geeks. En las 24 preguntas de `data/eval/test-queries.json`, el acierto correcto más bajo que entró en el top 3 puntuó 0.459. Dos preguntas ajenas al corpus (wifi de la oficina, lluvia en Miami) puntuaron 0.338 y 0.153 en su primer vecino. 0.40 queda entre esas dos cifras: deja fuera el contexto claramente irrelevante y conserva el acierto más débil de este conjunto. Habrá que repetir la medición cuando exista el modelo de embeddings de 4Geeks, porque el espacio vectorial cambia.

## Generación

El prompt fija la voz del vendedor y la audiencia (el prospecto, con un SDR usando la respuesta en la llamada). Obliga a usar solo el contexto recuperado. Si `retrieve()` no devuelve nada, el mensaje de usuario lleva `(no retrieved context)` y el sistema pide decir que la base no tiene información suficiente.

También deja por escrito las reglas del briefing: no ofrecer un descuento bajo el 22% (hace falta la aprobación de Marcos Ibáñez, también si piden bajar del 22% al 15%), presentar los plazos como promedios salvo la garantía de reemplazo de 6 meses, y hablar con transparencia de clientes competidores.

La respuesta debe citar las fuentes que sí aparecen en el contexto, en la forma `Sources: <source_document> — <section>`. La UI separa esas líneas bajo «Fuentes citadas». No son scores ni payloads crudos. Sin modelo de generación configurado, el endpoint responde 503 y la pantalla lo muestra como error. No se rellena la respuesta con el texto del chunk.

## Evaluación

`data/eval/test-queries.json` tiene 24 preguntas. Cubren los cuatro slugs en los dos idiomas e incluyen las objeciones textuales de los dos archivos de objeciones. `data/eval/recall_at_3.py` calcula Recall@3 sobre el top 3, con umbral de ranking en -1 para no ocultar vecinos, y un segundo conteo con `min_score`.

Con el embedder local el resultado de esta corrida fue 23/24 (0.958). La pregunta que no acertó fue la duración de una búsqueda ejecutiva en inglés: el chunk de líneas de servicio, que también dice «6 to 8 weeks», ocupó el top 3 por delante del SLA. Sigue por encima del 80% de este embedder. El criterio oficial, medido con el modelo de 4Geeks, queda sin ejecutar.

## Cómo correrlo

```bash
uv sync --all-groups
cp .env.example .env
docker compose up -d qdrant          # o dejar QDRANT_URL vacío y usar el motor embebido
uv run python -m data.process.rag
cd services/api && uv sync && cd ../..
export PYTHONPATH=.:packages:services/api
export JWT_SECRET=local-dev-only
services/api/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
uv run python -m pytest tests/pipelines/test_rag.py
uv run python -m data.eval.recall_at_3
```

`docker compose` exige un daemon. En el entorno donde se escribió esto no había Docker; la conectividad comprobada es el cliente embebido de `qdrant-client`, que crea la colección, inserta los 32 puntos y responde `query_points`. El archivo `docker-compose.yml` queda para el entorno donde sí haya daemon.
