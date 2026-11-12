# Pruebas de la API de autenticación

Batería de AUTH-088 sobre la API que ya vive en `services/api` (entrega 012) y el portal de `uis/portal` (entrega 013). No hay un repositorio nuevo. Las pruebas comprueban decisiones: a quién se acepta, qué se guarda y qué token vale. No comprueban el tipo de contenido ni el orden de las claves.

Las contraseñas y el secreto de firma que aparecen en los tests son fixtures locales (`clave-segura-1`, `test-jwt-secret-local-only`). No son cuentas reales. `services/api/.env.example` sigue con `JWT_SECRET` vacío.

## Cómo ejecutarlas

La raíz del proyecto FastAPI es `services/api`. El enunciado pide `uv run pytest` desde esa raíz («All tests must pass when running `uv run pytest` from the project root», en el apartado FastAPI, justo después de «at the root of your FastAPI project»). No hay un `pyproject.toml` en la raíz del monorepo.

```bash
cd services/api
uv sync --group dev
uv run pytest
uv run pytest --cov
```

`uv run pytest` tiene que terminar en verde. Recoge `services/api/tests` y `packages/incident_analysis/tests`. `uv run pytest --cov` mide `app.auth` y falla si baja del 70% (configuración en `services/api/pyproject.toml`).

Desde la raíz del monorepo, sin otro proyecto uv:

```bash
make test
make test-cov
```

El gestor de incidencias añade `services/api/tests/test_incident_seed.py` y `test_incident_manager.py` a esa misma batería: seeder idempotente y mapa CSV → modelo. `packages/shared` está en el `pythonpath` de pytest.

Cobertura de los extras, también desde `services/api`:

```bash
uv run pytest --cov=directory --cov=routes.suppliers --cov=app.routers.incidents --cov=incident_analysis.engine --cov-report=term-missing --cov-fail-under=60
```

Portal, aparte:

```bash
cd uis/portal
npm install
npx jest --coverage
```

Los nueve tests de Playwright que ya tenía el portal no forman parte de esta batería. Siguen en `uis/portal/e2e` y se lanzan con `npx playwright test` después de `npm run build`.

## Plan por endpoint

Cada fila es una decisión. El camino feliz es la entrada válida. El caso límite es el borde (vacío, duplicado, longitud, un solo registro). El fallo es la credencial mala, el token inservible o la petición que no se puede interpretar.

