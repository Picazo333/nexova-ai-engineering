.PHONY: test test-cov env up up-detach ps down

# Atajo. La batería se ejecuta dentro del proyecto FastAPI.
test:
	cd services/api && uv run pytest

test-cov:
	cd services/api && uv run pytest --cov

# Crea el .env gitignorado si falta y rellena solo los valores vacíos.
env:
	python3 scripts/ensure_compose_env.py

# Un comando: entorno local y la plataforma. Las URLs son las del host.
up: env
	@echo "Portal (website)  http://127.0.0.1:3000"
	@echo "Backoffice        http://127.0.0.1:3001"
	@echo "API               http://127.0.0.1:8000/health"
	docker compose up --build

up-detach: env
	docker compose up --build -d --wait

ps:
	docker compose ps

down:
	docker compose down
