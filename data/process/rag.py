"""Chunk the Nexova corpus and index it in Qdrant.

`setup()` and `embed()` live here. Retrieval and generation live in
`data.pipelines.rag` so each function has one job.

Idempotency is clear-and-reload: every `setup()` deletes `nexova_knowledge`
if it exists and writes the corpus again. Point IDs are UUID5 values derived
from company, source document, language and chunk index, so the same chunk
keeps the same ID across reloads.
"""

from __future__ import annotations

import logging
import math
import uuid
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from data.rag_errors import CorpusError, EmbeddingCallFailed, EmbeddingNotConfigured
from data.rag_settings import (
    COLLECTION,
    COMPANY,
    LOCAL_EMBED_MODEL,
    ROOT,
    Settings,
    load_settings,
)

logger = logging.getLogger(__name__)

CORPUS_DIR = ROOT / "docs" / "company-knowledge-base"
POINT_NAMESPACE = uuid.UUID("3c1a0e7a-5b14-4f2e-9d6a-8b7c6d5e4f30")

CORPUS_FILES = {
    "nexova-service-lines.en.md": ("service-lines", "en"),
    "nexova-service-lines.es.md": ("service-lines", "es"),
    "nexova-pricing-model.en.md": ("pricing-model", "en"),
    "nexova-pricing-model.es.md": ("pricing-model", "es"),
    "nexova-hiring-process-sla.en.md": ("hiring-process-sla", "en"),
    "nexova-hiring-process-sla.es.md": ("hiring-process-sla", "es"),
    "nexova-objection-handling.en.md": ("objection-handling", "en"),
    "nexova-objection-handling.es.md": ("objection-handling", "es"),
}

_CLIENTS: dict[str, QdrantClient] = {}
_LOCAL_MODEL = None


@dataclass(frozen=True)
class Chunk:
    source_document: str
    section: str
    language: str
    chunk_index: int
    text: str
    source_file: str


def corpus_paths() -> list:
    found = {path.name: path for path in CORPUS_DIR.glob("nexova-*.md")}
    missing = sorted(set(CORPUS_FILES) - set(found))
    extra = sorted(set(found) - set(CORPUS_FILES))
    if missing or extra:
        raise CorpusError(
            "docs/company-knowledge-base must contain the eight official "
            f"Nexova files. missing={missing} extra={extra}"
        )
    return [found[name] for name in sorted(CORPUS_FILES)]


def catalog_entries() -> list[dict]:
    """Titles and slugs of the source documents. No chunk bodies."""

    entries = []
    for path in corpus_paths():
        source_document, language = CORPUS_FILES[path.name]
        title = path.stem
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        entries.append(
            {
                "filename": path.name,
                "source_document": source_document,
                "language": language,
                "title": title,
            }
        )
    return entries


def chunk_corpus() -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in corpus_paths():
        source_document, language = CORPUS_FILES[path.name]
        text = path.read_text(encoding="utf-8")
        pieces = _chunk_lines(text.splitlines())
        if len(pieces) < 3:
            raise CorpusError(f"{path.name} produced {len(pieces)} chunks; expected at least 3.")
        for index, lines in enumerate(pieces):
            body = "\n".join(lines).strip()
            if not body:
                raise CorpusError(f"{path.name} chunk {index} is empty.")
            chunks.append(
                Chunk(
                    source_document=source_document,
                    section=_section_label(lines),
                    language=language,
                    chunk_index=index,
                    text=body,
                    source_file=path.name,
                )
            )
    return chunks


def _chunk_lines(raw_lines: list[str]) -> list[list[str]]:
    """Split on blank lines, which are the semantic boundaries in this corpus.

    Hard-wrapped sentences stay in one block because the official files do
    not insert a blank line inside a sentence. A bullet list that follows a
    lead-in stays with that lead-in. A markdown title stays with the first
    block so the title is not a chunk by itself.
    """

    blocks: list[list[str]] = []
    current: list[str] = []
    for line in raw_lines:
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(line)
    if current:
        blocks.append(current)

    chunks: list[list[str]] = []
    pending_title: list[str] = []
    for block in blocks:
        if len(block) == 1 and block[0].startswith("#"):
            pending_title = block
            continue
        if block[0].lstrip().startswith("-") and chunks:
            chunks[-1].extend([""] + block)
            continue
        if pending_title:
            chunks.append(pending_title + [""] + list(block))
            pending_title = []
        else:
            chunks.append(list(block))
    if pending_title:
        chunks.append(pending_title)
    return chunks


