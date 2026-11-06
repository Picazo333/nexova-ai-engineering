# Justificación — 015 ai-eng-company-monorepo-container

Base `feature/user-authentication-restore` (`d69a3b9`). El fork es Nexova. El portal Next.js sigue en `uis/portal`; `uis/website` lo arranca en el puerto 3000. El HTML estático de `uis/backoffice` sigue sirviéndolo la API. El proceso Next del puerto 3001 convive en esa carpeta y no sustituye esos ficheros.

| ID | Estado | Cómo se cumple | Evidencia |
| --- | --- | --- | --- |
| R01 | PASS | La rama sale de `d69a3b9`. No hay repositorio nuevo. | `git log -1` de la base. `rubric/RUBRIC.md`. |
| R02 | PASS | `uis/Dockerfile` parte de `node:22-alpine` en tres etapas de dependencias y una de ejecución. | `uis/Dockerfile`. |
| R03 | PASS | `npm ci` separado para `website`, `portal` y `backoffice`. | `uis/Dockerfile` etapas `website-deps`, `portal-deps`, `backoffice-deps`. |
| R04 | PASS | El `CMD` es `sh /app/start.sh`. Ese script lanza `npm run dev` en `/app/website` (portal, puerto 3000) y en `/app/backoffice` (puerto 3001). | `uis/Dockerfile`, `uis/start.sh`, `uis/website/package.json`. |
| R05 | PASS | `uis/.dockerignore` incluye `node_modules`, `.next`, `.env*` y `*.log`. | `uis/.dockerignore`. |
| R06 | PASS | `services/Dockerfile` parte de `python:3.12-slim-bookworm`. 3.12 es la versión con la que la API ya pasa la suite. | `services/Dockerfile`. |
| R07 | PASS | La etapa `uv` copia el binario `0.13.7`. El `RUN` es `uv pip install --system --no-cache -r requirements.txt`. | `services/Dockerfile`, `services/requirements.txt`. |
| R08 | PASS | El `CMD` de la API incluye `--reload` y `--reload-dir /app/services/api`. | `services/Dockerfile`. |
| R09 | PASS | `services/.dockerignore` incluye `__pycache__`, `*.pyc`, `.env*`, `tests/` y `*.log`. | `services/.dockerignore`. |
| R10 | PASS | `docker-compose.yml` construye `uis` y `services`, monta el código y deja el `CMD` con `next dev` y `--reload`. Qdrant se mantiene: el monorepo ya lo declaraba. | `docker-compose.yml`. |
| R11 | PASS | Publica 3000, 3001 y 8000. Qdrant publica 6333 y 6334, como antes. | `docker-compose.yml`. `evidence/compose-ps.txt`. |
| R12 | PASS | Red `monorepo-dev` con `name: monorepo-dev`. | `docker-compose.yml`. |
| R13 | PASS | `API_INTERNAL_URL=http://services:8000` y `QDRANT_URL=http://qdrant:6333`. Desde el contenedor de interfaces, `wget http://services:8000/health` respondió `{"status":"ok"}`. El panel muestra `services:8000`. La API abre `http://qdrant:6333/readyz` con 200. El navegador usa los puertos del host porque no resuelve el DNS de Docker. | `.env.example`. `evidence/stack-internal.json`. `evidence/container-success-1280.png`. |
| R14 | PASS | Los Dockerfile, el Compose y los scripts no asignan claves. La prueba de contrato lo recorre. | `tests/infra/test_compose_contract.py`. |
| R15 | PASS | `env_file: .env`. El YAML no fija `JWT_SECRET` ni otras claves. `make up` rellena el `.env` local si falta y no imprime el valor. | `docker-compose.yml`. `scripts/ensure_compose_env.py`. `Makefile`. |
| R16 | PASS | `.gitignore` contiene `.env`. `git log --all -- .env` está vacío. `git check-ignore` lo confirma en la prueba. | `.gitignore`. `tests/infra/test_compose_contract.py`. |
| R17 | PASS | `docker compose up -d --wait` dejó los tres servicios en marcha. La UI y la API quedaron `healthy`. El `.env` es el paso que el enunciado ya pide; `make up` lo crea. | `evidence/compose-ps.txt`. |
| R18 | PASS | Sin reconstruir la imagen, un cambio en el panel se vio en el puerto 3001 a los 3 s y un cambio en `/health` a 1 s. Los dos ficheros volvieron a su texto. | `evidence/hot-reload.txt`. |
| R19 | PASS | Un contenedor (`uis`) escucha 3000 y 3001. El 3000 es el portal existente. La API FastAPI es el servicio `services`. | `evidence/compose-ps.txt`. `curl` de `/login` en 200. |
| R20 | PASS | Multi-stage en los dos Dockerfile. `USER node` y `USER app` (uid 1000). Healthcheck de la UI (3000 y 3001) y de la API (`/health`). `docker compose exec` mostró uid 1000. | `uis/Dockerfile`. `services/Dockerfile`. `docker-compose.yml`. |
| R21 | PASS | `.env.example` deja `JWT_SECRET`, `RESEND_API_KEY`, `SENDGRID_API_KEY` y las claves de modelos vacías. | `.env.example`. |
| P01 | BLOCKED_HITL | No hay acceso SSH ni autorización de Miguel para desplegar. No se inventa una URL. | `docs/container/RUNBOOK.md`. |
| D01 | PASS | El PR lleva `docker compose ps` y la salida de los contenedores locales. | `evidence/compose-ps.txt`. |
| D02 | BLOCKED_HITL | No hay `docker compose ps` por SSH ni captura del VPS. El runbook deja los comandos exactos. | `docs/container/RUNBOOK.md`. |
| D03 | HITL_ENVIO_MIGUEL | Compartir el PR con el tech lead o el instructor es un envío humano. | Checklist de `quality/FINAL_AUDIT.md`. |
| D04 | HITL_MIGUEL | El enunciado pide merge a `main` tras la aprobación. Esta ejecución no hace merge. | `quality/FINAL_AUDIT.md`. |
| H01 | HITL_MIGUEL | Confirmar el SSH y autorizar el despliegue es una acción de Miguel. | `docs/container/RUNBOOK.md`. |
| U01 | PASS | El panel usa `tokens.css` y `motion.css` ya hasheados, Arial/Helvetica, y muestra carga, vacío, éxito y error. | `uis/backoffice/app/globals.css`. `evidence/container-loading-768.png`, `container-empty-390.png`, `container-success-1280.png`, `container-error-390.png`. |
| U02 | PASS | Capturas reales a 390, 768 y 1280 del panel en producción (`next start` en el puerto 3011, con la API publicada). | Serie `evidence/container-*-{390,768,1280}.png`. |
| U03 | PASS | `evidence/container-recorrido.webm` dura 6,60 s. Entra al panel, escribe en el filtro y baja al pie. | `ffprobe`. |
| U04 | PASS | Con `prefers-reduced-motion`, la duración computada del panel es `0s`. | `evidence/container-reduced-motion.txt`. `evidence/container-reduced-1280.png`. |
| U05 | PASS | El pie usa el lockup horizontal a 400 px desde 640 px y el apilado a 280 px por debajo. El SHA-256 del horizontal servido coincide con `85459232bf51e7bf7c94225fd4f2cd6b71a681b6d701cb4ffd6d2a142cf57a81`. | `evidence/container-lockup-hashes.txt`. `uis/backoffice/components/FooterLockup.tsx`. |
| U06 | PASS | Lighthouse 12.6.0, tres móvil y tres escritorio, `simulate`. Móvil 390×844, RTT 150, 1638,4 kbps, CPU ×4: mediana LCP 1889 ms, peor 1890 ms, CLS 0,0024, TBT 14 ms. Escritorio RTT 40, 10240 kbps, CPU ×1: mediana LCP 459 ms, peor 481 ms, CLS 0,005, TBT 0. INP no lo mide el laboratorio; la cifra de bloqueo es TBT. | `evidence/container-lighthouse-summary.json`. JSON completos en `/opt/cursor/artifacts/lighthouse/`. |
| U07 | PASS | Skip link, etiqueta visible del filtro, foco del token, `noindex`, 404 real y axe sin serious/critical en éxito, error y 404. | `uis/backoffice/app/layout.tsx`. `evidence/container-404-1280.png`. `evidence/container-axe.json`. |
| U08 | PASS | El script de captura aborta si `scrollWidth` supera al ancho del documento. Las 14 tomas pasaron. | `uis/portal/scripts/capture-container.mjs`. |
| U09 | NO_APLICA | El panel es interno. No hay landing pública nueva, ni canonical, ni sitemap. | `uis/backoffice/app/layout.tsx` (`robots: noindex`). |
| X01 | PASS | `make up` imprime las tres URLs. El panel muestra el host interno `services:8000`. | `Makefile`. `evidence/container-success-1280.png`. |
| X02 | PASS | Pytest del contrato de Compose, healthchecks y la sonda de recarga. | `tests/infra/test_compose_contract.py`. `evidence/hot-reload.txt`. `services/api/tests/test_health.py`. |

30/30 criterios que cuentan: PASS.
