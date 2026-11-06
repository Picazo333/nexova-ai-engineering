"""Carga de la serie oficial de Nexova. No reescribe el CSV."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

OFFICIAL_CSV_SHA256 = (
    "e3af15657506fae36a81eec6a9a544a54473bf38f41f2ee1bb066799ff94440a"
)
RAW_RELATIVE = Path("data/raw/nexova_sales.csv")
EXPECTED_COLUMNS = (
    "month",
    "revenue_usd",
    "active_contracts",
    "avg_contract_value_usd",
    "business_line",
)
TARGET_COLUMN = "revenue_usd"
PRIMARY_BUSINESS_LINE = "consolidated"
SERIES_START = "2016-01-01"
SERIES_END = "2025-12-01"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def official_csv_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / RAW_RELATIVE


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Quita filas con nulos o celdas vacías en las columnas del briefing.

    No imputa con valores futuros ni con la media del objetivo. Una celda en
    blanco cuenta como ausente. El archivo de origen no se modifica.
    """
    missing = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(
            "Faltan columnas del briefing de Nexova: " + ", ".join(missing)
        )
    extra = [column for column in df.columns if column not in EXPECTED_COLUMNS]
    if extra:
        raise ValueError(
            "El CSV trae columnas que el briefing no define: " + ", ".join(extra)
        )

    frame = df.loc[:, list(EXPECTED_COLUMNS)].copy()
    for column in frame.columns:
        if pd.api.types.is_object_dtype(frame[column]) or pd.api.types.is_string_dtype(frame[column]):
            text = frame[column].astype("string").str.strip()
            frame[column] = text.mask(text.eq("") | text.str.lower().isin(["nan", "none", "null"]))

    frame["month"] = pd.to_datetime(frame["month"], errors="coerce")
    for column in ("revenue_usd", "active_contracts", "avg_contract_value_usd"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    before = len(frame)
    frame = frame.dropna(subset=list(EXPECTED_COLUMNS)).copy()
    dropped = before - len(frame)
    frame["business_line"] = frame["business_line"].astype(str).str.strip()
    frame = frame.sort_values("month").reset_index(drop=True)
    return frame, dropped


def select_consolidated(df: pd.DataFrame) -> pd.DataFrame:
    """El objetivo del briefing es la fila consolidated, no una línea suelta."""
    return (
        df.loc[df["business_line"] == PRIMARY_BUSINESS_LINE]
        .sort_values("month")
        .reset_index(drop=True)
    )


def assert_series_contract(df: pd.DataFrame) -> None:
    """Restricciones del briefing: ingreso positivo y meses continuos."""
    if df.empty:
        raise ValueError("La serie consolidada está vacía.")
    if not bool((df[TARGET_COLUMN] > 0).all()):
        raise ValueError("revenue_usd debe ser positivo en todos los meses.")
    if not bool(df["business_line"].eq(PRIMARY_BUSINESS_LINE).all()):
        raise ValueError("El modelo solo admite business_line=consolidated.")
    expected = pd.date_range(SERIES_START, SERIES_END, freq="MS")
    actual = [timestamp.strftime("%Y-%m-%d") for timestamp in df["month"]]
    wanted = [timestamp.strftime("%Y-%m-%d") for timestamp in expected]
    if actual != wanted:
        raise ValueError(
            "La serie debe incluir cada mes de 2016-01 a 2025-12, sin huecos."
        )


def load_sales(path: Path) -> tuple[pd.DataFrame, dict]:
    if not path.is_file():
        raise FileNotFoundError(
            f"No está el CSV en {path}. No se genera ni se simula la serie."
        )
    digest = file_sha256(path)
    raw = pd.read_csv(path)
    cleaned, dropped = clean_frame(raw)
    consolidated = select_consolidated(cleaned)
    notes = {
        "path": str(path),
        "sha256": digest,
        "rows_read": int(len(raw)),
        "rows_dropped_null": int(dropped),
        "rows_consolidated": int(len(consolidated)),
        "official_hash_matches": digest == OFFICIAL_CSV_SHA256,
    }
    return consolidated, notes


def load_official_sales(root: Path | None = None) -> tuple[pd.DataFrame, dict]:
    """Carga el CSV oficial y rechaza cualquier archivo con otro hash."""
    frame, notes = load_sales(official_csv_path(root))
    if not notes["official_hash_matches"]:
        raise ValueError(
            "El hash del CSV no es el de la serie oficial. "
            "No se entrena con una serie alterada o simulada."
        )
    assert_series_contract(frame)
    return frame, notes
