"""POST /agent/query invokes the compiled graph. It does not retrieve or generate.

GET /agent/runs/{run_id} reads the trace written by that run.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


async def _read_question(request: Request) -> tuple[str | None, str]:
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        return None, "El cuerpo debe ser JSON con el campo question."
    try:
        payload = await request.json()
    except Exception:
        return None, "El cuerpo debe ser JSON con el campo question."
    if not isinstance(payload, dict):
        return None, "El cuerpo debe ser un objeto JSON."
    if "question" not in payload:
        return None, "El cuerpo debe ser JSON con el campo question."
    question = payload.get("question")
    if not isinstance(question, str):
        return None, "La pregunta debe ser texto."
    return question, ""


@router.post("/agent/query")
async def agent_query(request: Request):
    from app.agent.errors import GraphStructureError
    from app.agent.graph import run_agent

    question, transport_error = await _read_question(request)
    if transport_error:
        return JSONResponse({"detail": transport_error}, status_code=422)
    try:
        result = run_agent(question or "")
    except GraphStructureError as exc:
        logger.error("agent graph rejected at compile: %s", type(exc).__name__)
        return JSONResponse({"detail": str(exc)}, status_code=500)
    except Exception:
        logger.exception("agent endpoint crashed")
        return JSONResponse(
            {"detail": "El agente no pudo completar la respuesta."},
            status_code=502,
        )
    if result.http_status != 200:
        return JSONResponse(
            {"detail": result.error or "El agente no pudo completar la respuesta.", "run_id": result.run_id},
            status_code=result.http_status,
        )
    return {"answer": result.answer, "run_id": result.run_id, "trace": result.trace}


@router.get("/agent/runs/{run_id}")
def agent_run(run_id: str):
    from app.agent.graph import load_trace

    trace = load_trace(run_id)
    if trace is None:
        return JSONResponse(
            {"detail": "No hay una corrida con ese identificador."},
            status_code=404,
        )
    return trace
