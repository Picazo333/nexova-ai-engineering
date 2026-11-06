"""Retrieve Nexova chunks and generate an answer from that context.

`query()` is the only function the API calls. It is `retrieve()` plus
`generate_answer()`, so a later agent can call either step on its own.
"""

from __future__ import annotations

import logging
import re

import data.process.rag as indexing
from data.rag_errors import GenerationCallFailed, GenerationNotConfigured
from data.rag_settings import COLLECTION, load_settings

logger = logging.getLogger(__name__)

# A proxy can return HTTP 200 with a cut-off body ("Gra") or finish_reason
# "length". Neither is an answer. Two attempts, then a hard failure.
_MIN_ANSWER_CHARS = 20
_GENERATION_ATTEMPTS = 2

SYSTEM_PROMPT = """You answer as a Nexova salesperson. The audience is a prospect on a sales call. An SDR uses your answer before or during that call. Be confident and oriented toward closing. Write a natural answer, not a dump of database fragments.

Use only the retrieved context. Do not invent company facts, fees, percentages, amounts, timeframes, or commercial conditions that are not in that context.

If the context is empty or does not contain the answer, say clearly that the knowledge base does not have enough information. Do not guess and do not fill the gap with a plausible company fact.

Commercial rules:
- Never offer a discount below the 22% executive-search fee. If the prospect asks for a lower fee, including a change from 22% to 15%, say that the condition requires approval from Marcos Ibáñez. Do not invent an approved discount.
- Present delivery times as averages, not guarantees, except the 6-month replacement guarantee, which is contractual.
- If the prospect asks about competitor clients, be transparent: Nexova does not take simultaneous searches for two companies in a direct conflict of interest in the same selection process, and it may have worked with competitors in the past. Never conceal that.

Answer in the same language as the question.
After the answer, cite only sources present in the context, one per line, exactly as:
Sources: <source_document> — <section>
Do not include similarity scores, chunk indexes, or raw search payloads.
"""


_CONJUNCTION = re.compile(r"\s+(?:y|e|o|u|and|or)\s+", re.IGNORECASE)


def compound_clauses(question: str) -> list[str]:
    """Split a question that asks two things at once.

    One embedding of "tarifa y quién autoriza una rebaja" sits between two
    different chunks and can miss the fee block. Each side is searched on
    its own when both sides are real clauses (at least four words). A single
    topic, or a conjunction inside a short phrase, stays one search.
    """

    text = " ".join((question or "").split())
    parts = _CONJUNCTION.split(text)
    clauses: list[str] = []
    for part in parts:
        cleaned = part.strip()
        words = re.findall(r"\w+", cleaned, flags=re.UNICODE)
        if len(words) >= 4:
            clauses.append(cleaned)
    if len(clauses) < 2:
        return [text]
    return clauses[:3]


def _search_once(text: str, *, k: int, min_score: float) -> list[dict]:
    vector = indexing.embed(text)
    client = indexing.get_qdrant_client()
    response = client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=k,
        score_threshold=min_score,
        with_payload=True,
    )
    kept: list[dict] = []
    for point in response.points:
        score = float(point.score)
        if score < min_score:
            logger.info("drop hit below min_score score=%.4f", score)
            continue
        payload = dict(point.payload or {})
        payload.pop("score", None)
        logger.info(
            "hit score=%.4f source=%s section=%s",
            score,
            payload.get("source_document"),
            payload.get("section"),
        )
        kept.append(payload)
        if len(kept) >= k:
            break
    return kept


def _chunk_key(payload: dict) -> tuple:
    return (
        payload.get("source_document"),
        payload.get("language"),
        payload.get("chunk_index"),
        payload.get("section"),
    )


