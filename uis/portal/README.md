# Portal interno de Nexova

Aplicación Next.js (App Router) con el flujo de autenticación del ticket AUTH-02. No es una app de login aislada: después de entrar se usa el análisis de tickets, el directorio de proveedores y el perfil. La API es la de `services/api` (entrega 012). No hay claves de terceros.

## Qué vista exige sesión

| Ruta | Sesión |
| --- | --- |
| `/login` | Pública. Enlace «¿Olvidaste tu contraseña?» hacia `/forgot-password`. |
| `/register` | Pública |
| `/forgot-password` | Pública. Pide el correo y muestra siempre la misma confirmación. El formulario se desactiva al enviar. |
| `/reset-password` | Pública. Lee `token` de la query. Si falta, explica cómo pedir otro enlace. |
| `/` | Protegida. Es la vista autenticada principal: análisis de tickets. |
| `/proveedores` | Protegida |
| `/account/profile` | Protegida. Enlaza con el cambio de contraseña. |
| `/account/change-password` | Protegida. Contraseña actual, nueva y confirmación. |

El guard está en `components/SessionGate.tsx`. Lee `localStorage` (`nexova-access-token`) en el cliente. Si no hay token, redirige a `/login`. Si `GET /auth/me` responde `401`, `lib/api.ts` borra el token y abre `/login?reason=expired&next=...`. No hay `middleware.ts`: el middleware de Next.js no puede leer `localStorage`.

El enunciado exige ese almacén. En `content/projects/ai-eng-user-authentication-flows/README.md`, línea 34: «The token must be stored in `localStorage` and attached to every protected API call via the `Authorization: Bearer` header.» La lista de tareas, línea 80, repite: «On login and registration: store the token in `localStorage`.»

Nota. El portal Next.js de `uis/portal` (puerto 3000) guarda el token en `localStorage`. El backoffice del puerto 8000 sigue con el `sessionStorage` de 012: aquel contrato pedía el almacén de la pestaña, y cambiarlo rompería esa entrega. Son orígenes distintos, así que uno no ve la clave del otro.

`lib/api.ts` añade `Authorization: Bearer` en las llamadas protegidas (`/auth/me`, `/profiles/me`, `/suppliers`, `/api/incidents/*`). Login y registro no adjuntan un token viejo: un `401` de credenciales incorrectas no se trata como sesión vencida. Un `401` con token sí redirige a login y la promesa se rechaza, para que el estado de carga no se quede colgado. Las frases salen de `lib/http-messages.ts`: se conserva el texto de la API si es legible y se sustituye una traza, un secreto o un `Unexpected token`. El aviso de error es el mismo en las pantallas (`ErrorBanner`: reintentar, ir al inicio y una línea de soporte) y la espera usa `LoadingState`.

El logout está en la cabecera. Borra la clave y abre `/login`.

## Contraseña

`/forgot-password` llama a `POST /auth/forgot-password`. La frase de confirmación no dice si el correo existe. `/reset-password?token=` llama a `POST /auth/reset-password` y, si sale bien, abre `/login?notice=password-updated`. Un enlace inválido, caducado o ya usado muestra el motivo y un enlace a `/forgot-password`. `/account/change-password` comprueba que la nueva y la confirmación coinciden antes de llamar a la API.

El correo lo envía la API, no este portal. Resend lee `RESEND_API_KEY` en el servidor. Esta copia no tiene esa clave: las pruebas del portal arrancan la API con `EMAIL_TRANSPORT=mock`, que no abre una conexión. Un mock no cuenta como envío real.

## Cómo encaja con el resto del monorepo

El enunciado pide Next.js. Este monorepo no tenía ninguna app Next.js.

- El sitio público (Hito 1) son los HTML de la raíz (`index.html`, `application.html`, `404.html`). No los sirve este portal y no comprueban token.
- El backoffice de 009, 011 y 012 lo sigue sirviendo FastAPI en el puerto 8000 (`/`, `/proveedores`, `/privacidad`). El JWT de esa entrega sigue en `sessionStorage`, como dice la nota de arriba.
- Este portal, en el puerto 3000, es la superficie Next.js. Llama a la misma API y guarda el token en `localStorage`.

## Arranque

Hacen falta Python 3.12, el virtualenv de la API y Node 22.

```bash
cd services/api
uv sync --group dev
```

`services/api/.env` no se versiona. Copia `.env.example` de la API y pon un `JWT_SECRET` de al menos 16 caracteres y `ACCESS_TOKEN_EXPIRE_MINUTES`. Sin esas dos variables la API no arranca.

```bash
cd ../..
export PYTHONPATH=packages:services/api
services/api/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

En otra terminal:

```bash
cd uis/portal
npm install
npm run dev
```

Abre `http://127.0.0.1:3000/login`. `NEXT_PUBLIC_API_URL` vacío significa `http://127.0.0.1:8000` (ver `.env.example`). No hace falta un `.env`.

Producción local:

```bash
cd uis/portal
npm run build
npm run start
```

## Pruebas

Desde la raíz del repositorio, la API y los paquetes:

```bash
services/api/.venv/bin/python -m pytest -q
```

El portal, contra la API real (el secreto de firma se genera en memoria y no se escribe):

```bash
cd uis/portal
npm run build
npx playwright test
```

## Señal visual

Tokens, motion y lockups se copiaron byte a byte desde el paquete SIGNAL. El pie usa el lockup horizontal a 400px desde 640px y el apilado a 280px por debajo. La tipografía es Arial/Helvetica. El crédito del pie no afirma una asociación oficial.