| Endpoint | Camino feliz | Caso límite | Fallo |
| --- | --- | --- | --- |
| `POST /users` | Rol `user`, perfil creado, la contraseña solo se guarda como hash. | El correo se normaliza. Nombre, teléfono y dirección en blanco quedan vacíos. Ocho caracteres es la contraseña más corta. | Correo duplicado (409). Correo mal formado. Contraseña vacía o con espacios en el borde. El cuerpo no puede elegir el rol. |
| `POST /auth/login` | Token firmado. `sub` y `user_uuid` son el id de TinyDB. `expires_in` sale de `ACCESS_TOKEN_EXPIRE_MINUTES`. | El formulario de Swagger (`username`) acepta el correo en mayúsculas. Una contraseña hecha solo de espacios no está vacía: pasa la validación y falla el acceso. | Correo desconocido y contraseña incorrecta devuelven la misma frase. Cuenta inactiva, igual. Contraseña vacía: 422 antes de buscar la cuenta. Un JSON que no es un objeto: 422. Sin `JWT_SECRET` no se firma un token. |
| `GET /auth/me` | Devuelve el usuario del token y su perfil, sin el hash. | Un token caducado se rechaza y otro emitido antes sigue valiendo. Si cambia `AUTH_DATA_DIR`, ese token ya no encuentra a nadie. | Sin token, token mal formado, token firmado con otro secreto, o `user_uuid` distinto de `sub`. Usuario desactivado o borrado. Usuario sin perfil: 404. |
| `GET /users` | La lista sale por `created_at` y no incluye el hash. | Con una sola cuenta, la lista es esa cuenta. Antes de registrar a nadie, el servicio devuelve una lista vacía. | Sin token, 401. |
| `GET /users/{id}` | El propio usuario ve sus credenciales y el perfil, sin el hash. | Un admin puede leer otra cuenta y tampoco recibe el hash. | Otro usuario: 403. Id desconocido: 404. Sin token: 401. |
| `PUT /users/{id}` | Cambiar el correo y la contraseña. La contraseña anterior deja de entrar. | El mismo correo no es un conflicto. Un cuerpo vacío es «No hay cambios». Ocho caracteres sustituyen la contraseña. | Un `user` no cambia su rol ni `is_active`, ni la cuenta de otro. Contraseña corta: no se guarda. Correo ya usado: 409. Un admin sí cambia el rol. Id desconocido: 404. |
| `DELETE /users/{id}` | Borra la cuenta y el perfil. El login posterior es 401. | Un admin borra a otra persona y su propio token sigue valiendo. | Otro usuario: 403. Id desconocido: 404. Sin token: 401. |
| `GET /profiles/me` | Devuelve nombre, teléfono y dirección de quien llama. | Sin datos de contacto, los tres campos van vacíos. La respuesta no lleva el correo ni el hash. | Sin token o con un token mal formado: 401, y el cuerpo no incluye el teléfono. |
| `PUT /profiles/me` | Actualiza nombre, teléfono y dirección. | Un nombre en blanco lo borra. Los campos que no vienen se quedan. El teléfono se corta a 40 caracteres. | Cuerpo vacío: «No hay cambios». Un campo de más no se aplica. Sin token no se escribe. |

Módulos: `services/api/tests/test_register.py`, `test_login.py`, `test_token.py`, `test_list_users.py`, `test_read_user.py`, `test_update_user.py`, `test_delete_user.py`, `test_read_profile.py`, `test_update_profile.py`.

## Por qué estos casos

El registro y el login son públicos. El resto exige un token y, sobre otra persona, un admin. Esos dos ejes (¿hay sesión? ¿es el dueño?) cubren los 401 y los 403. Los bordes de contraseña (8 caracteres, 72 bytes, espacios) están en el modelo, no en el hash: el hash no decide la política. El token se juzga por lo que `decode_access_token` acepta (`sub`, `user_uuid`, caducidad) y por si esa persona sigue activa en TinyDB.

## Resultado medido

`cd services/api && uv run pytest`: 96 passed. De esas, 45 ya estaban (incidencias, directorio y autenticación de las entregas anteriores) y siguen en verde.

`cd services/api && uv run pytest --cov` sobre `app.auth`:

| Módulo | Cobertura |
| --- | --- |
| `app.auth` (paquete) | 95% (433 sentencias, 20 sin cubrir). Umbral 70%. |
| `app.routers.auth` | 100% |
| `app.routers.users` | 98% |
| `app.routers.profiles` | 82% |

Las líneas que faltan en perfiles son comprobaciones defensivas (`user_id` distinto del que se acaba de buscar). La consulta ya filtra por ese id, así que no salen en un uso normal.

## Bug que destapó la batería

`POST /users` con un correo repetido respondía 409, y `POST /auth/login` con la contraseña vacía respondía 422, pero el JSON decía «No se pudo completar la solicitud.» El router ya había elegido la frase («Ya existe una cuenta con ese correo.», «La contraseña es obligatoria.», «No hay cambios.»). `_error_content` en `services/api/app/main.py` solo conservaba el detalle en 401 y 403.

Ahora un 4xx con una frase propia del router conserva esa frase. Las frases inglesas de Starlette (`Not Found`, `Method Not Allowed`) siguen traduciéndose: un 404 de ruta desconocida sigue siendo «No encontrado.». Un 500 no copia el detalle, para no devolver el texto de una excepción interna.

