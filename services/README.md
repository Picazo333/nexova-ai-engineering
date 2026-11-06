# `services` folder

This folder contains **all the backend services** (APIs and background workers) related to the company for the cross-functional AI Engineering project.

Each subfolder inside `services/` must correspond to **one specific service** (for example: `admin-api`, `data-processor-worker`) and include its own technical and functional documentation.

- **Main purpose**: to centralize all the backend logic, APIs, and queue consumers that support the company's use cases.
- **Recommendation**: document in this file (or in sub-READMEs) the services you add, their objective, the technology used, and how to run them.

> _Spanish version: [README.es.md](./README.es.md)._

## Contenedor

`Dockerfile` instala `uv` y las dependencias con `uv pip install -r requirements.txt`. El comando de arranque es Uvicorn con `--reload`. El secreto `JWT_SECRET` se lee del entorno; si falta, el proceso sale. No hay un secreto en la imagen.

## `api/`

Central FastAPI app. Incidents: `POST /api/incidents/analyze` and `GET /api/incidents/results/export`. Suppliers: `/suppliers` plus the directory page `/proveedores`. Auth: `/auth`, `/users` and `/profiles` (TinyDB, JWT). Those incident and supplier routes require a bearer token. The commercial knowledge query is `POST /knowledge/query` on the same process, and the page is `/conocimiento`. The LangGraph support agent is `POST /agent/query` on that same process (`app/agent/`). Run instructions: [`api/README.md`](./api/README.md).
