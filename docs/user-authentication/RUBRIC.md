# Rúbrica — 012 Autenticación y restricción de rutas (Nexova)

Fuente: `content/projects/ai-eng-user-authentication-api` (README en inglés y español). El enunciado manda sobre el encargo y sobre SIGNAL. La base de código es el monorepo ya existente, rama previa `feature/supplier-directory`.

Leyenda: **required** = exigido por el enunciado o por la forma de entrega de este encargo. **extra** = pedido por el encargo y subordinado a la rúbrica.

| ID | Required | Criterio |
| --- | --- | --- |
| R01 | sí | El trabajo vive en el monorepo de Nexova. No se crea otro repositorio. La rama de la feature es `feature/auth-api`. |
| R02 | sí | Las dependencias de auth se instalan con `uv`: `python-jose[cryptography]` y `libpass[bcrypt]`. No se usa `pip install` ni `pipenv` para esas librerías, ni el paquete `passlib` sin mantenimiento. El import sigue siendo `from passlib.hash import bcrypt`. |
| R03 | sí | `User` está en TinyDB y tiene al menos `id`, `email`, `hashed_password`, `is_active`, `role`, `created_at`. El nombre visible y el contacto no se guardan en `User`. |
| R04 | sí | `role` solo acepta `admin`, `manager` o `user` (Enum o validador). `POST /users` crea el rol `user`. |
| R05 | sí | Hay una capa de servicios con crear usuario, obtener por id, obtener por email, actualizar y eliminar. |
| R06 | sí | `POST /users` registra, hashea la contraseña antes de guardar, acepta `name`, `phone` y `address` opcionales y crea el `Profile` en la misma operación. |
| R07 | sí | `GET /users` lista usuarios y está protegida. |
| R08 | sí | `GET /users/{id}` obtiene un usuario y está protegida. |
| R09 | sí | `PUT /users/{id}` actualiza credenciales (`email` y, si aplica, contraseña). El `role` solo cambia si quien llama es `admin`. Solo el propio usuario o un admin. Protegida. |
| R10 | sí | `DELETE /users/{id}` elimina el usuario y el perfil vinculado. Protegida. |
| R11 | sí | `Profile` está en TinyDB, uno a uno con `User` por `user_id`, con al menos `id`, `user_id`, `name`, `phone`, `address`. |
| R12 | sí | `GET /profiles/me` devuelve el perfil del autenticado. Protegida. |
| R13 | sí | `PUT /profiles/me` actualiza `name`, `phone` y `address`. Solo el dueño. Protegida. |
| R14 | sí | `POST /auth/login` acepta email y contraseña, valida credenciales y devuelve un JWT de acceso firmado. |
| R15 | sí | `GET /auth/me` devuelve `email`, `role` y el `Profile` vinculado. Protegida. |
| R16 | sí | `get_current_user` lee `Authorization: Bearer`, decodifica y valida el JWT, carga el usuario y responde `401` si algo falla. |
| R17 | sí | Se usa `OAuth2PasswordBearer` de FastAPI y `python-jose` para firmar. |
| R18 | sí | El JWT lleva como mínimo el `id` de TinyDB del usuario. Ese id es el `user_uuid` que pueden referenciar otros módulos. |
| R19 | sí | `ACCESS_TOKEN_EXPIRE_MINUTES` y el secreto de firma se leen del entorno (fichero `.env` local, no versionado). No hay secreto hardcodeado en el código. |
| R20 | sí | La contraseña se hashea al crear y se verifica en el login. El texto plano no se escribe en TinyDB ni se devuelve en las respuestas. |
| R21 | sí | La autenticación es JWT stateless. No hay sesión de servidor ni cookie de sesión. |
| R22 | sí | No hay tablas de usuario ni de perfil en Supabase, SQLModel ni PostgreSQL. `User` y `Profile` quedan en TinyDB. |
| R23 | sí | Al menos 5 rutas ya existentes, fuera de `/users` y `/auth`, exigen un token válido. Son rutas reales de 009 y 011. No se inventan rutas para llegar al número. |
| R24 | sí | Sin token, con token mal formado o con token expirado, la ruta protegida responde `401`. |
| R25 | sí | Acceder o modificar las credenciales de otro usuario responde `403`, no solo `401`. El perfil solo lo actualiza su dueño. |
| R26 | sí | Con un token válido, las rutas protegidas del monorepo siguen respondiendo como antes. Los tests de 009 y 011 quedan en verde. |
| R27 | sí | Auth bajo `/auth`, usuarios bajo `/users`, perfiles bajo `/profiles`. |
| R28 | sí | El flujo registro → login → copiar token → ruta protegida se puede ejecutar en `/docs`, y queda evidencia de `401` sin token. |
| R29 | sí | Hay un pull request con la nota de qué rutas quedaron protegidas y cómo se verificó. No se hace merge. La base del PR es `feature/supplier-directory` para que el diff sea solo 012; el orden de merge documentado es #9, luego #10, luego este. |
| R30 | sí | `services/api/README.md` explica cómo arrancar con `uv`, las variables de entorno y las rutas protegidas. |
| E01 | extra | Guía ejecutable en Swagger del recorrido registro → login → perfil → 401 → 403. |
| E02 | extra | Tests de expiración, de ownership y de regresión de las rutas protegidas existentes. |
| U01 | sí (encargo) | Si el backoffice llama a rutas que pasan a estar protegidas, sigue siendo usable con un login mínimo. El token vive en `sessionStorage` del navegador y se envía como `Authorization: Bearer`. No es una sesión de servidor. |
| U02 | sí (si hay UI) | Capturas reales a 390, 768 y 1280 px del backoffice con la sesión. |
| U03 | sí (si hay UI) | Lighthouse headless en móvil y en escritorio, con RTT 40 ms y CPU ×1 (preset de escritorio real, sin el throttling móvil). |
| U04 | sí (SIGNAL, UI existente) | Se mantienen tokens, tipografía Arial/Helvetica, estados de carga/error de la sesión, contraste y el lockup ya presente. No se regeneran los SVG. |
