"""HTML for the no-JavaScript form post. Dynamic text is escaped."""

from __future__ import annotations

import html

from data.process.rag import catalog_entries


def split_sources(answer: str) -> tuple[str, list[str]]:
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
    safe_question = html.escape(question, quote=True)
    if error:
        state = "error"
        result = (
            '<div role="alert" class="alert">'
            "<p class=\"result-title\">No se pudo obtener la respuesta</p>"
            f"<p>{html.escape(error)}</p>"
            "</div>"
        )
    elif answer:
        prose, sources = split_sources(answer)
        paragraphs = "".join(
            f"<p>{html.escape(line)}</p>" for line in prose.splitlines() if line.strip()
        )
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
  <footer><p>Nexova Solutions. Herramienta interna de consulta comercial.</p></footer>
</body>
</html>
"""
