# API de Nexova

Un solo proceso FastAPI, como pide `services/README.md`. Sirve el análisis de incidencias, el directorio de proveedores y la autenticación JWT de usuarios y perfiles.

## Incidencias

El router `app/routers/incidents.py` solo traduce HTTP. Las reglas del CSV están en `packages/incident_analysis` y son las mismas que usa `scripts/analyze.py`.

Las rutas de este entregable son las del enunciado, no un prefijo distinto:

- `POST /api/incidents/analyze` — CSV en `multipart/form-data`, campo `file`.
- `GET /api/incidents/results/export` — último análisis correcto, `results.csv`.

Con `Accept: application/json` el análisis responde JSON. Con `Accept: text/html` responde la página del backoffice. El navegador pide un fragmento con la cabecera `X-Report-Fragment: 1`.

No llama a ningún servicio de IA. No guarda el CSV. Guarda el resumen agregado en `services/api/.data/` (ignorado por git) para que la descarga sobreviva a un refresco. Si ese resumen contuviera `@`, no se escribe.

Errores de entrada: fichero ausente, vacío, sin filas, codificación o columnas incorrectas → `400` con `error` y `message`. Por encima de `INCIDENTS_MAX_UPLOAD_BYTES` (32 MiB por defecto) → `413`. Export sin análisis previo → `404`. Un fallo interno no incluye la excepción en la respuesta.

## Arranque

Desde la raíz del repositorio, con Python 3.12. Las dependencias de autenticación se instalan con `uv`, no con `pip install` ni con `pipenv`:

```bash
cd services/api
uv sync --group dev
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Pega el valor en `JWT_SECRET` dentro de `services/api/.env`. Ese fichero no se versiona. `ACCESS_TOKEN_EXPIRE_MINUTES` ya viene en el ejemplo (30). Sin esas dos variables el proceso no arranca y el código no trae un secreto de reserva.

```bash
cd ../..
export PYTHONPATH=packages:services/api
services/api/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

El proceso carga `services/api/.env` y no pisa variables que ya estén en el entorno. Abre `http://127.0.0.1:8000`. La guía de Swagger está en `http://127.0.0.1:8000/docs`.

## Pruebas

```bash
cd services/api
uv sync --group dev
cd ../..
services/api/.venv/bin/python -m pytest -q
```

CI instala `services/api/requirements.txt`, que fija las mismas versiones de `python-jose` y `libpass`.

## Directorio de proveedores

TinyDB local, sin claves externas. Los 15 contratos iniciales salen de `scripts/nexova-supplier-BRIEFING.es.md` (syllabus `content/contexts/supplier-directory/nexova-BRIEFING`). Los campos estructurados coinciden con la versión en inglés; las notas están en español, como el backoffice. No son un directorio genérico.

Al arrancar, la API ejecuta el seeder si `SUPPLIERS_AUTOSEED` no es `0`. Repetirlo no duplica nombres.

```bash
cd services/api
uv run seed
```

La consola imprime `Se insertaron N registros.`

| Método | Ruta | Resultado |
| --- | --- | --- |
| `POST` | `/suppliers` | Alta. `201` y el objeto con `id`. `422` si el cuerpo no cumple el modelo. |
| `GET` | `/suppliers` | Listado. Filtros opcionales `country`, `category` y `status`. |
| `GET` | `/suppliers/{id}` | Detalle, o `404`. |
| `PATCH` | `/suppliers/{id}/rate` | Cambia `monthly_rate` y reescribe `updated_at`. Rechaza tarifas ≤ 0. |
| `PATCH` | `/suppliers/{id}/status` | `active` o `suspended`. Cualquier otro valor es `422`. |
| `DELETE` | `/suppliers/{id}` | Elimina. `404` si el id no existe. |

`updated_at` lo escribe el servidor. Un proveedor de `Spain` tiene que usar `EUR` y uno de `USA`, `USD`. La página del directorio está en `/proveedores` (el path `/suppliers` es la API). Los formularios HTML usan `POST` y redirigen; la interfaz con JavaScript llama a `PATCH`.

## Autenticación

