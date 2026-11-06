(function () {
  var form = document.getElementById("incident-form");
  var panel = document.getElementById("incident-list");
  if (!form && !panel) return;

  var REQUIRED = {
    title: "El título es obligatorio.",
    description: "La descripción es obligatoria.",
    category: "La categoría es obligatoria.",
    status: "El estado es obligatorio.",
    origin: "El origen es obligatorio.",
    branch: "La sede es obligatoria."
  };

  function authHeaders(extra) {
    if (window.nexovaAuth) return window.nexovaAuth.headers(extra);
    return extra;
  }

  function token() {
    return window.nexovaAuth && window.nexovaAuth.token ? window.nexovaAuth.token() : "";
  }

  var SUMMARY_ERROR = '<div class="error-banner"><p id="incident-summary-error">No se pudo cargar el resumen. El listado de abajo sigue disponible.</p><p class="actions"><button class="button button-secondary" id="incident-summary-retry" type="button">Reintentar el resumen</button><a class="button button-secondary" href="/">Ir al inicio</a></p><p>Si se repite, contacta con el soporte interno de Nexova.</p></div>';

  function readJson(text) {
    if (window.nexovaErrors) return window.nexovaErrors.parseJson(text);
    try {
      return JSON.parse(text);
    } catch (err) {
      return null;
    }
  }

  function messageFrom(text, fallback) {
    if (window.nexovaErrors) return window.nexovaErrors.human(0, text, fallback);
    var data = readJson(text);
    if (data && typeof data.message === "string" && data.message && data.message.indexOf("Traceback") === -1) {
      return data.message;
    }
    return fallback;
  }

  function friendly(status, text, fallback) {
    if (status === 401) return "Hace falta una sesión. Entra y vuelve a intentarlo. Los datos se conservan.";
    if (window.nexovaErrors) return window.nexovaErrors.human(status, text, fallback);
    if (status >= 500) return fallback;
    return messageFrom(text, fallback);
  }

  if (form) setupForm(form);
  if (panel) setupPanel(panel);

  function setupForm(current) {
    var submit = document.getElementById("incident-submit");
    var statusEl = document.getElementById("incident-form-status");
    var banner = document.getElementById("incident-form-error");
    var confirmation = document.getElementById("incident-confirmation");
    var origin = document.getElementById("incident-origin");
    var branchField = document.getElementById("branch-field");
    var reminder = document.getElementById("branch-reminder");
    var fields = ["title", "description", "category", "status", "origin", "branch"];

    current.noValidate = true;

    function fieldNode(name) {
      return document.getElementById("incident-" + name);
    }

    function showFieldError(name, message) {
      var node = document.getElementById(name + "-error");
      var input = fieldNode(name);
      if (!node || !input) return;
      node.hidden = !message;
      node.textContent = message || "";
      if (message) input.setAttribute("aria-invalid", "true");
      else input.removeAttribute("aria-invalid");
    }

    var formCta = document.getElementById("incident-form-cta");

    function clearFields() {
      fields.forEach(function (name) { showFieldError(name, ""); });
      banner.hidden = true;
      banner.textContent = "";
      if (formCta) formCta.hidden = true;
    }

    function syncBranch() {
      var on = origin && origin.value === "branch";
      if (branchField) branchField.setAttribute("data-highlight", on ? "1" : "0");
      if (reminder) reminder.hidden = !on;
    }

    function setBusy(busy) {
      submit.disabled = busy;
      submit.setAttribute("aria-busy", busy ? "true" : "false");
      submit.textContent = busy ? "Guardando…" : "Registrar incidencia";
      statusEl.className = busy ? "loading-state" : "";
      statusEl.textContent = busy ? "Enviando la incidencia…" : "";
    }

    function clientErrors() {
      var found = [];
      fields.forEach(function (name) {
        var input = fieldNode(name);
        var value = input ? input.value.trim() : "";
        if (!value) found.push({ field: name, message: REQUIRED[name] });
      });
      return found;
    }

    function showErrors(errors, summary) {
      clearFields();
      errors.forEach(function (item) { showFieldError(item.field, item.message); });
      banner.hidden = false;
      banner.textContent = summary;
      if (formCta) formCta.hidden = false;
      var first = errors[0] && fieldNode(errors[0].field);
      if (first) first.focus();
      else banner.focus();
    }

    if (origin) origin.addEventListener("change", syncBranch);
    syncBranch();

    current.addEventListener("submit", function (event) {
      event.preventDefault();
      if (submit.disabled) return;
      confirmation.hidden = true;
      confirmation.textContent = "";
      var errors = clientErrors();
      if (errors.length) {
        showErrors(errors, "Revisa los campos marcados.");
        return;
      }
      clearFields();
      setBusy(true);
      var body = {};
      fields.forEach(function (name) { body[name] = fieldNode(name).value.trim(); });
      fetch("/api/incidents", {
        method: "POST",
        headers: authHeaders({ Accept: "application/json", "Content-Type": "application/json" }),
        body: JSON.stringify(body),
        cache: "no-store"
      }).then(function (response) {
        return response.text().then(function (text) {
          return { ok: response.ok, status: response.status, text: text };
        });
      }).then(function (response) {
        setBusy(false);
        if (response.status === 400) {
          var parsed = readJson(response.text) || {};
          var list = parsed.errors && parsed.errors.length ? parsed.errors : [{ field: parsed.field || "title", message: friendly(400, response.text, "Revisa los datos e inténtalo de nuevo.") }];
          showErrors(list, "Revisa los campos marcados.");
          return;
        }
        if (!response.ok) {
          showErrors([], "");
          banner.hidden = false;
          banner.textContent = friendly(response.status, response.text, "No se pudo registrar la incidencia. Inténtalo de nuevo.");
          if (formCta) formCta.hidden = false;
          banner.focus();
          return;
        }
        var created = readJson(response.text);
        if (!created || !created.id) {
          setBusy(false);
          banner.hidden = false;
          banner.textContent = "La respuesta no se pudo leer. Revisa el panel antes de repetir el alta.";
          if (formCta) formCta.hidden = false;
          banner.focus();
          return;
        }
        fields.forEach(function (name) {
          var input = fieldNode(name);
          if (!input) return;
          input.value = name === "status" ? "open" : "";
        });
        syncBranch();
        confirmation.hidden = false;
        confirmation.setAttribute("data-just-saved", "1");
        confirmation.textContent = "Incidencia registrada. Identificador " + created.id + ".";
        confirmation.focus();
      }).catch(function () {
        setBusy(false);
        banner.hidden = false;
        banner.textContent = "No hay conexión con la API. Los datos del formulario se conservan.";
        if (formCta) formCta.hidden = false;
        banner.focus();
      });
    });
  }

  function setupPanel() {
    var summary = document.getElementById("incident-summary");
    var summaryBody = document.getElementById("incident-summary-body");
    var list = document.getElementById("incident-list");
    var listStatus = document.getElementById("incident-list-status");
    var listError = document.getElementById("incident-list-error");
    var listErrorText = document.getElementById("incident-list-error-text");
    var retry = document.getElementById("incident-retry");
    var filterForm = document.getElementById("incident-filters");
    var labelsNode = document.getElementById("incident-labels");
    var labels = labelsNode ? readJson(labelsNode.textContent || "") : null;
    if (!labels) {
      summary.setAttribute("data-state", "error");
      summaryBody.innerHTML = SUMMARY_ERROR;
      listError.hidden = false;
      listErrorText.textContent = "No se pudieron leer las etiquetas de esta página. Recarga e inténtalo de nuevo.";
      return;
    }
    var listSeq = 0;
    var summarySeq = 0;
    var listController = null;

    function filters() {
      return {
        status: filterForm.status.value,
        origin: filterForm.origin.value,
        branch: filterForm.branch.value,
        category: filterForm.category.value
      };
    }

    function query(values) {
      var params = new URLSearchParams();
      ["status", "origin", "branch", "category"].forEach(function (name) {
        if (values[name]) params.set(name, values[name]);
      });
      var text = params.toString();
      return text ? "?" + text : "";
    }

    function labelFor(group, code) {
      var found = labels[group].filter(function (item) { return item.value === code; })[0];
      return found ? found.label : code;
    }

    function showListError(message) {
      listError.hidden = false;
      listErrorText.textContent = message;
    }

    function clearListError() {
      listError.hidden = true;
      listErrorText.textContent = "";
    }

    function lockedList() {
      list.setAttribute("data-state", "locked");
      list.innerHTML = '<div data-list-state="locked"><h3>Hace falta una sesión</h3><p>Entra para ver las incidencias registradas.</p></div>';
      summary.setAttribute("data-state", "locked");
      summaryBody.innerHTML = "<p>Entra con tu sesión para ver los totales.</p>";
      listStatus.textContent = "";
    }

    function renderSummary(data) {
      var groups = [
        ["Por estado", "by_status", "statuses"],
        ["Por categoría", "by_category", "categories"],
        ["Por origen", "by_origin", "origins"],
        ["Por sede", "by_branch", "branches"]
      ];
      var html = '<div class="summary-grid">';
      groups.forEach(function (group) {
        html += '<div class="table-scroll" tabindex="0" aria-label="Desplazamiento: ' + group[0] + '"><table><caption>' + group[0] + '</caption><thead><tr><th scope="col">Código</th><th scope="col">Total</th><th scope="col">Significado</th></tr></thead><tbody>';
        labels[group[2]].forEach(function (item) {
          var count = data[group[1]][item.value] || 0;
          html += "<tr><th scope=\"row\" class=\"code\">" + item.value + "</th><td class=\"num\">" + count + "</td><td>" + item.label + "</td></tr>";
        });
        html += "</tbody></table></div>";
      });
      html += '<p id="incident-summary-total">Total de incidencias: ' + data.total + '.</p></div>';
      summaryBody.innerHTML = html;
      summary.setAttribute("data-state", "ready");
      annotateFilters(data);
    }

    function annotateFilters(data) {
      var map = {
        status: ["by_status", "Todos"],
        origin: ["by_origin", "Todos"],
        branch: ["by_branch", "Todas"],
        category: ["by_category", "Todas"]
      };
      Object.keys(map).forEach(function (name) {
        var select = filterForm.elements[name];
        Array.prototype.forEach.call(select.options, function (option) {
          if (!option.getAttribute("data-base")) option.setAttribute("data-base", option.textContent);
          var base = option.getAttribute("data-base");
          if (!option.value) {
            option.textContent = base;
            return;
          }
          var count = data[map[name][0]][option.value];
          option.textContent = base + " (" + (count || 0) + ")";
        });
      });
    }

    function renderRows(items) {
      if (!items.length) {
        var active = ["status", "origin", "branch", "category"].some(function (name) { return filters()[name]; });
        var text = active
          ? "Ninguna incidencia coincide con esos filtros. Quita uno o registra una incidencia nueva."
          : "Todavía no hay incidencias. Registra la primera desde el formulario.";
        list.innerHTML = '<div data-list-state="empty"><h3>Sin incidencias para mostrar</h3><p>' + text + '</p><p><a class="button" href="/incidencias/nueva">Registrar incidencia</a></p></div>';
        list.setAttribute("data-state", "empty");
        listStatus.textContent = "Sin resultados para los filtros actuales.";
        return;
      }
      var html = '<div data-list-state="ready"><p>Mostrando ' + items.length + ' incidencias con los filtros actuales.</p><div class="table-scroll" tabindex="0" aria-label="Desplazamiento horizontal del listado de incidencias"><table><caption>Incidencias registradas</caption><thead><tr><th scope="col">Título</th><th scope="col">Categoría</th><th scope="col">Origen</th><th scope="col">Sede</th><th scope="col">Estado</th><th scope="col">Alta</th></tr></thead><tbody>';
      items.forEach(function (item) {
        var next = [item.status].concat(labels.transitions[item.status] || []);
        var options = "";
        var seen = {};
        next.forEach(function (code) {
          if (seen[code]) return;
          seen[code] = true;
          options += '<option value="' + code + '"' + (code === item.status ? " selected" : "") + ">" + labelFor("statuses", code) + "</option>";
        });
        var disabled = (labels.transitions[item.status] || []).length ? "" : " disabled";
        html += '<tr id="incidencia-' + item.id + '" data-id="' + item.id + '" data-status="' + item.status + '">';
        html += "<th scope=\"row\">" + escapeText(item.title) + "<details><summary>Ver descripción</summary><p>" + escapeText(item.description) + "</p></details></th>";
        html += "<td>" + escapeText(labelFor("categories", item.category)) + "</td>";
        html += "<td>" + escapeText(labelFor("origins", item.origin)) + "</td>";
        html += "<td>" + escapeText(labelFor("branches", item.branch)) + "</td>";
        html += '<td><label for="status-' + item.id + '">Cambiar estado</label><select id="status-' + item.id + '" data-status-select data-current="' + item.status + '"' + disabled + ' aria-describedby="status-hint-' + item.id + '">' + options + '</select><p id="status-hint-' + item.id + '" class="field-hint"></p></td>';
        html += '<td class="code">' + escapeText(item.created_at) + "</td></tr>";
      });
      html += "</tbody></table></div></div>";
      list.innerHTML = html;
      list.setAttribute("data-state", "ready");
      listStatus.textContent = "Mostrando " + items.length + " incidencias con los filtros actuales.";
    }

    function escapeText(value) {
      return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function loadSummary() {
      var seq = ++summarySeq;
      summary.setAttribute("data-state", "loading");
      summary.setAttribute("aria-busy", "true");
      summaryBody.innerHTML = '<p class="loading-state">Cargando el resumen…</p>';
      return fetch("/api/incidents/summary", {
        headers: authHeaders({ Accept: "application/json" }),
        cache: "no-store"
      }).then(function (response) {
        return response.text().then(function (text) {
          return { ok: response.ok, status: response.status, text: text };
        });
      }).then(function (response) {
        if (seq !== summarySeq) return;
        summary.setAttribute("aria-busy", "false");
        if (!response.ok) {
          summary.setAttribute("data-state", "error");
          summaryBody.innerHTML = SUMMARY_ERROR;
          return;
        }
        var summaryData = readJson(response.text);
        if (!summaryData) {
          summary.setAttribute("data-state", "error");
          summaryBody.innerHTML = SUMMARY_ERROR;
          return;
        }
        renderSummary(summaryData);
      }).catch(function () {
        if (seq !== summarySeq) return;
        summary.setAttribute("aria-busy", "false");
        summary.setAttribute("data-state", "error");
        summaryBody.innerHTML = SUMMARY_ERROR;
      });
    }

    function loadList() {
      var seq = ++listSeq;
      if (listController) listController.abort();
      listController = new AbortController();
      var values = filters();
      if (window.history && window.history.replaceState) {
        window.history.replaceState(null, "", "/incidencias" + query(values));
      }
      list.setAttribute("data-state", "loading");
      list.setAttribute("aria-busy", "true");
      listStatus.className = "loading-state";
      listStatus.textContent = "Cargando incidencias…";
      clearListError();
      return fetch("/api/incidents" + query(values), {
        headers: authHeaders({ Accept: "application/json" }),
        signal: listController.signal,
        cache: "no-store"
      }).then(function (response) {
        return response.text().then(function (text) {
          return { ok: response.ok, status: response.status, text: text };
        });
      }).then(function (response) {
        if (seq !== listSeq) return;
        list.setAttribute("aria-busy", "false");
        if (!response.ok) {
          list.setAttribute("data-state", "error");
          listStatus.className = "";
          listStatus.textContent = "";
          showListError(friendly(response.status, response.text, "No se pudo cargar el listado. Inténtalo de nuevo."));
          if (!list.querySelector("[data-list-state='ready']")) {
            list.innerHTML = '<div data-list-state="error"><h3>No se pudo cargar el listado</h3><p>La página sigue disponible. Usa Reintentar.</p></div>';
          }
          return;
        }
        var rows = readJson(response.text);
        if (!Array.isArray(rows)) {
          list.setAttribute("data-state", "error");
          listStatus.className = "";
          listStatus.textContent = "";
          showListError("No se pudo leer el listado. Inténtalo de nuevo.");
          return;
        }
        clearListError();
        listStatus.className = "";
        renderRows(rows);
      }).catch(function (err) {
        if (err && err.name === "AbortError") return;
        if (seq !== listSeq) return;
        list.setAttribute("aria-busy", "false");
        list.setAttribute("data-state", "error");
        listStatus.className = "";
        listStatus.textContent = "";
        showListError("No hay conexión con la API. Inténtalo de nuevo.");
      });
    }

    function loadAll() {
      if (!token()) {
        lockedList();
        return;
      }
      loadSummary();
      loadList();
    }

    summary.addEventListener("click", function (event) {
      if (event.target && event.target.id === "incident-summary-retry") loadSummary();
    });
    retry.addEventListener("click", function () { loadList(); });
    filterForm.addEventListener("submit", function (event) {
      event.preventDefault();
      loadList();
    });
    ["status", "origin", "branch", "category"].forEach(function (name) {
      filterForm.elements[name].addEventListener("change", function () { loadList(); });
    });
    list.addEventListener("change", function (event) {
      var select = event.target;
      if (!select.matches || !select.matches("[data-status-select]")) return;
      var previous = select.getAttribute("data-current");
      var next = select.value;
      var row = select.closest("tr");
      var hint = document.getElementById(select.getAttribute("aria-describedby"));
      if (next === previous) return;
      select.disabled = true;
      fetch("/api/incidents/" + row.getAttribute("data-id") + "/status", {
        method: "PATCH",
        headers: authHeaders({ Accept: "application/json", "Content-Type": "application/json" }),
        body: JSON.stringify({ status: next }),
        cache: "no-store"
      }).then(function (response) {
        return response.text().then(function (text) {
          return { ok: response.ok, status: response.status, text: text };
        });
      }).then(function (response) {
        if (!response.ok) {
          select.value = previous;
          select.disabled = (labels.transitions[previous] || []).length === 0;
          if (hint) hint.textContent = friendly(response.status, response.text, "No se pudo cambiar el estado. Se ha recuperado el valor anterior.");
          showListError("No se pudo cambiar el estado. Se ha recuperado el valor anterior.");
          return;
        }
        if (hint) hint.textContent = "";
        clearListError();
        row.setAttribute("data-just-updated", "1");
        loadSummary();
        loadList();
      }).catch(function () {
        select.value = previous;
        select.disabled = false;
        showListError("No se pudo cambiar el estado. Se ha recuperado el valor anterior.");
      });
    });

    window.addEventListener("nexova-session", loadAll);
    if (token()) loadAll();
    else if (list.getAttribute("data-state") === "locked") lockedList();
  }
})();
