# 022 B01 — Supabase (verificación por conector, solo lectura)

022 usa el mismo backend Nexova y las mismas tablas de inventario que 021 (`public.asset`, `assetentry`, `assetexit`) en el proyecto `4geeks-cohorte` (`atraotgdztnrqystnujh`).

## Verificación del 2026-11-12 (autorizada por Miguel, 15:46 CST)

Se corrieron, **solo con SELECT**, las mismas consultas de `check_db.py` a través del conector MCP `user-Supabase` (`execute_sql`). No se creó, alteró ni borró nada para el 022. Detalle en `03-mcp-check.json`.

- Identidad MCP: `current_user=postgres`, `current_database=postgres`, Postgres `17.11`, `now_cst=2026-11-12 15:48:57`. El puerto que ve el MCP es 5432 (API SQL, no el pooler).
- Stock calculado: NXV-IT-001=12, NXV-IT-002=6, NXV-PER-001=20, NXV-PER-002=0, NXV-OFF-001=18, NXV-TRN-001=15. Coincide con `EXPECTED` de `check_db.py`.
- Conteos: asset 6, assetentry 6, assetexit 3. RLS activo en las tres tablas (sin FORCE).
- **Resultado de los datos: PASS.** El camino TCP del Transaction pooler (`*.pooler.supabase.com:6543`) **no se ejecutó** desde la caja (sigue bloqueado, ver `02-box-connect-attempt.txt`). Esa parte de `check_db.py` no es equivalente a una sesión MCP.

## Evidencia previa (2026-11-06)

- `00-migration-applied.sql` y `01-readback.json`: esquema y semilla aplicados el 2026-11-06 con el conector (migración `nexova_021_inventory_schema_seed`). El stock de entonces es el mismo que el de hoy.
- `check_db.py`: script de un comando para una máquina que sí pueda abrir Postgres hacia el pooler. No se corrió desde la caja.
- `02-box-connect-attempt.txt`: timeout al protocolo Postgres desde la caja.

Sin merge, sin LMS, sin push. Sin secretos en estos archivos.