`User` y `Profile` están solo en TinyDB (`auth.json`, tablas `users` y `profiles`). No hay tablas de usuario en SQLModel, Supabase ni PostgreSQL. El id de TinyDB viaja en el JWT como `sub` y como `user_uuid`.

La contraseña se hashea con `libpass` (import `from passlib.hash import bcrypt`) antes de guardarla. El login compara con ese hash. La respuesta nunca incluye `hashed_password` ni la contraseña en claro.

No hay cookie ni sesión de servidor. El cliente envía `Authorization: Bearer <token>`.

| Método | Ruta | Quién |
| --- | --- | --- |
| `POST` | `/users` | Pública. Rol `user`. Acepta `name`, `phone` y `address` y crea el perfil. |
| `GET` | `/users` | Token. Lista sin el hash. |
| `GET` | `/users/{id}` | Token. El propio usuario o un admin. Si no, `403`. |
| `PUT` | `/users/{id}` | Token. Credenciales. El rol y `is_active` solo los cambia un admin. Si no es el dueño ni admin, `403`. |
| `DELETE` | `/users/{id}` | Token. Borra también el perfil. Mismas reglas de dueño o admin. |
| `POST` | `/auth/login` | Pública. JSON `email`/`password` o formulario `username`/`password` (botón Authorize de Swagger). |
| `GET` | `/auth/me` | Token. Correo, rol y perfil. |
| `GET` | `/profiles/me` | Token. |
| `PUT` | `/profiles/me` | Token. Solo el perfil de quien llama. |

Sin token, con un token mal formado o con un token caducado, la ruta protegida responde `401`.

### Rutas que ya existían y ahora piden token

Son 10, todas fuera de `/users` y `/auth`:

- `GET /suppliers`
- `GET /suppliers/{id}`
- `POST /suppliers`
- `PATCH /suppliers/{id}/rate`
- `POST /suppliers/{id}/rate`
- `PATCH /suppliers/{id}/status`
- `POST /suppliers/{id}/status`
- `DELETE /suppliers/{id}`
- `POST /api/incidents/analyze`
- `GET /api/incidents/results/export`

`GET /proveedores` sigue siendo la página. Sin cabecera `Authorization` no pinta tarifas ni contactos: muestra el formulario de sesión. Con token, el HTML es el de antes. El backoffice guarda el JWT en `sessionStorage` de la pestaña y lo manda en `Authorization`. Eso no es una cookie de sesión.

En `/docs`, la descripción de la API es una guía en cinco pasos: registro, login, perfil, 401 y 403.

## Variables

| Variable | Defecto | Uso |
| --- | --- | --- |
| `INCIDENTS_DATA_DIR` | `services/api/.data` | Carpeta del último resumen |
| `INCIDENTS_MAX_UPLOAD_BYTES` | `33554432` | Tope del CSV |
| `INCIDENTS_CORS_ORIGINS` | localhost en los puertos 8000 y 3000 | Orígenes permitidos, lista separada por comas. Sin credenciales y sin comodín. |
| `SUPPLIERS_DATA_DIR` | `services/api/.data` | Carpeta de `suppliers.json`. |
| `SUPPLIERS_AUTOSEED` | `1` | `0` arranca sin cargar el briefing. |
| `JWT_SECRET` | ninguna | Secreto de firma. Obligatorio, mínimo 16 caracteres, solo en `.env` o en el entorno. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ninguna | Minutos de vida del JWT. Obligatorio. |
| `AUTH_DATA_DIR` | `services/api/.data` | Carpeta de `auth.json`. |
| `AUTH_BCRYPT_ROUNDS` | `12` | Coste bcrypt. Las pruebas usan `4`. |

## Portal Next.js

`uis/portal` es el frontend de los flujos de autenticación. Corre en el puerto 3000 y llama a esta API en el 8000. El JWT va en `localStorage` del origen del portal y en la cabecera `Authorization`. El backoffice que sirve esta API en `/` y `/proveedores` no cambia: sigue usando `sessionStorage` de esa otra origen. El sitio público de la raíz del repositorio no pasa por aquí.
