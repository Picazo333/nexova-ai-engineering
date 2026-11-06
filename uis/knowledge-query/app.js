(function () {
  const form = document.querySelector("#query-form");
  const question = document.querySelector("#question");
  const submit = document.querySelector("#submit");
  const result = document.querySelector("#result");
  const resultBody = document.querySelector("#result-body");
  const live = document.querySelector("#live");
  const documents = document.querySelector("#documents");
  const status = document.querySelector("#index-status");
  const submitLabel = "Consultar la base";
  let controller = null;
  let requestSeq = 0;

  document.querySelectorAll("[data-question]").forEach(function (button) {
    button.addEventListener("click", function () {
      question.value = button.getAttribute("data-question") || "";
      question.focus();
    });
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const value = question.value.trim();
    if (!value) {
      showError("Escribe una pregunta antes de consultar.", false);
      return;
    }
    if (controller) controller.abort();
    controller = new AbortController();
    const seq = ++requestSeq;
    submit.disabled = true;
    submit.textContent = "Consultando la base";
    result.dataset.state = "loading";
    result.setAttribute("aria-busy", "true");
    resultBody.replaceChildren();
    const loading = document.createElement("p");
    loading.textContent = "Consultando la base y redactando la respuesta.";
    resultBody.appendChild(loading);
    live.textContent = "Consultando la base.";

    fetch("/knowledge/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({ question: value }),
      signal: controller.signal
    })
      .then(function (response) {
        return response.json().catch(function () { return null; }).then(function (payload) {
          return { response: response, payload: payload };
        });
      })
      .then(function (resultPack) {
        if (seq !== requestSeq) return;
        const response = resultPack.response;
        const payload = resultPack.payload;
        if (!response.ok || !payload || typeof payload.answer !== "string" || !payload.answer.trim()) {
          showError(errorDetail(payload), true);
          return;
        }
        showSuccess(payload.answer);
      })
      .catch(function (error) {
        if (error && error.name === "AbortError") return;
        if (seq !== requestSeq) return;
        showError("No se pudo contactar el servicio. La pregunta sigue en el campo.", true);
      })
      .finally(function () {
        if (seq !== requestSeq) return;
        submit.disabled = false;
        submit.textContent = submitLabel;
        result.setAttribute("aria-busy", "false");
      });
  });

  function errorDetail(payload) {
    if (payload && typeof payload.detail === "string" && payload.detail.trim()) return payload.detail;
    return "La consulta no devolvió una respuesta.";
  }

  function showError(message, canRetry) {
    result.dataset.state = "error";
    resultBody.replaceChildren();
    const alert = document.createElement("div");
    alert.setAttribute("role", "alert");
    alert.tabIndex = -1;
    const title = document.createElement("p");
    title.className = "result-title";
    title.textContent = "No se pudo obtener la respuesta";
    const paragraph = document.createElement("p");
    paragraph.textContent = message;
    alert.append(title, paragraph);
    if (canRetry) {
      const retry = document.createElement("button");
      retry.type = "button";
      retry.textContent = "Reintentar la consulta";
      retry.addEventListener("click", function () { form.requestSubmit(); });
      alert.append(retry);
    }
    resultBody.appendChild(alert);
    live.textContent = "Error al consultar. La pregunta sigue en el campo.";
    alert.focus();
  }

  function showSuccess(answer) {
    const parts = splitSources(answer);
    result.dataset.state = "success";
    resultBody.replaceChildren();
    const article = document.createElement("div");
    article.className = "answer";
    parts.body.split(/\n+/).forEach(function (line) {
      if (!line.trim()) return;
      const paragraph = document.createElement("p");
      paragraph.textContent = line;
      article.appendChild(paragraph);
    });
    resultBody.appendChild(article);
    if (parts.sources.length) {
      const heading = document.createElement("h3");
      heading.textContent = "Fuentes citadas";
      const list = document.createElement("ul");
      parts.sources.forEach(function (source) {
        const item = document.createElement("li");
        item.textContent = source;
        list.appendChild(item);
      });
      resultBody.append(heading, list);
    }
    const copy = document.createElement("button");
    copy.type = "button";
    copy.textContent = "Copiar respuesta";
    copy.addEventListener("click", function () {
      if (!navigator.clipboard) {
        copy.textContent = "No se pudo copiar";
        return;
      }
      navigator.clipboard.writeText(answer).then(function () {
        copy.textContent = "Respuesta copiada";
      }).catch(function () {
        copy.textContent = "No se pudo copiar";
      });
    });
    resultBody.appendChild(copy);
    live.textContent = "Respuesta lista.";
  }

  function splitSources(answer) {
    const body = [];
    const sources = [];
    answer.split(/\n/).forEach(function (line) {
      const stripped = line.trim();
      if (stripped.indexOf("Sources:") === 0 || stripped.indexOf("Fuentes:") === 0) {
        sources.push(stripped.slice(stripped.indexOf(":") + 1).trim());
      } else {
        body.push(line);
      }
    });
    return { body: body.join("\n").trim(), sources: sources };
  }

  fetch("/knowledge/catalog", { headers: { "Accept": "application/json" } })
    .then(function (response) { return response.json(); })
    .then(function (payload) {
      documents.replaceChildren();
      (payload.documents || []).forEach(function (item) {
        const li = document.createElement("li");
        li.textContent = item.title + " · " + item.language;
        documents.appendChild(li);
      });
    })
    .catch(function () {
      documents.replaceChildren();
      const li = document.createElement("li");
      li.textContent = "No se pudo cargar la lista de documentos.";
      documents.appendChild(li);
    });

  fetch("/knowledge/status", { headers: { "Accept": "application/json" } })
    .then(function (response) { return response.json(); })
    .then(function (payload) {
      if (!payload.reachable) {
        status.textContent = "Qdrant no responde. La consulta mostrará el error del servicio, no una respuesta vacía.";
        return;
      }
      if (!payload.indexed) {
        status.textContent = "La colección " + payload.collection + " todavía no está indexada.";
        return;
      }
      status.textContent = "Colección " + payload.collection + ". " + payload.chunk_count + " fragmentos indexados.";
    })
    .catch(function () {
      status.textContent = "No se pudo comprobar la colección.";
    });
})();
