# Carpeta `services`

Esta carpeta contiene **todos los servicios backend** (APIs y workers en segundo plano) relacionados con la compañía para el proyecto transversal de AI Engineering.

Cada subcarpeta dentro de `services/` debe corresponder a **un servicio concreto** (por ejemplo `admin-api`, `data-processor-worker`) e incluir su propia documentación técnica y funcional.

- **Propósito principal**: centralizar toda la lógica backend, APIs y consumidores de colas que dan soporte a los casos de uso de la compañía.
- **Recomendación**: documenta en este archivo (o en sub-READMEs) los servicios que vayas añadiendo, su objetivo, tecnología usada y cómo ejecutarlos.

## `api/`

API FastAPI central. Incidencias: `POST /api/incidents/analyze` y `GET /api/incidents/results/export`. Proveedores: `/suppliers` y la página `/proveedores`. Auth: `/auth`, `/users` y `/profiles` (TinyDB, JWT). Esas rutas de incidencias y proveedores piden un token. Inventario: `/inventory` (SQLModel sobre PostgreSQL con `DATABASE_URL`; los usuarios siguen en TinyDB). La consulta comercial es `POST /knowledge/query` y el agente LangGraph es `POST /agent/query`, en el mismo proceso. Cómo arrancarla: [`api/README.md`](./api/README.md).