def retrieve(query: str, *, k: int = 5, min_score: float | None = None) -> list[dict]:
    """Embed the question, search Qdrant, and drop hits below `min_score`.

    The return value is a list of payloads. It can be shorter than `k`,
    including empty. Raw SDK objects and scores are not returned; scores are
    logged on the server only.

    A compound question is searched once per clause. The lists are merged in
    round-robin order and capped at `k`, so each clause can place its best
    chunk in the result instead of one blended vector filling every slot.
    """

    cleaned = (query or "").strip()
    if not cleaned:
        raise ValueError("query must not be blank.")
    if k < 1:
        raise ValueError("k must be at least 1.")
    settings = load_settings()
    threshold = settings.min_score if min_score is None else min_score
    clauses = compound_clauses(cleaned)
    if len(clauses) == 1:
        return _search_once(clauses[0], k=k, min_score=threshold)
    batches = [_search_once(clause, k=k, min_score=threshold) for clause in clauses]
    merged: list[dict] = []
    seen: set[tuple] = set()
    for rank in range(k):
        for batch in batches:
            if rank >= len(batch):
                continue
            item = batch[rank]
            key = _chunk_key(item)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
            if len(merged) >= k:
                return merged
    return merged


def build_messages(question: str, context: list[dict]) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _user_message(question, context)},
    ]


def _user_message(question: str, context: list[dict]) -> str:
    if not context:
        rendered = "(no retrieved context)"
    else:
        blocks = []
        for index, item in enumerate(context, start=1):
            blocks.append(
                "\n".join(
                    [
                        f"[{index}] source_document={item.get('source_document', '')}",
                        f"section={item.get('section', '')}",
                        f"language={item.get('language', '')}",
                        str(item.get("text", "")),
                    ]
                )
            )
        rendered = "\n\n".join(blocks)
    return f"Question:\n{question}\n\nRetrieved context:\n{rendered}"


def generate_answer(question: str, context: list[dict]) -> str:
    """Call the generation model with the question and the retrieved context."""

    cleaned = (question or "").strip()
    if not cleaned:
        raise ValueError("question must not be blank.")
    settings = load_settings()
    settings.ensure_distinct_model_ids()
    if not settings.generation_remote_ready:
        raise GenerationNotConfigured()
    return complete_chat(build_messages(cleaned, context), settings)


def _usable_answer(choice) -> str | None:
    """Accept only a finished answer. Truncation and stubs are not answers."""

    if choice is None:
        return None
    finish = getattr(choice, "finish_reason", None)
    message = getattr(choice, "message", None)
    raw = getattr(message, "content", None) if message is not None else None
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    if finish != "stop":
        return None
    if len(text) < _MIN_ANSWER_CHARS:
        return None
    return text


def complete_chat(messages: list[dict], settings) -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=settings.generation_api_key,
        base_url=settings.generation_base_url,
        timeout=45.0,
        max_retries=0,
    )
    last_reason = "empty"
    for attempt in range(1, _GENERATION_ATTEMPTS + 1):
        try:
            response = client.chat.completions.create(
                model=settings.generation_model_id,
                messages=messages,
                temperature=0.2,
                max_tokens=700,
            )
        except Exception as exc:
            last_reason = type(exc).__name__
            logger.warning("generation request failed (%s) attempt %s", last_reason, attempt)
            continue
        choice = response.choices[0] if getattr(response, "choices", None) else None
        text = _usable_answer(choice)
        if text is not None:
            return text
        finish = getattr(choice, "finish_reason", None) if choice is not None else None
        raw = getattr(getattr(choice, "message", None), "content", None) if choice is not None else None
        length = len(raw.strip()) if isinstance(raw, str) else 0
        if finish != "stop":
            last_reason = finish or "missing_finish_reason"
        elif length < _MIN_ANSWER_CHARS:
            last_reason = "too_short"
        else:
            last_reason = "empty"
        logger.warning(
            "incomplete generation attempt %s finish_reason=%s chars=%s",
            attempt,
            finish,
            length,
        )
    raise GenerationCallFailed(
        "The generation model returned an incomplete answer "
        f"({last_reason}). The partial text was not accepted."
    )


def query(question: str) -> str:
    """Return the model answer for one question. This is retrieve + generate."""

    cleaned = (question or "").strip()
    if not cleaned:
        raise ValueError("question must not be blank.")
    settings = load_settings()
    context = retrieve(cleaned, k=settings.top_k, min_score=settings.min_score)
    logger.info("query kept %s chunk(s)", len(context))
    return generate_answer(cleaned, context)
