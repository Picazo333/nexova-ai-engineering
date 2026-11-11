.PHONY: test test-cov

# Atajo. La batería se ejecuta dentro del proyecto FastAPI.
test:
	cd services/api && uv run pytest

test-cov:
	cd services/api && uv run pytest --cov
