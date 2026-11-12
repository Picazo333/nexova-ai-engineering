# 021 — Supabase live (proyecto 4geeks-cohorte, atraotgdztnrqystnujh)

Aplicado el 2026-11-06 ~11:58 CST con el conector de Supabase (apply_migration `nexova_021_inventory_schema_seed`), por autorización literal de Miguel (11:52 CST). Sin merge y sin LMS.

- `00-migration-applied.sql`: DDL generado desde los modelos SQLModel de `106083a` (`app/inventory/models.py`, dialecto postgresql) más la semilla de `app/inventory/seed.py`. Esquema `public`, que es el valor por defecto de `INVENTORY_SCHEMA`, así que `create_all` y `seed_if_empty` de la app no duplican nada. RLS activado en las tres tablas: la app conecta como `postgres`, que lo ignora, y la API REST anónima no las expone.
- `01-readback.json` (execute_sql): Postgres 17.11; tablas `asset`, `assetentry`, `assetexit`; sin columna `current_stock`; sin tablas user/profile; FK de entradas y salidas hacia asset; stock calculado NXV-IT-001=12, IT-002=6, PER-001=20, PER-002=0, OFF-001=18, TRN-001=15 (igual a `EXPECTED_STOCK`); CHECK quantity>0 y FK rechazan inserciones de prueba, 0 filas residuales.
- `02-box-connect-attempt.txt`: arranque real de la API con `DATABASE_URL` del Transaction pooler (6543) desde la caja. Timeout: la red de la caja bloquea el protocolo Postgres. No cuenta como conexión.
- `check_db.py`: verificación de un comando para Miguel, en su máquina. Sale 0 solo si conecta por el pooler 6543 y el stock coincide.

Estados: S01 (URI real con Transaction pooler) y S02 (conexión a un proyecto Supabase alojado) quedan HITL_MIGUEL hasta que `check_db.py` salga 0 en su máquina. El esquema y la semilla en el proyecto alojado ya están verificados.
