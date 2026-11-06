(function () {
  var form = document.getElementById("analyze-form");
  if (!form) {
    return;
  }
  var fileInput = document.getElementById("csv-file");
  var submit = document.getElementById("submit");
  var statusEl = document.getElementById("status");
  var errorEl = document.getElementById("error");
  var errorText = document.getElementById("error-text");
  var resultsEl = document.getElementById("results");
  var drop = document.getElementById("drop");
  var chosen = document.getElementById("chosen-file");
  var storageKey = "nexova-incidents-report-fragment";
  var requestSeq = 0;

  function setBusy(busy) {
    form.setAttribute("data-busy", busy ? "1" : "0");
    submit.disabled = busy;
    submit.setAttribute("aria-busy", busy ? "true" : "false");
  }

  function showError(message) {
    errorText.textContent = message;
    errorEl.hidden = false;
    errorEl.focus();
  }

  function clearError() {
    errorEl.hidden = true;
    errorText.textContent = "";
  }

  function remember(html) {
    try {
      sessionStorage.setItem(storageKey, html);
    } catch (err) {
      /* Storage can be blocked. The page still shows the result. */
    }
  }

  function restore() {
    if (resultsEl.getAttribute("data-state") === "success") {
      remember(resultsEl.innerHTML);
      return;
    }
    var saved = "";
    try {
      saved = sessionStorage.getItem(storageKey) || "";
    } catch (err) {
      saved = "";
    }
    if (!saved || saved.indexOf("@") !== -1) {
      return;
    }
    resultsEl.innerHTML = saved;
    resultsEl.setAttribute("data-state", "success");
    statusEl.textContent = "Se muestra el último análisis de esta pestaña. Si la descarga falla, analiza el fichero de nuevo.";
  }

  function saveBlob(blob) {
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = "results.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  restore();

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (form.getAttribute("data-busy") === "1") {
      return;
    }
    if (!fileInput.files || !fileInput.files.length) {
      showError("Elige un fichero CSV antes de analizar.");
      fileInput.focus();
      return;
    }
    var previousHtml = resultsEl.getAttribute("data-state") === "success" ? resultsEl.innerHTML : "";
    var seq = ++requestSeq;
    if (form._controller) {
      form._controller.abort();
    }
    var controller = new AbortController();
    form._controller = controller;
    setBusy(true);
    clearError();
    resultsEl.setAttribute("data-state", "loading");
    resultsEl.replaceChildren();
    var loading = document.createElement("p");
    loading.textContent = "Analizando el fichero. El cálculo sigue en la API interna.";
    resultsEl.appendChild(loading);
    statusEl.textContent = loading.textContent;
    fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { Accept: "text/html", "X-Report-Fragment": "1" },
      signal: controller.signal,
      cache: "no-store"
    }).then(function (response) {
      return response.text().then(function (text) {
        return { ok: response.ok, text: text };
      });
    }).then(function (response) {
      if (seq !== requestSeq) {
        return;
      }
      if (!response.ok || response.text.indexOf("@") !== -1) {
        var message = "No se pudo analizar el fichero.";
        if (response.text.indexOf("@") === -1) {
          try {
            var data = JSON.parse(response.text);
            if (data && data.message) {
              message = data.message;
            }
          } catch (err) {
            if (response.text && response.text.indexOf("<") === -1) {
              message = response.text;
            }
          }
        }
        if (previousHtml && previousHtml.indexOf("@") === -1) {
          resultsEl.innerHTML = previousHtml;
          resultsEl.setAttribute("data-state", "success");
          statusEl.textContent = "Este fichero no se analizó. Sigue en pantalla el análisis anterior.";
        } else {
          resultsEl.setAttribute("data-state", "error");
          resultsEl.replaceChildren();
          statusEl.textContent = "";
        }
        showError(message);
        return;
      }
      resultsEl.innerHTML = response.text;
      resultsEl.setAttribute("data-state", "success");
      remember(response.text);
      var summary = document.getElementById("report-summary");
      statusEl.textContent = summary ? summary.textContent : "Análisis listo.";
      var heading = document.getElementById("report-title");
      if (heading) {
        heading.focus();
      }
    }).catch(function (err) {
      if (err && err.name === "AbortError") {
        return;
      }
      if (seq !== requestSeq) {
        return;
      }
      if (previousHtml && previousHtml.indexOf("@") === -1) {
        resultsEl.innerHTML = previousHtml;
        resultsEl.setAttribute("data-state", "success");
        statusEl.textContent = "No hay conexión con la API. Sigue en pantalla el análisis anterior.";
      } else {
        resultsEl.setAttribute("data-state", "error");
        resultsEl.replaceChildren();
        statusEl.textContent = "";
      }
      showError("No hay conexión con la API. Comprueba que el servicio sigue en marcha y pulsa Analizar fichero.");
    }).then(function () {
      if (seq === requestSeq) {
        setBusy(false);
      }
    });
  });

  fileInput.addEventListener("change", function () {
    var file = fileInput.files && fileInput.files[0];
    chosen.textContent = file ? "Fichero elegido: " + file.name : "Ningún fichero elegido.";
  });

  ["dragenter", "dragover"].forEach(function (name) {
    drop.addEventListener(name, function (event) {
      event.preventDefault();
      drop.setAttribute("data-drag", "1");
      statusEl.textContent = "Suelta el CSV para elegirlo.";
    });
  });
  ["dragleave", "drop"].forEach(function (name) {
    drop.addEventListener(name, function (event) {
      event.preventDefault();
      if (name === "dragleave") {
        drop.setAttribute("data-drag", "0");
      }
    });
  });
  drop.addEventListener("drop", function (event) {
    drop.setAttribute("data-drag", "0");
    var files = event.dataTransfer && event.dataTransfer.files;
    if (!files || !files.length) {
      return;
    }
    fileInput.files = files;
    fileInput.dispatchEvent(new Event("change"));
    statusEl.textContent = "Fichero listo para analizar.";
  });

  document.addEventListener("click", function (event) {
    var link = event.target && event.target.closest ? event.target.closest("a[data-export]") : null;
    if (!link) {
      return;
    }
    event.preventDefault();
    var fallback = document.getElementById("export-csv");
    fetch(link.href, { headers: { Accept: "text/csv" }, cache: "no-store" }).then(function (response) {
      if (!response.ok) {
        throw new Error("missing");
      }
      return response.blob();
    }).then(function (blob) {
      saveBlob(blob);
      statusEl.textContent = "Descarga de results.csv iniciada desde la API.";
    }).catch(function () {
      if (fallback && fallback.textContent.indexOf("@") === -1 && fallback.textContent.indexOf("metric,") === 0) {
        saveBlob(new Blob([fallback.textContent], { type: "text/csv;charset=utf-8" }));
        statusEl.textContent = "La API no tiene el análisis. Se descarga la copia de esta pestaña.";
        return;
      }
      statusEl.textContent = "";
      showError("No hay un análisis guardado para descargar. Analiza el fichero de nuevo.");
    });
  });
})();
