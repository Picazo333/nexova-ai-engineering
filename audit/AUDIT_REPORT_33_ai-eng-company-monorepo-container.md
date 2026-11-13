# Informe de auditoría adversaria — actividad 33

- **Auditor:** Rodrigo Salcedo (independiente; no es el autor)
- **Fecha:** 13 de noviembre de 2026, 10:52 CST (America/Mexico_City, UTC-6)
- **Slug:** `ai-eng-company-monorepo-container`
- **Tarea LMS:** 1022000 (GET 13 nov 2026: `PENDING`, `github_url` vacío)
- **Repo / PR:** [Picazo333/nexova-ai-engineering#22](https://github.com/Picazo333/nexova-ai-engineering/pull/22)
- **Rama:** `feature/company-monorepo-container`
- **Head auditado:** `bcd9ba615bc815d628c0cef291e5f5b2dc17d774` (13 nov 2026, 10:42:02 CST; documentación de ESTADO sobre el checkpoint `f4c4ac2`)
- **Fuente de criterios:** enunciado oficial `/workspace/ejecucion/015-ai-eng-company-monorepo-container/source/OFFICIAL_README.md` @ syllabus `fd2da034`, casillas de «What We Will Evaluate».
- **Alcance:** inspección de Dockerfiles, Compose, `.dockerignore`, red y secretos; tests de contrato e API; historial de `.env`. Sin merge, sin LMS, sin créditos. Este sandbox **no tiene CLI de Docker**: no se relanzó `docker compose up` en vivo (limitación del entorno, no del trabajo). El test de compose renderizado se salta cuando no hay Docker, por diseño.

## Veredicto

**PASA** (READY). Criterios oficiales que no son HITL: PASS. El despliegue en el VPS es **HITL** (cuenta/host de Miguel, runbook completo, sin URL inventada) y **no es GRAVE**. 0 GRAVE. Solo GRAVE bloquea.

HITL abiertos, no restan: VPS, envío al LMS, merge. El PR está `mergeable_state=dirty` porque la base se movió hoy al añadir el checkpoint (H2, MENOR).

## Criterios oficiales

| Criterio | Dictamen | Evidencia |
|---|---|---|
| `docker compose up` desde la raíz arranca la plataforma. | **PASS** con nota MENOR | `docker-compose.yml`: servicios `uis` (target `dev`, puertos 3000 y 3001), `services` (Uvicorn `--reload`, puerto 8000) y `qdrant` (ya lo usaba el monorepo; puertos solo en `127.0.0.1`). Red explícita `monorepo-dev`. Bind mounts en UI y API. `Makefile` `up` = `ensure_compose_env.py` + `docker compose up --build`. Ver H1: sin ese paso, `JWT_SECRET` vacío rompe el login, no el healthcheck. No se relanzó Compose en vivo aquí. Evidencia del autor en el PR y en `evidence/`. |
| Los cambios en el host se reflejan sin reconstruir (bind mounts). | **PASS** (estático) | Volúmenes `./uis:/app` y `.:/app` en el servicio API; volúmenes nombrados para `node_modules`. `start.sh` usa `npm run dev`; la API lanza `--reload --reload-dir /app/services/api`. |
| Un solo contenedor UI levanta las dos apps Next en 3000 y 3001. | **PASS** | `uis/Dockerfile` `CMD ["sh", "/app/start.sh"]`, imagen `node:22-alpine`. `start.sh` arranca `/app/website` (shim que delega en `uis/portal`, puerto 3000) y `/app/backoffice` (3001). Dependencias de `website`, `portal` y `backoffice` se instalan en etapas separadas (`npm ci`). |
| Comunicación interna por nombre de servicio, no `localhost`. | **PASS** | `.env.example`: `API_INTERNAL_URL=http://services:8000`, `QDRANT_URL=http://qdrant:6333`. Los `127.0.0.1` de healthcheck son el loopback del propio contenedor; `NEXT_PUBLIC_*` apuntan al host porque el navegador no resuelve DNS de Docker. `test_internal_url_helper_rejects_localhost` pasa. |
| Sin secretos en Dockerfile ni en `docker-compose.yml`. | **PASS** | Lectura completa de ambos y de `docker-compose.prod.yml`. Variables vía `env_file: .env` (`required: false`). Escaneo sin claves reales. |
| `.env` en `.gitignore` y ausente del historial. | **PASS** | `.gitignore` L14: `.env`. Índice: no está. API GitHub `path=.env` (y variantes): 0 commits. El test de historial falló solo en este clone parcial (H3). |
| Existen `.dockerignore` en `/uis/` y `/services/`. | **PASS** | `uis/.dockerignore`: `node_modules`, `.next`, `.env*`, `*.log`. `services/.dockerignore`: `__pycache__`, `*.pyc`, `.env*`, `tests/`, `*.log`. |
| Contenedores en producción en el VPS existente. | **HITL** | `docs/container/RUNBOOK.md` describe el despliegue con override `docker-compose.prod.yml` (sin reload, Qdrant sin puertos públicos). Estado declarado BLOCKED_HITL: no hay SSH ni autorización. No se inventó una URL. No es GRAVE. |

Dockerfile del backend: imagen oficial `python:3.12-slim-bookworm`, instala `uv` y `uv pip install … -r requirements.txt`, Uvicorn con `--reload`. Cumple el enunciado.

## Pruebas corridas (esta pasada)

Desde `/tmp/r033`, `UV_PROJECT_ENVIRONMENT=/tmp/venv-r033`:

- `cd services/api && uv sync --group dev && uv run pytest`: **157 passed** en 6,11 s.
- `pytest tests/infra/test_compose_contract.py`: **7 passed, 1 failed, 1 skipped**. El fallo es el `git log --all` del clone incompleto (H3), no un `.env` commiteado. El skip es ausencia de Docker CLI.

## Seguridad y secretos

Sin secretos en Compose ni Dockerfiles. `.env` gitignorado y nunca en el historial público. Qdrant en local solo en loopback; en prod `ports: !reset []`. `ensure_compose_env.py` genera `JWT_SECRET` sin imprimirlo.

## Hallazgos

Véase el checkpoint. GRAVE 0, MENOR 2, IRRELEVANTE 1. VPS en HITL.
