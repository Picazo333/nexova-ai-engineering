"""POST /knowledge/query calls `query()` and returns the model answer only."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

import data.pipelines.rag as pipeline
from data.process.rag import COLLECTION, catalog_entries, get_qdrant_client
from data.rag_errors import (
    EmbeddingNotConfigured,
    GenerationCallFailed,
    GenerationNotConfigured,
    ModelIdConflict,
    RagError,
)
from services.api.pages import render_result_page

logger = logging.getLogger(__name__)
router = APIRouter()


class AnswerOut(BaseModel):
    answer: str = Field(min_length=1)


def _wants_html(request: Request) -> bool:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        return False
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        return True
    return "text/html" in request.headers.get("accept", "")


async def _read_question(request: Request) -> tuple[str, str]:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            payload = await request.json()
        except Exception:
            return "", "El cuerpo debe ser JSON con el campo question."
        if not isinstance(payload, dict):
            return "", "El cuerpo debe ser un objeto JSON."
        raw = payload.get("question", "")
    else:
        form = await request.form()
        raw = form.get("question", "")
    if not isinstance(raw, str):
        return "", "La pregunta debe ser texto."
    question = raw.strip()
    if not question:
        return "", "Escribe una pregunta antes de consultar."
    if len(question) > 2000:
        return "", "La pregunta supera el máximo de 2000 caracteres."
    return question, ""


def _public_message(exc: Exception) -> str:
    if isinstance(exc, GenerationNotConfigured):
        return (
            "El modelo de generación no está configurado. "
            "Hacen falta GENERATION_MODEL_ID, GENERATION_BASE_URL y GENERATION_API_KEY, "
            "con un ID distinto del modelo de embeddings. No se inventó una respuesta."
        )
    if isinstance(exc, EmbeddingNotConfigured):
        return (
            "El modelo de embeddings no está configurado. "
            "No se inventó una respuesta."
        )
    return str(exc)


def _fail(request: Request, question: str, message: str, status_code: int):
    if _wants_html(request):
        return HTMLResponse(
            render_result_page(question=question, error=message),
            status_code=status_code,
        )
    return JSONResponse({"detail": message}, status_code=status_code)


@router.post("/knowledge/query")
async def knowledge_query(request: Request):
    question, error = await _read_question(request)
    if error:
        return _fail(request, question, error, 422)
    try:
        answer = pipeline.query(question)
    except (EmbeddingNotConfigured, GenerationNotConfigured) as exc:
        logger.info("knowledge query unavailable: %s", type(exc).__name__)
        return _fail(request, question, _public_message(exc), 503)
    except (GenerationCallFailed, ModelIdConflict, RagError) as exc:
        logger.warning("knowledge query failed: %s", type(exc).__name__)
        return _fail(request, question, str(exc), 502)
    except Exception:
        logger.exception("knowledge query crashed")
        return _fail(
            request,
            question,
            "El servicio no pudo completar la respuesta.",
            502,
        )
    if not answer.strip():
        return _fail(request, question, "El modelo devolvió una respuesta vacía.", 502)
    if _wants_html(request):
        return HTMLResponse(render_result_page(question=question, answer=answer), status_code=200)
    return AnswerOut(answer=answer)


@router.get("/knowledge/catalog")
def knowledge_catalog() -> dict:
    return {"documents": catalog_entries()}


@router.get("/knowledge/status")
def knowledge_status() -> dict:
    try:
        client = get_qdrant_client()
        if not client.collection_exists(COLLECTION):
            return {
                "collection": COLLECTION,
                "indexed": False,
                "chunk_count": 0,
                "reachable": True,
            }
        count = client.count(collection_name=COLLECTION, exact=True).count
        return {
            "collection": COLLECTION,
            "indexed": count > 0,
            "chunk_count": count,
            "reachable": True,
        }
    except Exception:
        logger.exception("qdrant status failed")
        return {
            "collection": COLLECTION,
            "indexed": False,
            "chunk_count": 0,
            "reachable": False,
        }
