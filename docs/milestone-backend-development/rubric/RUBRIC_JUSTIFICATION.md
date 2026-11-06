# Justificación — 021 Inventario

PostgreSQL 16.15 en local. Con `NEXOVA_TEST_DATABASE_URL`: `uv run pytest` en `services/api` → **169 passed**. Sin esa variable: **162 passed, 7 skipped**. Esos 7 saltos son las pruebas que exigen Postgres; no cuentan como PASS de base de datos. La raíz: **64 passed, 1 skipped** (el salto de generación en vivo ya estaba).

| ID | Estado | Cómo se cumple | Evidencia |
| --- | --- | --- | --- |
| R01 | PASS | La rama sale de `2232caf` en `feature/company-monorepo-container`. El código nuevo está dentro de este repo. | `git merge-base` con esa rama es `2232caf`. PR contra esa base. |
| R02 | PASS | El router se monta en `create_app()`. No hay otro paquete de servicio. Los tests de auth, proveedores e incidencias siguen verdes. `guide.py` solo añade la descripción OpenAPI de inventario. | `services/api/app/main.py` líneas 38, 67 y 113. `evidence/pytest-postgres.txt`. |
| R03 | PASS | `uv add sqlmodel psycopg2-binary` dejó `sqlmodel==0.0.48` y `psycopg2-binary==2.9.13` en `pyproject.toml`, `uv.lock` y `requirements.txt` (la imagen los instala con `uv pip`). Los modelos heredan `SQLModel, table=True`. | `services/api/pyproject.toml`. `services/api/app/inventory/models.py` línea 18. |
| R04 | PASS | `database_url()` lee `DATABASE_URL`. El ejemplo está vacío. `.env` y `services/api/.env` están en `.gitignore`. Una URI `sqlite` lanza error. | `app/inventory/database.py` líneas 36-56. `.gitignore` líneas 13-14. `.env.example`. Test `test_sqlite_url_is_rejected`. |
| R05 | PASS | `init_databases()` abre `get_auth_db()` (TinyDB de usuarios, sin cambiar el almacén) y, si hay URI, el motor SQLModel. Sin URI la API arranca y `/inventory` responde 503. | `app/inventory/database.py` líneas 117-129. `app/main.py` línea 67. Test `test_products_without_database_url_are_503`. |
| R06 | PASS | `get_db` hace `yield` de un `Session` y lo cierra. No hay `Session` de módulo. El `get_db` de `services/api/database.py` sigue siendo el TinyDB de proveedores; no se reutilizó para el inventario. | `app/inventory/database.py` línea 133. Test `test_router_prefix_and_no_global_session`. |
| R07 | PASS | Columnas de `asset`: `id`, `name`, `sku`, `category`, `office`. `information_schema` no lista `current_stock`. | `models.py` líneas 18-27. `evidence/postgres-inspect.txt`. |
| R08 | PASS | `assetentry.asset_id` referencia `asset(id)`. `user_uuid` no tiene FK. | `models.py` líneas 30-44. `postgres-inspect.txt` (definición de la FK). |
| R09 | PASS | `assetexit` tiene `exit_type`, `assigned_to` nulo y la misma FK. | `models.py` líneas 47-63. `postgres-inspect.txt`. |
| R10 | PASS | `create_all()` llama a `SQLModel.metadata.create_all(engine)` después de importar los modelos. El README dice que no vale para producción compartida. | `database.py` líneas 109-114. `services/api/README.md`, sección Inventario. |
| R11 | PASS | `schemas.py` usa `BaseModel`. `AssetRead.current_stock` existe. `Asset` no tiene ese campo. | `schemas.py` línea 27. Test `test_stock_is_not_a_column_and_schemas_are_separate`. |
| R12 | PASS | Las seis rutas declaran `response_model`. Las funciones devuelven `AssetRead` o `InventoryOrderRead`. | `app/routers/inventory.py`. |
| R13 | PASS | `APIRouter(prefix="/inventory")` e `include_router` en la app. El archivo vive en `services/api/app/routers/` porque ese es el servicio que ya existía, no un `services/main.py` plano. | `inventory.py` línea 13. `main.py` línea 113. |
| R14 | PASS | OpenAPI lista las cinco rutas (el POST y el GET de productos comparten path). | Test `test_openapi_lists_the_inventory_paths`. `evidence/http-transcript.txt`. |
| R15 | PASS | OpenAPI pone seguridad solo en el POST de productos. Sin token, el POST responde 401. El GET de productos respondió 200 sin token. | `http-transcript.txt`. Test `test_writes_require_the_tinydb_user`. |
| R16 | PASS | El alta de `NXV-PER-010` volvió `current_stock: 0`. Enviar `current_stock` respondió 422 y no creó el activo. El neto de `NXV-IT-001` es 12. | `http-transcript.txt`. `service.py` `stock_by_asset`. |
| R17 | PASS | El cálculo no filtra por `office` de la orden: suma todas las órdenes del `asset_id`. `GET /inventory/products?office=Valencia` devuelve los cuatro SKU de Valencia. El briefing fija la fórmula por activo y usa `office` para filtrar. | `seed.py` `EXPECTED_STOCK`. Test `test_seed_stock_matches_entries_minus_exits`. |
| R18 | PASS | Pedir 13 del portátil con 12 disponibles respondió 400 con el texto exacto. El stock siguió en 12 y no aumentó el número de salidas. | `service.py` línea 141. `http-transcript.txt`. Test `test_outbound_over_stock_is_400_before_any_write`. |
| R19 | PASS | La entrada creada con token guardó `user_uuid` igual al `id` de `/auth/me` (`35f56551-3914-4021-82d2-ad9db287db30` en la transcripción). Mandar `user_uuid` en el cuerpo es 422. | `routers/inventory.py` (`str(user["id"])`). `http-transcript.txt`. |
| R20 | PASS | `allocation` sin `assigned_to`, y `consumption` con `assigned_to`, responden 422. | `schemas.py` `assigned_to_follows_exit_type`. Test `test_writes_require_the_tinydb_user`. |
| R21 | PASS | `pg_constraint` muestra `FOREIGN KEY (asset_id) REFERENCES asset(id)` en las dos tablas de órdenes. Insertar `asset_id` 999999 lanza `IntegrityError`. Cero tablas `user`/`profile`. | `postgres-inspect.txt`. Test `test_postgres_enforces_the_foreign_key_and_has_no_user_table`. |
| R22 | PASS | Seis activos. Stock: IT-001 12, IT-002 6, PER-001 20, PER-002 0, OFF-001 18, TRN-001 15. En SQL, IT-001 tiene entradas 15 (10+5) y salida 3. | `seed.py`. `http-transcript.txt`. `postgres-inspect.txt`. |
| R23 | PASS | Clases y columnas con los nombres del briefing en inglés. Los nombres visibles de la semilla (`Laptop 14" Business`, `NXV-IT-001`, …) son los de `nexova-BRIEFING.en.md`. | `source/nexova-BRIEFING.en.md`. `models.py`. |
| R24 | PASS | Literales de Pydantic. `office=Lisboa` responde 422. | `schemas.py`. Test de filtro de oficina. |
| R25 | PASS | Dialecto `postgresql`, `SELECT version()` contiene `PostgreSQL`. 169 passed con la URI real. SQLite está rechazado y no se usó como éxito. | `evidence/pytest-postgres.txt`. `postgres-inspect.txt`. |
| R26 | PASS | Sin Postgres de pruebas: 162 passed y 7 skipped (157 anteriores + 5 pruebas que no abren la base). Con Postgres: 169 passed. Raíz: 64 passed, 1 skipped. Cobertura de `app.auth`: 91.60% (mínimo 70). | `evidence/pytest-sin-postgres.txt`, `pytest-postgres.txt`, `pytest-raiz.txt`, `pytest-cov.txt`. |
| R27 | PASS | La contraseña local y la URI no aparecen en el diff ni en las transcripciones. `git check-ignore` cubre `.env`. | `evidence/http-transcript.txt` (el token va como `<redacted>`). |
| R28 | PASS | `list_orders` usa `selectinload`. El test cuenta los `SELECT` de un listado de 9 órdenes y exige 6 o menos. Un N+1 se iría por encima. | `service.py` `list_orders`. Test `test_listing_orders_does_not_query_once_per_row`. |
| R29 | PASS | Rúbrica, justificación, excelencia, auditoría, evidencia, manifiesto y telemetría están en esta carpeta. | Este directorio. |
| R30 | PASS | El PR queda abierto contra `feature/company-monorepo-container`. No hay merge ni envío al LMS. El README no añade colaboradores. | Cuerpo del PR. |
| S01 | BLOCKED_HITL | Hace falta la URI de Transaction pooler de un proyecto Supabase. No está en el entorno y no se inventa. | `RUNBOOK_SUPABASE.md` pasos 1-3. |
| S02 | BLOCKED_HITL | No hubo conexión a un host `pooler.supabase.com`. El PASS de R25 es PostgreSQL local. | `RUNBOOK_SUPABASE.md`. `postgres-inspect.txt` muestra Ubuntu 16.15, no Supabase. |
| D01 | HITL_ENVIO_MIGUEL | Enviar la URL del fork o del PR por la plataforma del estudiante. | Checklist de `quality/FINAL_AUDIT.md`. |
| D02 | HITL_MIGUEL | Pegar la URI, revisar y, si procede, hacer merge. | `RUNBOOK_SUPABASE.md` paso 10 y checklist. |
| E01 | PASS | El README de la API tiene la tabla de stock y un curl de registro, login y salida rechazada. | `services/api/README.md`, sección Inventario. |
| E02 | PASS | `with_for_update()` antes de calcular el stock. Dos hilos pidiendo 4 sobre 5 unidades terminan en 201 y 400, y el stock queda en 1. `CHECK (quantity > 0)` rechaza un 0 en la base. | `service.py` línea 105. `models.py` `__table_args__`. Test `test_two_exits_cannot_oversell_the_same_asset`. |
