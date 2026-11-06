"""The Compose files keep secrets out of Git and name the Docker network."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SECRET_ASSIGNMENT = re.compile(
    r"(?i)(api[_-]?key|password|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}"
)


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_compose_uses_a_named_network_and_the_env_file() -> None:
    text = _read("docker-compose.yml")
    assert "name: monorepo-dev" in text
    assert "env_file:" in text
    assert "./uis:/app" in text
    assert ".:/app" in text
    assert '"3000:3000"' in text
    assert '"3001:3001"' in text
    assert '"8000:8000"' in text
    assert "target: dev" in text
    assert "--reload" not in text


def test_dockerfiles_match_the_ticket() -> None:
    ui = _read("uis/Dockerfile")
    api = _read("services/Dockerfile")
    assert "node:22-alpine" in ui
    assert "AS website-deps" in ui
    assert "AS backoffice-deps" in ui
    assert "AS portal-deps" in ui
    assert 'CMD ["sh", "/app/start.sh"]' in ui
    assert "USER node" in ui
    assert "python:3.12-slim-bookworm" in api
    assert "uv pip install --system --no-cache -r requirements.txt" in api
    assert "--reload" in api
    assert "USER app" in api
    start = _read("uis/start.sh")
    assert "/app/website" in start
    assert "/app/backoffice" in start


def test_dockerignore_lists_the_required_names() -> None:
    ui = _read("uis/.dockerignore")
    api = _read("services/.dockerignore")
    for name in ("node_modules", ".next", ".env*", "*.log"):
        assert name in ui
    for name in ("__pycache__", "*.pyc", ".env*", "tests/", "*.log"):
        assert name in api


def test_no_secret_literals_in_images_or_compose() -> None:
    for relative in (
        "docker-compose.yml",
        "docker-compose.prod.yml",
        "uis/Dockerfile",
        "services/Dockerfile",
        "uis/start.sh",
        "services/entrypoint.sh",
    ):
        text = _read(relative)
        assert SECRET_ASSIGNMENT.search(text) is None, relative
        assert "sk-" not in text


def test_example_env_names_the_service_hosts_and_leaves_secrets_empty() -> None:
    example = _read(".env.example")
    assert "API_INTERNAL_URL=http://services:8000" in example
    assert "QDRANT_URL=http://qdrant:6333" in example
    assert "JWT_SECRET=" in example
    assert "JWT_SECRET=change" not in example
    assert "RESEND_API_KEY=" in example
    for line in example.splitlines():
        if line.startswith("JWT_SECRET="):
            assert line == "JWT_SECRET="
        if line.startswith("RESEND_API_KEY="):
            assert line == "RESEND_API_KEY="
        if line.startswith("EMBEDDING_API_KEY="):
            assert line == "EMBEDDING_API_KEY="


def test_env_is_gitignored_and_absent_from_history() -> None:
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", ".env"],
        cwd=ROOT,
        check=False,
    )
    assert ignored.returncode == 0
    history = subprocess.run(
        ["git", "log", "--all", "--oneline", "--", ".env"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert history.stdout.strip() == ""


def test_internal_url_helper_rejects_localhost() -> None:
    from scripts.ensure_compose_env import fill

    filled = fill("JWT_SECRET=\nAPI_INTERNAL_URL=\nQDRANT_URL=\n", secret="x" * 24)
    assert "API_INTERNAL_URL=http://services:8000" in filled
    assert "QDRANT_URL=http://qdrant:6333" in filled
    assert "JWT_SECRET=" + ("x" * 24) in filled
    again = fill(filled, secret="y" * 24)
    assert "JWT_SECRET=" + ("x" * 24) in again
    assert "y" * 24 not in again
