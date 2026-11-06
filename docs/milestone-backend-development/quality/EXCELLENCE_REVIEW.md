# Revisión de excelencia — 021

Los extras no cambian el enunciado: mismas entidades, mismas rutas, mismo mensaje de stock y la auth TinyDB intacta.

## E01 — Guía de curl y stock sembrado (visible) — IMPLEMENT

Al leer `services/api/README.md` se ve la tabla de los seis SKU con el neto, y un bloque que registra un usuario, entra y pide una salida imposible. La salida esperada es el `400` del briefing.

Evidencia: la sección Inventario de `services/api/README.md`. La misma secuencia, contra el proceso en el puerto 8011, está en `evidence/http-transcript.txt` (alta 201, salida excesiva 400, stock que no se mueve, `user_uuid` del TinyDB).

## E02 — Cierre de fila y tope en la base (técnico) — IMPLEMENT

Antes de decidir una salida, la transacción bloquea la fila del activo con `FOR UPDATE` y solo entonces suma las órdenes. Dos salidas simultáneas de 4 unidades sobre un stock de 5 no pueden quedar las dos escritas: el test espera `201` y `400`, y un stock final de 1.

Además, PostgreSQL rechaza `quantity <= 0` con un `CHECK`, aunque el schema de la API ya pide un entero mayor que cero. El listado de órdenes carga el activo con `selectinload` y el test falla si el listado de 9 órdenes dispara más de 6 `SELECT`.

Evidencia: `services/api/app/inventory/service.py` (`_lock_asset`, `list_orders`), `models.py` (`ck_assetentry_quantity_positive`, `ck_assetexit_quantity_positive`), tests `test_two_exits_cannot_oversell_the_same_asset`, `test_listing_orders_does_not_query_once_per_row` y `test_postgres_enforces_the_foreign_key_and_has_no_user_table`. Corrida: `evidence/pytest-postgres.txt` (169 passed).

## Rechazadas o aplazadas

| Idea | Decisión | Motivo |
| --- | --- | --- |
| Pantalla de inventario y lockup | REJECT | El enunciado es una API. Añadir UI solo para mostrar la marca contradice SIGNAL en proyectos sin frontend. |
| Alembic | DEFER | El enunciado pide `create_all()` en este aprendizaje y avisa de no usarlo en producción. Un migrador no estaba pedido y no sustituye esa llamada. |
| Partir el stock por `office` dentro del mismo activo | REJECT | El briefing define `current_stock` como la suma de todas las entradas menos todas las salidas de ese activo. Cada SKU ya lleva su oficina. |
| Marcar S01/S02 como PASS por el Postgres local | REJECT | El enunciado nombra el Transaction pooler de Supabase. El local demuestra PostgreSQL; no demuestra ese proyecto. |
