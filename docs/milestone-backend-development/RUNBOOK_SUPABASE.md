# Runbook — PostgreSQL de inventario y Supabase (Miguel)

Esto no está hecho desde aquí. No hay proyecto Supabase, no se creó una cuenta y no se pegó ninguna URI real. Hasta que completes los pasos, S01 y S02 siguen en `BLOCKED_HITL`. Un mock, SQLite o este PostgreSQL local no los convierten en PASS.

## Lo que ya quedó verificado

En esta máquina hay PostgreSQL 16.15. La API leyó `DATABASE_URL` del entorno (no de un archivo versionado) y pasó CRUD, FK y JWT contra esa base. La evidencia está en `evidence/postgres-inspect.txt` y `evidence/http-transcript.txt`.

Para repetirlo en local, sin Supabase:

```bash
# Crea tú el rol y la base. No subas la contraseña.
cd services/api
uv sync --group dev
export JWT_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
export DATABASE_URL='postgresql+psycopg2://USUARIO:CLAVE@127.0.0.1:5432/nexova_inventory'
export PYTHONPATH=/ruta/al/repo:/ruta/al/repo/packages:/ruta/al/repo/packages/shared:/ruta/al/repo/services/api
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`postgres://` también vale: el proceso lo normaliza a `postgresql+psycopg2://`. Una URI `sqlite:` se rechaza.

Pruebas de integración:

```bash
cd services/api
export NEXOVA_TEST_DATABASE_URL="$DATABASE_URL"
uv run pytest
```

Sin `NEXOVA_TEST_DATABASE_URL` esas pruebas se saltan. El salto no es un PASS de PostgreSQL.

## Pasos para el criterio de Supabase

1. Entra en el proyecto Supabase que ya sea tuyo. No hace falta crear uno nuevo si ya tienes el del curso. Este repositorio no puede hacerlo por ti.
2. Abre **Connect**. El enunciado pide el método **Transaction pooler** y el tipo **URI**. No uses la cadena de sesión (`Session pooler`) ni la conexión directa si el enunciado pide el pooler de transacciones.
3. Copia esa URI. Tiene host `aws-0-….pooler.supabase.com`, puerto **6543** y el parámetro `pgbouncer=true`. No la pegues en el chat, ni en un commit, ni en este runbook.
4. En tu máquina, copia `services/api/.env.example` a `services/api/.env` (ese archivo ya está en `.gitignore`).
5. Rellena solo en ese `.env`:
   - `JWT_SECRET` con un secreto local de al menos 16 caracteres.
   - `ACCESS_TOKEN_EXPIRE_MINUTES=30`.
   - `DATABASE_URL=` la URI del paso 3, sin comillas de más.
6. Arranca la API como arriba, sin exportar `DATABASE_URL` si ya está en `.env`. El proceso no pisa variables que ya vengan del entorno.
7. Comprueba, con un token de `POST /auth/login`:
   - `GET /inventory/products` devuelve los seis SKU y el stock de la tabla del README (`NXV-IT-001` = 12).
   - `POST /inventory/orders/outbound` con cantidad mayor que el stock responde `400` y el texto `Insufficient stock for asset '…'`.
   - En el panel SQL de Supabase, `asset` no tiene columna `current_stock`, y no existen tablas `user` ni `profile`.
8. Si el pooler de transacciones cierra la sesión entre operaciones, la app ya usa `NullPool` cuando la URI lleva `pgbouncer=true` o el puerto `6543`. No cambies eso por un pool con estado.
9. `create_all()` crea las tablas al arrancar. Vale en tu base de aprendizaje. No apuntes esta variable a una base compartida de producción.
10. Cuando eso responda contra el host de Supabase, puedes pasar S01 y S02 a PASS en tu revisión. Hasta entonces siguen `BLOCKED_HITL`.

## Entrega al instructor

Subir el enlace del fork o del pull request a la plataforma del estudiante es el paso D01 (`HITL_ENVIO_MIGUEL`). No se envía desde aquí. El merge del PR es D02 y también es tuyo.
