#!/usr/bin/env python3
"""Entrena el pronóstico de ingresos de Nexova.

El briefing de la empresa pide el script de entrenamiento en ``scripts/``.
La lógica vive en ``pipelines/`` para que ``tests/pipelines/`` la importe.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipelines.train_sales_model import main


if __name__ == "__main__":
    raise SystemExit(main())
