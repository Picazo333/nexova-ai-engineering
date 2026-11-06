(function () {
  var KEY = "nexova-access-token";
  var sessionForm = document.getElementById("session-form");
  var sessionStatus = document.getElementById("session-status");
  var sessionError = document.getElementById("session-error");
  var sessionButton = document.getElementById("session-submit");
  var logoutButton = document.getElementById("session-logout");

  function token() {
    try {
      return sessionStorage.getItem(KEY) || "";
    } catch (err) {
      return "";
    }
  }

  function paintSession() {
    var value = token();
    if (value) {
      sessionStatus.textContent = "Hay una sesión en esta pestaña. La consulta de tickets la enviará.";
      logoutButton.hidden = false;
    } else {
      sessionStatus.textContent = "No hay una sesión en esta pestaña. La tool de tickets usa el mismo token que el gestor de incidentes.";
      logoutButton.hidden = true;
    }
  }

  function showSessionError(message) {
    sessionError.hidden = false;
    sessionError.textContent = message;
    sessionError.focus();
  }

  paintSession();

  sessionForm.addEventListener("submit", function (event) {
    event.preventDefault();
    if (sessionButton.disabled) {
      return;
    }
    sessionError.hidden = true;
    sessionButton.disabled = true;
    sessionStatus.textContent = "Comprobando la sesión.";
    var email = document.getElementById("session-email").value;
    var password = document.getElementById("session-password").value;
    fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ email: email, password: password })
    }).then(function (response) {
      return response.json().then(function (body) {
        return { ok: response.ok, body: body };
      });
    }).then(function (result) {
      sessionButton.disabled = false;
      if (!result.ok || !result.body.access_token) {
        showSessionError(result.body.detail || result.body.message || "No se pudo entrar.");
        paintSession();
        return;
      }
      try {
        sessionStorage.setItem(KEY, result.body.access_token);
      } catch (err) {
        showSessionError("Esta pestaña no puede guardar el token.");
      }
      document.getElementById("session-password").value = "";
      paintSession();
    }).catch(function () {
      sessionButton.disabled = false;
      showSessionError("No se pudo entrar. Inténtalo de nuevo.");
      paintSession();
    });
  });

  logoutButton.addEventListener("click", function () {
    try {
      sessionStorage.removeItem(KEY);
    } catch (err) {
      /* the next request simply goes without a token */
    }
    paintSession();
  });

  function bindExample(id) {
    var button = document.getElementById(id);
    button.addEventListener("click", function () {
      var field = document.getElementById(button.getAttribute("data-target"));
      field.value = button.getAttribute("data-question");
      field.focus();
    });
  }

  bindExample("rag-example");
  bindExample("tool-example");

  function bindLane(formId, buttonId, resultId, bodyId, traceId) {
    var form = document.getElementById(formId);
    var button = document.getElementById(buttonId);
    var result = document.getElementById(resultId);
    var body = document.getElementById(bodyId);
    var trace = document.getElementById(traceId);
    var generation = 0;

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (button.disabled) {
        return;
      }
      var questionField = form.querySelector("textarea");
      var question = questionField.value;
      generation += 1;
      var current = generation;
      button.disabled = true;
      result.setAttribute("data-state", "loading");
      result.setAttribute("aria-busy", "true");
      body.textContent = "Consultando esta ruta.";
      var headers = { "Content-Type": "application/json", Accept: "application/json" };
      var value = token();
      if (value) {
        headers.Authorization = "Bearer " + value;
      }
      fetch("/agent/query", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({ question: question })
      }).then(function (response) {
        return response.json().then(function (payload) {
          return { ok: response.ok, status: response.status, body: payload };
        });
      }).then(function (payload) {
        if (current !== generation) {
          return;
        }
        button.disabled = false;
        result.setAttribute("aria-busy", "false");
        if (!payload.ok) {
          result.setAttribute("data-state", "error");
          body.replaceChildren();
          var title = document.createElement("p");
          title.className = "result-title";
          title.textContent = "No se pudo consultar";
          var message = document.createElement("p");
          message.textContent = (payload.body && payload.body.detail) || "No se pudo consultar.";
          var retry = document.createElement("p");
          retry.textContent = "Revisa la pregunta y vuelve a consultar. El texto que escribiste se conserva.";
          body.append(title, message, retry);
          renderTrace(trace, payload.body && payload.body.trace);
          return;
        }
        var status = payload.body.trace && payload.body.trace.status;
        var empty = status === "ticket_unavailable" || status === "insufficient_context";
        result.setAttribute("data-state", empty ? "empty" : "success");
        body.replaceChildren();
        if (empty) {
          var emptyTitle = document.createElement("p");
          emptyTitle.className = "result-title";
          emptyTitle.textContent = "Sin dato confirmado";
          body.appendChild(emptyTitle);
        }
        String(payload.body.answer || "").split("\n").forEach(function (line) {
          if (!line.trim()) {
            return;
          }
          var paragraph = document.createElement("p");
          paragraph.textContent = line;
          body.appendChild(paragraph);
        });
        if (empty) {
          var hint = document.createElement("p");
          hint.textContent = "Puedes reintentar con otro id o volver a la base de conocimiento.";
          body.appendChild(hint);
        }
        renderTrace(trace, payload.body.trace);
      }).catch(function () {
        if (current !== generation) {
          return;
        }
        button.disabled = false;
        result.setAttribute("aria-busy", "false");
        result.setAttribute("data-state", "error");
        body.textContent = "No se pudo consultar. Inténtalo de nuevo. El texto que escribiste se conserva.";
      });
    });
  }

  function renderTrace(container, trace) {
    var heading = container.querySelector("h3");
    container.replaceChildren();
    if (heading) {
      container.appendChild(heading);
    } else {
      var created = document.createElement("h3");
      created.textContent = "Traza";
      container.appendChild(created);
    }
    if (!trace) {
      var missing = document.createElement("p");
      missing.textContent = "Esta respuesta no trajo traza.";
      container.appendChild(missing);
      return;
    }
    var summary = document.createElement("p");
    var sources = (trace.sources || []).join(" → ") || "ninguna";
    summary.textContent = "Ruta decidida: " + (trace.route || "sin ruta") + ". Fuentes en orden: " + sources + ".";
    var list = document.createElement("ol");
    (trace.nodes || []).forEach(function (step) {
      var item = document.createElement("li");
      var name = document.createElement("span");
      name.className = "node-name";
      name.textContent = step.order + ". " + step.node;
      item.appendChild(name);
      list.appendChild(item);
    });
    container.append(summary, list);
  }

  bindLane("rag-form", "rag-submit", "rag-result", "rag-body", "rag-trace");
  bindLane("tool-form", "tool-submit", "tool-result", "tool-body", "tool-trace");
}());
