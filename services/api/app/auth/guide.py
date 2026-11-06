"""Text shown at the top of Swagger UI. The steps use the real routes."""

API_DESCRIPTION = """
API de Nexova. Esta entrega añade autenticación JWT. Las contraseñas viven
hasheadas en TinyDB y el token se firma con el secreto local `JWT_SECRET`.

## Guía ejecutable: registro, sesión, perfil, 401 y 403

Haz los pasos en este orden con **Try it out**. El botón **Authorize** también
sirve para el paso 2: envía el correo en `username` y la contraseña en
`password` (formulario OAuth2). El mismo `POST /auth/login` acepta JSON
`{"email","password"}`.

1. **Registro.** `POST /users` con correo, contraseña (8 caracteres o más) y,
   si quieres, `name`, `phone` y `address`. El rol queda en `user`. La
   respuesta no incluye la contraseña. Anota el `id`.
2. **Login.** `POST /auth/login`. Copia `access_token`. Pulsa **Authorize** y
   pega solo el token (Swagger añade `Bearer`).
3. **Perfil.** `GET /auth/me` devuelve correo, rol y el perfil. `GET /profiles/me`
   devuelve el perfil. `PUT /profiles/me` cambia nombre, teléfono o dirección.
4. **401.** Pulsa **Logout** en Authorize, o no envíes cabecera, y llama a
   `GET /profiles/me` o a `GET /suppliers`. La respuesta es 401. Un token
   cortado o caducado también es 401.
5. **403.** Repite el paso 1 con otro correo. Con el token del primero, llama a
   `PUT /users/{id}` usando el `id` del segundo (por ejemplo cambia el email).
   La respuesta es 403. `GET /users/{id}` y `DELETE /users/{id}` sobre el otro
   usuario también son 403. Cada cual sí puede modificar su propio usuario.

Rutas del monorepo que ahora piden el mismo token: el directorio
`/suppliers` (listar, detalle, alta, tarifa, estado y baja, incluidos los
`POST` de los formularios) y las incidencias `POST /api/incidents/analyze` y
`GET /api/incidents/results/export`.

No hay cookie de sesión. El id del usuario en TinyDB viaja en el JWT como
`sub` y como `user_uuid`.

Recuperación de contraseña: `POST /auth/forgot-password` responde siempre
200 y, si el correo tiene una cuenta activa y el correo transaccional está
configurado, envía un enlace. `POST /auth/reset-password` cambia la
contraseña con ese enlace de un solo uso. `POST /auth/change-password` pide
el token de sesión y la contraseña actual.
""".strip()

OPENAPI_TAGS = [
    {
        "name": "users",
        "description": "Paso 1 y paso 5. Alta pública. El resto exige token y, sobre otro usuario, responde 403.",
    },
    {
        "name": "auth",
        "description": "Paso 2 y paso 3. Login público. `GET /auth/me` exige token. Recuperar y cambiar la contraseña vive en este grupo.",
    },
    {
        "name": "profiles",
        "description": "Paso 3 y paso 4. El perfil autenticado. Sin token responde 401.",
    },
    {
        "name": "suppliers",
        "description": "Directorio de proveedores ya existente. Todas las rutas exigen token.",
    },
    {
        "name": "incidents",
        "description": "Análisis de incidencias ya existente. Analizar y exportar exigen token.",
    },
    {
        "name": "directory-page",
        "description": "Página HTML del directorio. Sin token no incluye tarifas ni contactos.",
    },
    {
        "name": "inventory",
        "description": (
            "Activos, entradas y salidas. El stock se calcula con las órdenes. "
            "Las escrituras exigen token. El user_uuid sale del usuario de TinyDB."
        ),
    },
]
