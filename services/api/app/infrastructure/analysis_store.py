"""Last successful analysis, kept on local disk without the source CSV."""

from __future__ import annotations

import json
import threading
from pathlib import Path

from app.config import data_dir

_store: "AnalysisStore | None" = None


class AnalysisStore:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self._lock = threading.Lock()
        self.payload: dict | None = None
        self.csv_text: str | None = None
        self._load()

    def _path(self) -> Path:
        return self.directory / "last_analysis.json"

    def _load(self) -> None:
        path = self._path()
        if not path.is_file():
            return
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        payload = saved.get("payload")
        csv_text = saved.get("csv")
        if not isinstance(payload, dict) or not isinstance(csv_text, str):
            return
        if "@" in csv_text or "@" in json.dumps(payload, ensure_ascii=False):
            return
        self.payload = payload
        self.csv_text = csv_text

    def save(self, payload: dict, csv_text: str) -> None:
        serialised = json.dumps(payload, ensure_ascii=False)
        if "@" in csv_text or "@" in serialised:
            raise RuntimeError("refusing to store a report that contains @")
        with self._lock:
            self.directory.mkdir(parents=True, exist_ok=True)
            self._path().write_text(
                json.dumps({"payload": payload, "csv": csv_text}, ensure_ascii=False),
                encoding="utf-8",
            )
            self.payload = payload
            self.csv_text = csv_text

    def clear(self) -> None:
        with self._lock:
            self.payload = None
            self.csv_text = None
            path = self._path()
            if path.exists():
                path.unlink()


def get_store() -> AnalysisStore:
    global _store
    if _store is None:
        _store = AnalysisStore(data_dir())
    return _store


def reset_store(directory: Path | None = None) -> AnalysisStore:
    global _store
    _store = AnalysisStore(directory or data_dir())
    return _store
