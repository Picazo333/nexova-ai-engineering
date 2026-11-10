#!/usr/bin/env python3
"""Fail if Qdrant would publish a port on a non-loopback address.

Uses `docker compose config --format json` (no Docker engine needed). Checks
the local stack (docker-compose.yml) and the production stack
(docker-compose.yml + docker-compose.prod.yml). Exit 0 = ok, 1 = exposed,
2 = compose CLI missing.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOPBACK = {"127.0.0.1", "::1", "localhost"}


def compose_cmd() -> list[str] | None:
    override = os.environ.get("COMPOSE_BIN")
    if override:
        return [override]
    if shutil.which("docker"):
        probe = subprocess.run(["docker", "compose", "version"], capture_output=True)
        if probe.returncode == 0:
            return ["docker", "compose"]
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    return None


def rendered(cmd: list[str], files: list[str]) -> dict:
    args = [*cmd]
    for name in files:
        args += ["-f", str(ROOT / name)]
    args += ["config", "--format", "json"]
    out = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def problems(config: dict, *, allow_loopback: bool) -> list[str]:
    found = []
    for port in config.get("services", {}).get("qdrant", {}).get("ports", []) or []:
        host = port.get("host_ip") or "0.0.0.0"
        if not (allow_loopback and host in LOOPBACK):
            found.append(f"{host}:{port.get('published')}->{port.get('target')}")
    return found


def main() -> int:
    cmd = compose_cmd()
    if cmd is None:
        print("docker compose no está disponible (define COMPOSE_BIN)", file=sys.stderr)
        return 2
    local = problems(rendered(cmd, ["docker-compose.yml"]), allow_loopback=True)
    prod = problems(rendered(cmd, ["docker-compose.yml", "docker-compose.prod.yml"]), allow_loopback=False)
    for label, items in (("local", local), ("prod", prod)):
        print(f"{label}: qdrant ports fuera de loopback = {items or 'ninguno'}")
    return 1 if local or prod else 0


if __name__ == "__main__":
    raise SystemExit(main())
