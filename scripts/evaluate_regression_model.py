#!/usr/bin/env python3
"""Evalúa el pronóstico de ingresos con CV temporal y curva de aprendizaje.

Reutiliza el bosque, las features y el split de 035. No cambia hiperparámetros.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipelines.evaluate_regression import run_evaluation, terminal_summary, write_outputs
from pipelines.load_sales import load_official_sales, repo_root


def main() -> int:
    try:
        raw, notes = load_official_sales(repo_root())
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    if notes.get("official_hash_matches") is not True:
        print("ERROR: data/raw/nexova_sales.csv no coincide con el hash oficial.")
        return 1
    result = run_evaluation(raw)
    paths = write_outputs(result, repo_root())
    print(terminal_summary(result))
    for path in paths.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
