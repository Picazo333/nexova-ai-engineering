# Runbook — producción en el VPS

Estado: **BLOCKED_HITL**. No hay acceso SSH y Miguel no ha autorizado el despliegue. Este documento no inventa una URL pública. Cuando el acceso exista, los comandos de abajo son los que hay que ejecutar, en este orden, en el servidor que ya se usa para la infraestructura de Nexova.

No se pega ningún secreto en el repositorio. El `.env` de producción se crea en el VPS y se queda allí.

## 1. Requisitos en el servidor

- Docker Engine y Docker Compose v2 (`docker compose version`).
- Un usuario con permiso para usar el socket de Docker.
- El checkout de este repositorio en la rama que se vaya a desplegar.
- Puertos libres en el host: 3000 (portal), 3001 (backoffice) y 8000 (API). 6333 lo usa Qdrant.

## 2. Código

```bash
git fetch origin
git checkout feature/company-monorepo-container
git pull origin feature/company-monorepo-container
```

Sustituye la rama por la que Miguel indique después del merge. Hasta entonces no hay `main` con este stack.

## 3. Variables

```bash
cp .env.example .env
chmod 600 .env
python3 scripts/ensure_compose_env.py
```

Abre `.env` en el servidor y sustituye:

- `JWT_SECRET` por un valor nuevo, de al menos 16 caracteres, generado en el servidor (`python3 -c "import secrets; print(secrets.token_urlsafe(32))"`). No lo copies al portátil ni al chat.
- `PUBLIC_APP_URL` por el origen con el que las personas abren el portal. Si todavía no hay un nombre de dominio, usa el origen del host publicado, no `http://services:8000`.
- `NEXT_PUBLIC_PORTAL_URL` y `NEXT_PUBLIC_API_ORIGIN` con esos mismos orígenes de navegador.
- Deja `API_INTERNAL_URL=http://services:8000` y `QDRANT_URL=http://qdrant:6333`. Esos nombres solo resuelven dentro de la red `monorepo-dev`.
- `RESEND_API_KEY` y `SENDGRID_API_KEY` vacías hasta que exista una cuenta del proveedor. Un mock no cuenta como envío real.
- `EMBEDDING_*` y `GENERATION_*` vacías hasta tener los modelos. No inventes una clave.

## 4. Arranque

El override de producción quita el reload de Uvicorn, construye el target `prod` de la UI (sin montar el código fuente de `uis/`) y reinicia los contenedores si el proceso muere.

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose ps
```

Comprobaciones en el propio servidor, no desde un nombre público:

```bash
wget -q -O - http://127.0.0.1:8000/health
wget -q -O /dev/null http://127.0.0.1:3000/login && echo portal
wget -q -O /dev/null http://127.0.0.1:3001/ && echo backoffice
docker compose exec uis wget -q -O - http://services:8000/health
```

La última línea tiene que responder `{"status":"ok"}`. Si el host de esa URL es `localhost`, el despliegue no vale.

## 5. Qué no hacer

- No commitear `.env`.
- No publicar una URL de producción en el README hasta que el servidor responda de verdad y Miguel confirme el nombre.
- No abrir el puerto 6333 a internet. Qdrant se queda en la red Docker. Si el firewall del VPS publica 6333, ciérralo.
- No usar `EMAIL_TRANSPORT=mock` como prueba de entrega del correo.

## 6. Parada

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

El volumen `qdrant_storage` se conserva. `down -v` lo borra.
