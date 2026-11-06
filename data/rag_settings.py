"""Runtime settings for the Nexova knowledge base.

Values come from the environment. A local `.env` file is read only to fill
variables that are not already set. Secret values are never logged.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COLLECTION = "nexova_knowledge"
COMPANY = "nexova"
DEFAULT_MIN_SCORE = 0.40
DEFAULT_TOP_K = 5
LOCAL_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LOCAL_EMBED_DIMENSION = 384

_DOTENV_LOADED = False


def load_dotenv() -> None:
    """Fill missing environment variables from `.env` without overriding."""

    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return
    _DOTENV_LOADED = True
    path = ROOT / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def _clean(name: str) -> str:
    return os.environ.get(name, "").strip()


@dataclass(frozen=True)
class Settings:
    embedding_model_id: str
    generation_model_id: str
    embedding_base_url: str
    generation_base_url: str
    embedding_api_key: str
    generation_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    qdrant_path: str
    embed_backend: str
    min_score: float
    top_k: int

    @property
    def embedding_remote_ready(self) -> bool:
        return bool(self.embedding_model_id and self.embedding_base_url and self.embedding_api_key)

    @property
    def generation_remote_ready(self) -> bool:
        return bool(self.generation_model_id and self.generation_base_url and self.generation_api_key)

    def ensure_distinct_model_ids(self) -> None:
        from data.rag_errors import ModelIdConflict

        values: list[str] = []
        if self.embedding_model_id:
            values.append(self.embedding_model_id)
        if self.generation_model_id:
            values.append(self.generation_model_id)
        if self.embed_backend == "fastembed":
            values.append(LOCAL_EMBED_MODEL)
        if len(values) != len(set(values)):
            raise ModelIdConflict()


def load_settings() -> Settings:
    load_dotenv()
    raw_score = _clean("RAG_MIN_SCORE")
    try:
        min_score = float(raw_score) if raw_score else DEFAULT_MIN_SCORE
    except ValueError as exc:
        raise ValueError("RAG_MIN_SCORE must be a number.") from exc
    raw_k = _clean("RAG_TOP_K")
    try:
        top_k = int(raw_k) if raw_k else DEFAULT_TOP_K
    except ValueError as exc:
        raise ValueError("RAG_TOP_K must be an integer.") from exc
    if top_k < 1:
        raise ValueError("RAG_TOP_K must be at least 1.")
    path = _clean("QDRANT_PATH") or str(ROOT / "data" / "qdrant")
    return Settings(
        embedding_model_id=_clean("EMBEDDING_MODEL_ID"),
        generation_model_id=_clean("GENERATION_MODEL_ID"),
        embedding_base_url=_clean("EMBEDDING_BASE_URL").rstrip("/"),
        generation_base_url=_clean("GENERATION_BASE_URL").rstrip("/"),
        embedding_api_key=_clean("EMBEDDING_API_KEY"),
        generation_api_key=_clean("GENERATION_API_KEY"),
        qdrant_url=_clean("QDRANT_URL").rstrip("/"),
        qdrant_api_key=_clean("QDRANT_API_KEY"),
        qdrant_path=path,
        embed_backend=_clean("RAG_EMBED_BACKEND").lower(),
        min_score=min_score,
        top_k=top_k,
    )