## Flujo con el agente

El plan de la tabla salió de leer los routers y `app.auth.service`. Después de ese plan, la lectura de `authenticate` y `decode_access_token` añadió tres casos que no estaban en la lista de rutas:

- Correo desconocido y contraseña incorrecta tienen que devolver la misma frase. El servicio compara contra un hash ficticio cuando el correo no existe, para no delatar si la cuenta está dada de alta.
- Un token con `user_uuid` distinto de `sub` no es una sesión, aunque la firma sea buena.
- Una contraseña de solo espacios no está vacía para el login. El registro sí rechaza los espacios del borde. En el login la decisión es 401, no 422.

El cuarto hallazgo es el bug del apartado anterior. No había un fallo de caducidad en el código de firma: el token caducado se rechaza y el que se emitió antes sigue valiendo.

## Extra API-042 — backoffice

Dos grupos que no son la autenticación: el directorio de proveedores y el análisis de incidencias. Misma estructura de tres niveles, en `test_backoffice_suppliers.py` y `test_backoffice_incidents.py`.

| Grupo | Camino feliz | Caso límite | Fallo |
| --- | --- | --- | --- |
| `POST/GET/DELETE /suppliers` | Un contrato de Spain se guarda en EUR. | El filtro por categoría deja fuera al resto. La tarifa 0,01 entra; 0 no. | Id desconocido: 404. Spain con USD no se inserta. |
| `POST /api/incidents/analyze` y export | Un ticket cerrado cuenta y el correo del cliente no sale en el informe. | Una descripción de 5 caracteres vale; una de 4 no. La nota de un ticket abierto no entra en la media. | Sin fichero, fichero vacío, o export sin análisis previo. |

Cobertura medida con la batería completa:

| Módulo | Cobertura |
| --- | --- |
| `directory` | 96% |
| `routes.suppliers` | 68% |
| `app.routers.incidents` | 100% |
| `incident_analysis.engine` | 93% |

Los dos grupos quedan por encima del 60%. En proveedores, lo que falta es sobre todo el camino HTML de los formularios. Estas pruebas miran la decisión (moneda, filtro, tarifa, id ausente), no el HTML.

## Extra FE-019 — utilidades del portal

Jest está en `uis/portal/jest.config.ts`. Los tests están en `uis/portal/__tests__/`. `npx jest --coverage`: 15 passed. Sentencias de `lib/forms.ts`, `lib/paths.ts` y `lib/session.ts`: 100%.

| Función | Camino feliz | Fallo |
| --- | --- | --- |
| `writeToken` / `readToken` | Guardan `nexova-access-token` y lo leen. | Si `localStorage` lanza o no devuelve el mismo valor, `writeToken` es `false`. Sin `window`, `readToken` es `""`. |
| `clearToken` | Borra la clave. | Si `removeItem` lanza, la función no propaga el error. |
| `emailError` | `ANA@Nexova.test` con espacios es válido. | Sin dominio, sin `@`, o con un espacio dentro: formato no válido. |
| `passwordError` | Ocho caracteres entran. 36 «á» (72 bytes) entran. | Siete caracteres, espacios en el borde, o más de 72 bytes. |
| `textLimit` | Un texto dentro del límite no produce error. | Por encima del límite, el mensaje nombra el campo y el tope. |
| `safeNext` | `/proveedores?country=Spain` y `/account/profile` se conservan. | `null`, una URL absoluta, `//host`, un `%2F%2F` codificado, un `%` suelto o una ruta que no está en la lista vuelven a `/`. |
| `apiBase` | Una URL con barra final se queda sin esa barra. | Variable ausente o en blanco: `http://127.0.0.1:8000`, no una ruta relativa. |

`apiBase` vive en `lib/api.ts`. El resto de ese módulo habla con `fetch` y lo ejercitan los tests de Playwright, no esta batería.
