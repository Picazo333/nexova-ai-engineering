# Agente de soporte

Grafo de apoyo comercial para una pregunta. Responde con la base de conocimiento de Nexova o con el gestor de incidentes, y elige cuál a partir del texto.

El grafo, los checkpoints y la traza están en `services/api/app/agent/`. La entrada HTTP es `POST /agent/query` en la app FastAPI existente (`services/api/app/main.py`). `GET /agent/runs/{run_id}` devuelve la traza guardada. `/agente` muestra una traza RAG y una traza de ticket, una al lado de la otra.

Nodos:

1. `receive_question` — guarda la pregunta y rechaza una vacía o demasiado larga.
2. `route_sources` — deja la ruta en `rag`, `ticket` o `both`.
3. `retrieve_context` — llama a `retrieve()` en `data/pipelines/rag.py`.
4. `lookup_ticket` — llama a la tool de tickets, de solo lectura.
5. `generate_answer` — llama a `generate_answer(question, context)` con los fragmentos del paso 3.
6. `report_ticket` / `compose_sources` — redactan la respuesta con el resultado de la tool y, si corrieron las dos fuentes, con la respuesta del RAG.

Aristas condicionales:

- Pregunta vacía o inválida → `refuse_empty`. No hay recuperación ni tool.
- Texto de ticket, sin texto de política → solo `lookup_ticket`.
- Texto de política, sin texto de ticket → solo `retrieve_context`.
- Las dos señales → `lookup_ticket` y después `retrieve_context`.
- Ningún fragmento por encima del umbral → `insufficient_context`. No hay generación.
- Timeout, error, token ausente o id desconocido → una frase honesta. No se inventa un estado.

`query()` no es un nodo. El estado es `question`, `context`, `answer`, `error`, `status`, `route`, `sources` y `ticket`. No hay historial de conversación.

La tool de tickets está en `services/api/app/agent/tools/tickets.py`. Ver `agents/tools/README.es.md`.

```bash
uv run python -m pytest tests/pipelines/test_agent_graph.py tests/pipelines/test_agent_routing.py
PYTHONPATH=services/api:. uv run python -m app.agent.export_trace
PYTHONPATH=services/api:. uv run python -m app.agent.export_compare
```

La generación en vivo necesita `GENERATION_MODEL_ID`, `GENERATION_BASE_URL` y `GENERATION_API_KEY`. La recuperación con el embedder remoto necesita `EMBEDDING_*`. Mientras estén vacías, el eval de anclaje en vivo informa `BLOCKED_HITL`. Los exports versionados usan un doble explícito para la generación y lo dicen. La columna del ticket no: lee una incidencia que guardó el gestor.

> _English version: [README.md](./README.md)._
