# Agente de soporte

Grafo de apoyo comercial para un SDR. Responde una pregunta con la base de conocimiento de Nexova.

El grafo, los checkpoints y la traza están en `services/api/app/agent/`. La entrada HTTP es `POST /agent/query` en la app FastAPI existente (`services/api/app/main.py`). `GET /agent/runs/{run_id}` devuelve la traza guardada.

Nodos:

1. `receive_question` — guarda la pregunta y rechaza una vacía o demasiado larga.
2. `retrieve_context` — llama a `retrieve()` en `data/pipelines/rag.py`.
3. `generate_answer` — llama a `generate_answer(question, context)` con los fragmentos del paso 2.

Aristas condicionales:

- Pregunta vacía o inválida → `refuse_empty`. No hay recuperación.
- Ningún fragmento por encima del umbral → `insufficient_context`. No hay generación.
- En cualquier otro caso → `generate_answer`.

`query()` no es un nodo. El estado es `question`, `context`, `answer`, `error` y `status`. No hay historial de conversación.

```bash
uv run python -m pytest tests/pipelines/test_agent_graph.py
PYTHONPATH=services/api uv run python -m app.agent.export_trace
```

La traza publicada es la corrida live de 4Geeks en `docs/langgraph/evidence/llm-live/`. Modelo de generación: `online/openrouter/deepseek/deepseek-v4-flash` en `https://llm.4geeks.ai/v1`. La respuesta de la tarifa mantiene el 22% y nombra a Marcos Ibáñez. Se rehace el export con `PYTHONPATH=services/api uv run python -m app.agent.export_trace`. Los tests de routing pueden sustituir las dos funciones del pipeline. Esos sustitutos no son la traza publicada.

> _English version: [README.md](./README.md)._
