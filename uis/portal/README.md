# Portal interno de Nexova

Aplicación Next.js (App Router) con el flujo de autenticación del ticket AUTH-02. No es una app de login aislada: después de entrar se usa el análisis de tickets, el directorio de proveedores y el perfil. La API es la de `services/api` (entrega 012). No hay claves de terceros.

## Qué vista exige sesión

| Ruta | Sesión |
| --- | --- |
| `/login` | Pública |
| `/register` | Pública |
| `/` | Protegida. Es la vista autenticada principal: análisis de tickets. |
| `/proveedores` | Protegida |
| `/account/profile` | Protegida |

El guard está en `components/SessionGate.tsx`. Lee `localStorage` (`nexova-access-token`) en el cliente. Si no hay token, redirige a `/login`. Si `GET /auth/me` responde `401`, `lib/api.ts` borra el token y abre `/login?reason=expired&next=...`. No hay `middleware.ts`: el middleware de Next.js no puede leer `localStorage`.

`lib/api.ts` añade `Authorization: Bearer` en las llamadas protegidas (`/auth/me`, `/profiles/me`, `/suppliers`, `/api/incidents/*`). Login y registro no adjuntan un token viejo: un `401` de credenciales incorrectas no se trata como sesión vencida.

El logout está en la cabecera. Borra la clave y abre `/login`.

## Cómo encaja con el resto del monorepo

El enunciado pide Next.js. Este monorepo no tenía ninguna app Next.js.

- El sitio público (Hito 1) son los HTML de la raíz (`index.html`, `application.html`, `404.html`). No los sirve este portal y no comprueban token.
- El backoffice de 009, 011 y 012 lo sigue sirviendo FastAPI en el puerto 8000 (`/`, `/proveedores`, `/privacidad`). Allí el JWT de 012 vive en `sessionStorage` de ese origen. Cambiarlo rompería el contrato de aquella entrega. `localStorage` no se comparte entre el puerto 3000 y el 8000.
- Este portal, en el puerto 3000, es la superficie Next.js. Llama a la misma API.

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
