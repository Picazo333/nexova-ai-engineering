# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:0.13.7 AS uv

FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/packages:/app/services/api \
    UV_SYSTEM_PYTHON=1

COPY --from=uv /uv /uvx /bin/

RUN useradd --create-home --uid 1000 --shell /bin/sh app

COPY requirements.txt /opt/req/requirements.txt
COPY api/requirements.txt /opt/req/api/requirements.txt
WORKDIR /opt/req
RUN uv pip install --system --no-cache -r requirements.txt

WORKDIR /app/services
COPY entrypoint.sh /app/services/entrypoint.sh
COPY api /app/services/api
RUN chmod 755 /app/services/entrypoint.sh \
    && chown -R app:app /app

USER app
WORKDIR /app/services/api
EXPOSE 8000

ENTRYPOINT ["sh", "/app/services/entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/services/api"]