def _section_label(lines: list[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        stripped = _strip_number(stripped)
        if stripped.startswith('"') and stripped.endswith('"') and len(stripped) > 1:
            stripped = stripped[1:-1]
        if ":" in stripped:
            head, _, _rest = stripped.partition(":")
            if 0 < len(head) <= 90 and "." not in head:
                return head.strip()
        return stripped[:120]
    return "untitled"


def _strip_number(value: str) -> str:
    digits = 0
    while digits < len(value) and value[digits].isdigit():
        digits += 1
    if digits and value[digits : digits + 2] == ". ":
        return value[digits + 2 :]
    return value


def point_id(chunk: Chunk) -> str:
    name = f"{COMPANY}|{chunk.source_document}|{chunk.language}|{chunk.chunk_index}"
    return str(uuid.uuid5(POINT_NAMESPACE, name))


def payload_for(chunk: Chunk) -> dict:
    return {
        "company": COMPANY,
        "source_document": chunk.source_document,
        "section": chunk.section,
        "language": chunk.language,
        "chunk_index": chunk.chunk_index,
        "text": chunk.text,
    }


def reset_client_cache() -> None:
    for client in _CLIENTS.values():
        close = getattr(client, "close", None)
        if close:
            close()
    _CLIENTS.clear()


def get_qdrant_client() -> QdrantClient:
    """Open Qdrant over HTTP, or the embedded local engine when no URL is set."""

    settings = load_settings()
    if settings.qdrant_url:
        key = f"url:{settings.qdrant_url}"
        if key not in _CLIENTS:
            _CLIENTS[key] = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key or None,
                timeout=10,
            )
        return _CLIENTS[key]
    if settings.qdrant_path in {":memory:", "memory"}:
        key = "memory"
        if key not in _CLIENTS:
            _CLIENTS[key] = QdrantClient(":memory:")
        return _CLIENTS[key]
    path = settings.qdrant_path
    key = f"path:{path}"
    if key not in _CLIENTS:
        from pathlib import Path

        Path(path).mkdir(parents=True, exist_ok=True)
        _CLIENTS[key] = QdrantClient(path=path)
    return _CLIENTS[key]


def embed(text: str) -> list[float]:
    """Embed one text with the dedicated embeddings model.

    The same function is used for chunks at index time and for the question
    at query time. The generation model is never called from here.
    """

    if not isinstance(text, str) or not text.strip():
        raise ValueError("embed() requires non-empty text.")
    settings = load_settings()
    settings.ensure_distinct_model_ids()
    if settings.embedding_remote_ready:
        raw = _embed_remote(text, settings)
    elif settings.embed_backend == "fastembed":
        raw = _embed_fastembed(text)
    elif settings.embed_backend:
        raise EmbeddingNotConfigured()
    else:
        raise EmbeddingNotConfigured()
    if not raw:
        raise EmbeddingCallFailed("The embeddings call returned an empty vector.")
    return _l2_normalize([float(value) for value in raw])


def _embed_remote(text: str, settings: Settings) -> list[float]:
    from openai import OpenAI

    client = OpenAI(
        api_key=settings.embedding_api_key,
        base_url=settings.embedding_base_url,
        timeout=30.0,
        max_retries=1,
    )
    try:
        response = client.embeddings.create(model=settings.embedding_model_id, input=text)
        vector = response.data[0].embedding
    except EmbeddingCallFailed:
        raise
    except Exception as exc:
        logger.warning("embedding request failed (%s)", type(exc).__name__)
        raise EmbeddingCallFailed("The embeddings endpoint rejected the request.") from exc
    return list(vector)


def _embed_fastembed(text: str) -> list[float]:
    global _LOCAL_MODEL
    if _LOCAL_MODEL is None:
        try:
            from fastembed import TextEmbedding
        except ImportError as exc:
            raise EmbeddingCallFailed(
                "RAG_EMBED_BACKEND=fastembed but the fastembed package is not installed."
            ) from exc
        _LOCAL_MODEL = TextEmbedding(model_name=LOCAL_EMBED_MODEL)
    vectors = list(_LOCAL_MODEL.embed([text]))
    return [float(value) for value in vectors[0]]


def _l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        raise EmbeddingCallFailed("The embedding vector has zero norm.")
    return [value / norm for value in vector]


def setup() -> dict:
    """Read the corpus, embed every chunk, and reload the Qdrant collection."""

    chunks = chunk_corpus()
    counts: dict[str, int] = {}
    for chunk in chunks:
        key = f"{chunk.source_document}:{chunk.language}"
        counts[key] = counts.get(key, 0) + 1
    short = {key: count for key, count in counts.items() if count < 3}
    if short:
        raise CorpusError(f"Documents with fewer than 3 chunks: {short}")

    vectors = [embed(chunk.text) for chunk in chunks]
    size = len(vectors[0])
    if any(len(vector) != size for vector in vectors):
        raise CorpusError("embed() returned vectors of different sizes.")

    client = get_qdrant_client()
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=size, distance=Distance.COSINE),
    )
    points = [
        PointStruct(id=point_id(chunk), vector=vector, payload=payload_for(chunk))
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]
    client.upsert(collection_name=COLLECTION, points=points, wait=True)
    stored = client.count(collection_name=COLLECTION, exact=True).count
    report = {
        "collection": COLLECTION,
        "chunk_count": stored,
        "vector_size": size,
        "distance": "cosine",
        "idempotency": "clear-and-reload with deterministic uuid5 ids",
        "per_document": counts,
    }
    logger.info("indexed %s points into %s", stored, COLLECTION)
    return report


def main() -> None:
    import json

    print(json.dumps(setup(), ensure_ascii=False, indent=2))
    reset_client_cache()


if __name__ == "__main__":
    main()
