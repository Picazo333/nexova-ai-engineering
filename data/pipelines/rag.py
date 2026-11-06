"""Retrieve Nexova chunks and generate an answer from that context.

`query()` is the only function the API calls. It is `retrieve()` plus
`generate_answer()`, so a later agent can call either step on its own.
"""

from __future__ import annotations

import logging

import data.process.rag as indexing
from data.rag_errors import GenerationCallFailed, GenerationNotConfigured
from data.rag_settings import COLLECTION, load_settings

logger = logging.getLogger(__name__)

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


def retrieve(query: str, *, k: int = 5, min_score: float | None = None) -> list[dict]:
    """Embed the question, search Qdrant, and drop hits below `min_score`.

    The return value is a list of payloads. It can be shorter than `k`,
    including empty. Raw SDK objects and scores are not returned; scores are
    logged on the server only.
    """

    cleaned = (query or "").strip()
    if not cleaned:
        raise ValueError("query must not be blank.")
    if k < 1:
        raise ValueError("k must be at least 1.")
    settings = load_settings()
    threshold = settings.min_score if min_score is None else min_score
    vector = indexing.embed(cleaned)
    client = indexing.get_qdrant_client()
    response = client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=k,
        score_threshold=threshold,
        with_payload=True,
    )
    kept: list[dict] = []
    for point in response.points:
        score = float(point.score)
        if score < threshold:
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


def complete_chat(messages: list[dict], settings) -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=settings.generation_api_key,
        base_url=settings.generation_base_url,
        timeout=45.0,
        max_retries=1,
    )
    try:
        response = client.chat.completions.create(
            model=settings.generation_model_id,
            messages=messages,
            temperature=0.2,
            max_tokens=700,
        )
        content = response.choices[0].message.content if response.choices else None
    except Exception as exc:
        logger.warning("generation request failed (%s)", type(exc).__name__)
        raise GenerationCallFailed("The generation endpoint rejected the request.") from exc
    if not content or not str(content).strip():
        raise GenerationCallFailed("The generation endpoint returned an empty answer.")
    return str(content).strip()


def query(question: str) -> str:
    """Return the model answer for one question. This is retrieve + generate."""

    cleaned = (question or "").strip()
    if not cleaned:
        raise ValueError("question must not be blank.")
    settings = load_settings()
    context = retrieve(cleaned, k=settings.top_k, min_score=settings.min_score)
    logger.info("query kept %s chunk(s)", len(context))
    return generate_answer(cleaned, context)
