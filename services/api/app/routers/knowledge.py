"""POST /knowledge/query calls query() and returns the model answer only.

Imports of the data package stay inside the handlers. Importing this router
does not load Qdrant, so the rest of the API starts without that extra path.
"""

from __future__ import annotations

import html
import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

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
    from data.rag_errors import EmbeddingNotConfigured, GenerationNotConfigured

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


def _split_sources(answer: str) -> tuple[str, list[str]]:
    body: list[str] = []
    sources: list[str] = []
    for line in answer.splitlines():
        stripped = line.strip()
        if stripped.startswith("Sources:") or stripped.startswith("Fuentes:"):
            sources.append(stripped.split(":", 1)[1].strip())
        else:
            body.append(line)
    return "\n".join(body).strip(), sources


def render_result_page(*, question: str, answer: str | None = None, error: str | None = None) -> str:
    from data.process.rag import catalog_entries

    safe_question = html.escape(question, quote=True)
    if error:
        state = "error"
        result = (
            '<div role="alert" class="alert">'
            '<p class="result-title">No se pudo obtener la respuesta</p>'
            f"<p>{html.escape(error)}</p>"
            "</div>"
        )
    elif answer:
        prose, sources = _split_sources(answer)
        paragraphs = "".join(f"<p>{html.escape(line)}</p>" for line in prose.splitlines() if line.strip())
        source_html = ""
        if sources:
            items = "".join(f"<li>{html.escape(item)}</li>" for item in sources)
            source_html = f"<h3>Fuentes citadas</h3><ul>{items}</ul>"
        state = "success"
        result = f'<div class="answer">{paragraphs}</div>{source_html}'
    else:
        state = "empty"
        result = "<p>Todavía no hay respuesta. Escribe la pregunta y consulta la base.</p>"
    documents = "".join(
        "<li>{title} · {language}</li>".format(
            title=html.escape(item["title"]),
            language=html.escape(item["language"]),
        )
        for item in catalog_entries()
    )
    lockup = (
        '<img class="lockup lockup-horizontal" src="/ui/brand/signal-horizontal.svg" '
        'width="1000" height="160" alt="4Geeks por Divinivid">'
        '<img class="lockup lockup-stacked" src="/ui/brand/signal-stacked.svg" '
        'width="600" height="300" alt="4Geeks por Divinivid">'
    )
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>Consulta comercial de Nexova</title>
  <link rel="stylesheet" href="/ui/tokens.css">
  <link rel="stylesheet" href="/ui/styles.css">
</head>
<body>
  <a class="skip" href="#contenido">Saltar al contenido</a>
  <header><p class="brand">Nexova · Ventas</p></header>
  <main id="contenido" class="wrap">
    <h1>Pregunta de un prospecto</h1>
    <form class="panel" method="post" action="/knowledge/query">
      <label for="question">Pregunta</label>
      <textarea id="question" name="question" required maxlength="2000" rows="5">{safe_question}</textarea>
      <div class="actions"><button class="primary" type="submit">Consultar la base</button></div>
    </form>
    <section class="panel" data-state="{state}" aria-live="polite">
      <h2>Respuesta</h2>
      {result}
    </section>
    <aside class="panel">
      <h2>Documentos</h2>
      <ul>{documents}</ul>
    </aside>
  </main>
  <footer>
    <p>Nexova Solutions. Herramienta interna de consulta comercial.</p>
    {lockup}
  </footer>
</body>
</html>
"""


def _fail(request: Request, question: str, message: str, status_code: int):
    if _wants_html(request):
        return HTMLResponse(render_result_page(question=question, error=message), status_code=status_code)
    return JSONResponse({"detail": message}, status_code=status_code)


@router.post("/knowledge/query")
async def knowledge_query(request: Request):
    import data.pipelines.rag as pipeline
    from data.rag_errors import (
        EmbeddingNotConfigured,
        GenerationCallFailed,
        GenerationNotConfigured,
        ModelIdConflict,
        RagError,
    )

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
        return _fail(request, question, "El servicio no pudo completar la respuesta.", 502)
    if not answer.strip():
        return _fail(request, question, "El modelo devolvió una respuesta vacía.", 502)
    if _wants_html(request):
        return HTMLResponse(render_result_page(question=question, answer=answer), status_code=200)
    return AnswerOut(answer=answer)


@router.get("/knowledge/catalog")
def knowledge_catalog() -> dict:
    from data.process.rag import catalog_entries

    return {"documents": catalog_entries()}


@router.get("/knowledge/status")
def knowledge_status() -> dict:
    from data.process.rag import COLLECTION, get_qdrant_client

    try:
        client = get_qdrant_client()
        if not client.collection_exists(COLLECTION):
            return {"collection": COLLECTION, "indexed": False, "chunk_count": 0, "reachable": True}
        count = client.count(collection_name=COLLECTION, exact=True).count
        return {
            "collection": COLLECTION,
            "indexed": count > 0,
            "chunk_count": count,
            "reachable": True,
        }
    except Exception:
        logger.exception("qdrant status failed")
        return {"collection": COLLECTION, "indexed": False, "chunk_count": 0, "reachable": False}
