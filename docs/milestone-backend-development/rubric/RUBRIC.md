# Rúbrica — 021 Inventario con ORM y doble base de datos (Nexova)

Fuente: README del syllabus `ai-eng-milestone-backend-development` (inglés y español) y `content/contexts/05-backend-development/nexova-BRIEFING`. El enunciado manda sobre el encargo y sobre SIGNAL. La base es el monorepo ya existente, en `feature/company-monorepo-container` (`2232caf`).

Leyenda: **required** = exigido por el enunciado o por la forma de entrega. **extra** = por encima del mínimo. **no cuenta** = HITL o bloqueo externo; no entra en el 100%.

| ID | Required | Criterio |
| --- | --- | --- |
| R01 | sí | El trabajo vive en el monorepo de Nexova. La rama es `feature/milestone-backend-development`, tomada de `feature/company-monorepo-container` en `2232caf`. No hay otro repositorio. |
| R02 | sí | Se extiende el FastAPI que ya está en `services/api`. No se crea un servicio nuevo. La auth TinyDB y el JWT de 012/013/014 siguen igual de comportamiento. |
| R03 | sí | `sqlmodel` y `psycopg2-binary` se añaden con `uv add`. El ORM de inventario es SQLModel. No se modela el inventario con SQLAlchemy suelto ni con `pip install`. |
| R04 | sí | `DATABASE_URL` se lee del entorno. No hay credenciales en el código. `.env` está en `.gitignore`. El ejemplo deja la variable vacía. |
| R05 | sí | Al arrancar se abren las dos conexiones: el cliente TinyDB de usuarios y, si hay URI, el motor SQLModel. |
| R06 | sí | `get_db` entrega una sesión SQLModel por petición con `Depends()`. No hay una sesión global. |
| R07 | sí | `Asset` es tabla SQLModel con `id`, `name`, `sku`, `category` y `office`. `current_stock` no es columna. |
| R08 | sí | `AssetEntry` tiene `id`, `asset_id` con FK a `Asset`, `quantity`, `supplier`, `office`, `created_at` y `user_uuid`. `user_uuid` no tiene FK y no hay tabla de usuarios. |
| R09 | sí | `AssetExit` tiene `id`, `asset_id` con FK, `quantity`, `exit_type`, `assigned_to` nulo, `office`, `created_at` y `user_uuid`. |
| R10 | sí | `SQLModel.metadata.create_all(engine)` corre al arrancar. Queda escrito que es solo para este aprendizaje, no para una base compartida de producción. |
| R11 | sí | Los schemas de petición y respuesta son Pydantic, en otro archivo, y no son las clases del ORM. La respuesta del activo incluye `current_stock` calculado. |
| R12 | sí | Ningún endpoint de inventario devuelve un objeto SQLModel. Usan `response_model`. |
| R13 | sí | Hay un `APIRouter` con `prefix="/inventory"` registrado en la app principal. |
| R14 | sí | Existen `GET/POST /inventory/products`, `GET /inventory/products/{id}`, `POST /inventory/orders/inbound`, `POST /inventory/orders/outbound` y `GET /inventory/orders`. |
| R15 | sí | Las escrituras exigen el JWT. Los GET quedan públicos: el briefing de Nexova no pide lo contrario (el ejemplo HealthCore no es Nexova). |
| R16 | sí | `current_stock` = suma de entradas − suma de salidas de ese activo. No se puede enviar en el alta. Un activo nuevo nace en 0 y solo suma con entradas. |
| R17 | sí | El alcance del stock es el activo. `office` filtra listados. El briefing no parte el stock de un mismo activo por oficina: cada SKU ya pertenece a una oficina. |
| R18 | sí | Una salida que dejaría el stock negativo responde `400` con el mensaje exacto del briefing y no inserta la fila. |
| R19 | sí | Cada orden creada por la API guarda el `user_uuid` del usuario autenticado de TinyDB. El cliente no puede elegir ese valor. |
| R20 | sí | `assigned_to` es obligatorio en `allocation` y nulo en `consumption`. Si no, error de validación y no hay escritura. |
| R21 | sí | PostgreSQL impone la FK de `asset_id`. No existen tablas `user` ni `profile` en el esquema de inventario. |
| R22 | sí | La semilla del briefing está cargada. `GET /inventory/products` devuelve el neto de esas filas. |
| R23 | sí | Los nombres de entidad y de campo son los del briefing: `Asset`, `AssetEntry`, `AssetExit` y los campos listados allí. |
| R24 | sí | `category` solo acepta `hardware`, `peripherals`, `office_supplies`, `training_materials`. `office` solo `Valencia` o `Miami`. `exit_type` solo `allocation` o `consumption`. |
| R25 | sí | CRUD, relaciones y escrituras con JWT se probaron contra PostgreSQL real, con `DATABASE_URL`. Un mock o SQLite no cuenta. |
| R26 | sí | La suite previa de `services/api` sigue en verde. La raíz del monorepo también. |
| R27 | sí | No se versiona ningún secreto. La URI de prueba no está en el repositorio. |
| R28 | sí | `GET /inventory/orders` trae el activo y `user_uuid` sin una consulta por fila. |
| R29 | sí | El encargo deja los documentos en `docs/milestone-backend-development/`. |
| R30 | sí | Hay pull request contra `feature/company-monorepo-container`. No se hace merge. No se inventa autoría ni se envía al LMS. |
| S01 | no cuenta | URI real de Supabase con Transaction pooler. No hay proyecto Supabase en este entorno. |
| S02 | no cuenta | Conexión a un proyecto Supabase alojado. PostgreSQL local no sustituye ese proyecto. |
| D01 | no cuenta | Entregar la URL del fork por la plataforma del estudiante. |
| D02 | no cuenta | Miguel pega la URI, revisa el PR y decide el merge. |
| E01 | extra | Guía visible de curl autenticado y tabla de stock sembrado en el README de la API. |
| E02 | extra | La salida bloquea la fila del activo (`FOR UPDATE`) y un test de dos salidas a la vez no deja el stock negativo. Hay `CHECK (quantity > 0)` en PostgreSQL. |
