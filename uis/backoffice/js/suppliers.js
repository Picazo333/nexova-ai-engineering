(function () {
  var form = document.getElementById("directory-filters");
  var createForm = document.getElementById("create-supplier");
  if (!form || !createForm) {
    return;
  }

  var list = document.getElementById("directory-list");
  var statusEl = document.getElementById("directory-status");
  var errorEl = document.getElementById("directory-error");
  var errorText = document.getElementById("directory-error-text");
  var noticeEl = document.getElementById("directory-notice");
  var memory = document.getElementById("filter-memory");
  var createError = document.getElementById("create-error");
  var createButton = document.getElementById("create-submit");
  var retry = document.getElementById("directory-retry");
  var storageKey = "nexova-supplier-directory-filters";
  var requestSeq = 0;
  var controller = null;

  createForm.noValidate = true;

  function filtersFromForm() {
    return {
      country: form.country.value,
      category: form.category.value,
      status: form.status.value
    };
  }

  function applyFilters(values) {
    form.country.value = values.country || "";
    form.category.value = values.category || "";
    form.status.value = values.status || "";
  }

  function saveFilters(values) {
    try {
      sessionStorage.setItem(storageKey, JSON.stringify(values));
    } catch (err) {
      /* The list still works for this visit. */
    }
  }

  function readFilters() {
    try {
      return JSON.parse(sessionStorage.getItem(storageKey) || "null");
    } catch (err) {
      return null;
    }
  }

  function queryString(values) {
    var params = new URLSearchParams();
    if (values.country) params.set("country", values.country);
    if (values.category) params.set("category", values.category);
    if (values.status) params.set("status", values.status);
    var text = params.toString();
    return text ? "?" + text : "";
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

  function showNotice(message) {
    noticeEl.hidden = false;
    noticeEl.textContent = message;
  }

  function messageFrom(text, fallback) {
    if (window.nexovaErrors) return window.nexovaErrors.human(422, text, fallback);
    try {
      var data = JSON.parse(text);
      if (data && typeof data.message === "string" && data.message && data.message.indexOf("Traceback") === -1) {
        return data.message;
      }
      if (data && typeof data.detail === "string" && data.detail && data.detail.indexOf("Traceback") === -1) {
        return data.detail;
      }
    } catch (err) {
      /* HTML responses use the fallback sentence. */
    }
    return fallback;
  }

  function loadList(updatedId) {
    var values = filtersFromForm();
    saveFilters(values);
    var nextUrl = "/proveedores" + queryString(values);
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, "", nextUrl);
    }
    var seq = ++requestSeq;
    if (controller) controller.abort();
    controller = new AbortController();
    list.setAttribute("aria-busy", "true");
    list.setAttribute("data-state", "loading");
    var pending = document.createElement("p");
    pending.id = "directory-loading";
    pending.className = "loading-state";
    pending.textContent = "Cargando proveedores…";
    list.prepend(pending);
    statusEl.textContent = "Cargando proveedores…";
    var listHeaders = { Accept: "text/html", "X-Directory-Fragment": "1" };
    return fetch(nextUrl, {
      headers: window.nexovaAuth ? window.nexovaAuth.headers(listHeaders) : listHeaders,
      signal: controller.signal,
      cache: "no-store"
    }).then(function (response) {
      return response.text().then(function (text) {
        return { ok: response.ok, status: response.status, text: text };
      });
    }).then(function (response) {
      if (seq !== requestSeq) return;
      var loading = document.getElementById("directory-loading");
      if (loading) loading.remove();
      list.setAttribute("aria-busy", "false");
      if (response.status === 401) {
        list.setAttribute("data-state", "locked");
        list.innerHTML = '<div data-list-state="locked"><h3>Hace falta una sesión</h3><p>Entra de nuevo para ver el directorio.</p></div>';
        statusEl.textContent = "";
        showError("La sesión no es válida o falta. Entra de nuevo para ver el directorio.");
        return;
      }
      if (!response.ok) {
        list.setAttribute("data-state", "error");
        statusEl.textContent = "";
        showError("No se pudo actualizar el listado. El directorio anterior sigue en pantalla.");
        return;
      }
      list.innerHTML = response.text;
      var stateNode = list.querySelector("[data-list-state]");
      list.setAttribute("data-state", stateNode ? stateNode.getAttribute("data-list-state") : "success");
      var summary = stateNode ? stateNode.querySelector("p") : null;
      statusEl.textContent = summary ? summary.textContent : "Listado actualizado.";
      clearError();
      if (updatedId) {
        var row = document.getElementById("proveedor-" + updatedId);
        if (row) row.setAttribute("data-just-updated", "1");
      }
    }).catch(function (err) {
      if (err && err.name === "AbortError") return;
      if (seq !== requestSeq) return;
      var loading = document.getElementById("directory-loading");
      if (loading) loading.remove();
      list.setAttribute("aria-busy", "false");
      list.setAttribute("data-state", "error");
      statusEl.textContent = "";
      showError("No se pudo actualizar el listado. El directorio anterior sigue en pantalla.");
    });
  }

  var params = new URLSearchParams(window.location.search);
  var fromUrl = params.has("country") || params.has("category") || params.has("status");
  var locked = !!list.querySelector("[data-list-state='locked']");
  if (!fromUrl) {
    var saved = readFilters();
    if (saved && (saved.country || saved.category || saved.status)) {
      applyFilters(saved);
      if (memory) {
        memory.textContent = "Se mantienen el país, la categoría y el estado de tu visita anterior.";
      }
      if (!locked) loadList();
    }
  } else {
    saveFilters(filtersFromForm());
  }

  window.addEventListener("nexova-session", function () {
    if (window.nexovaAuth && window.nexovaAuth.token()) loadList();
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    loadList();
  });

  ["country", "category", "status"].forEach(function (name) {
    form.elements[name].addEventListener("change", function () {
      loadList();
    });
  });

  document.addEventListener("click", function (event) {
    var target = event.target;
    if (!target || !target.closest) return;
    var link = target.closest('a[href="/proveedores"]');
    if (!link) return;
    try {
      sessionStorage.removeItem(storageKey);
    } catch (err) {
      /* Navigation still clears the query string. */
    }
  });

  if (retry) {
    retry.addEventListener("click", function () {
      loadList();
    });
  }

  var currencyByCountry = { Spain: "EUR", USA: "USD" };
  createForm.country.addEventListener("change", function () {
    var currency = currencyByCountry[createForm.country.value];
    if (currency) createForm.currency.value = currency;
  });

  function createErrors() {
    var errors = [];
    if (!createForm.name.value.trim()) errors.push("El nombre es obligatorio.");
    if (!createForm.country.value) errors.push("El país es obligatorio.");
    if (!createForm.querySelectorAll('input[name="categories"]:checked').length) {
      errors.push("Elige al menos una categoría.");
    }
    var rateRaw = createForm.monthly_rate.value.trim();
    var rate = Number(rateRaw);
    if (!rateRaw || !isFinite(rate) || rate <= 0) {
      errors.push("La tarifa mensual tiene que ser un número mayor que cero.");
    }
    if (createForm.status.value !== "active" && createForm.status.value !== "suspended") {
      errors.push("El estado solo puede ser active o suspended.");
    }
    var email = createForm.contact_email.value.trim();
    if (email && (email.indexOf("@") < 1 || email.indexOf(" ") !== -1 || email.indexOf(".") < 0)) {
      errors.push("El correo de contacto no tiene un formato válido.");
    }
    return errors;
  }

  createForm.addEventListener("submit", function (event) {
    event.preventDefault();
    if (createForm.getAttribute("data-busy") === "1") return;
    var errors = createErrors();
    if (errors.length) {
      createError.hidden = false;
      createError.textContent = errors.join(" ");
      createError.focus();
      return;
    }
    createError.hidden = true;
    createError.textContent = "";
    var categories = [];
    createForm.querySelectorAll('input[name="categories"]:checked').forEach(function (box) {
      categories.push(box.value);
    });
    var payload = {
      name: createForm.name.value.trim(),
      country: createForm.country.value,
      categories: categories,
      monthly_rate: Number(createForm.monthly_rate.value),
      currency: createForm.currency.value,
      status: createForm.status.value,
      contract_renewal_date: createForm.contract_renewal_date.value || null,
      contact_email: createForm.contact_email.value.trim() || null,
      notes: createForm.notes.value.trim() || null
    };
    createForm.setAttribute("data-busy", "1");
    createButton.disabled = true;
    createButton.setAttribute("aria-busy", "true");
    statusEl.textContent = "Registrando proveedor…";
    var createHeaders = { Accept: "application/json", "Content-Type": "application/json" };
    fetch("/suppliers", {
      method: "POST",
      headers: window.nexovaAuth ? window.nexovaAuth.headers(createHeaders) : createHeaders,
      body: JSON.stringify(payload),
      cache: "no-store"
    }).then(function (response) {
      return response.text().then(function (text) {
        return { ok: response.ok, text: text };
      });
    }).then(function (response) {
      createForm.setAttribute("data-busy", "0");
      createButton.disabled = false;
      createButton.setAttribute("aria-busy", "false");
      if (!response.ok) {
        createError.hidden = false;
        createError.textContent = messageFrom(response.text, "La API rechazó el proveedor. Los datos del formulario se conservan.");
        createError.focus();
        statusEl.textContent = "";
        return;
      }
      createForm.reset();
      showNotice("Proveedor registrado. Si no aparece, no coincide con los filtros activos.");
      statusEl.textContent = noticeEl.textContent;
      return loadList();
    }).catch(function () {
      createForm.setAttribute("data-busy", "0");
      createButton.disabled = false;
      createButton.setAttribute("aria-busy", "false");
      createError.hidden = false;
      createError.textContent = "No se pudo registrar el proveedor. Los datos del formulario se conservan.";
      createError.focus();
    });
  });

  document.addEventListener("submit", function (event) {
    var node = event.target;
    if (!node || !node.classList) return;
    if (node.classList.contains("rate-form")) {
      event.preventDefault();
      submitRate(node);
    } else if (node.classList.contains("status-form")) {
      event.preventDefault();
      submitStatus(node);
    }
  });

  function supplierId(action) {
    var match = String(action).match(/\/suppliers\/(\d+)\//);
    return match ? match[1] : "";
  }

  function submitRate(rateForm) {
    if (rateForm.getAttribute("data-busy") === "1") return;
    var input = rateForm.querySelector('input[name="monthly_rate"]');
    var button = rateForm.querySelector("button");
    var rate = Number(input.value);
    if (!String(input.value).trim() || !isFinite(rate) || rate <= 0) {
      showError("La tarifa mensual tiene que ser un número mayor que cero.");
      input.focus();
      return;
    }
    var id = supplierId(rateForm.getAttribute("action") || rateForm.action);
    rateForm.setAttribute("data-busy", "1");
    button.disabled = true;
    var rateHeaders = { Accept: "application/json", "Content-Type": "application/json" };
    fetch("/suppliers/" + id + "/rate", {
      method: "PATCH",
      headers: window.nexovaAuth ? window.nexovaAuth.headers(rateHeaders) : rateHeaders,
      body: JSON.stringify({ monthly_rate: rate }),
      cache: "no-store"
    }).then(function (response) {
      return response.text().then(function (text) {
        return { ok: response.ok, text: text };
      });
    }).then(function (response) {
      rateForm.setAttribute("data-busy", "0");
      button.disabled = false;
      if (!response.ok) {
        showError(messageFrom(response.text, "La API rechazó la tarifa."));
        return;
      }
      showNotice("Tarifa mensual actualizada. La hora del cambio quedó registrada.");
      return loadList(id);
    }).catch(function () {
      rateForm.setAttribute("data-busy", "0");
      button.disabled = false;
      showError("No se pudo actualizar la tarifa. El valor anterior sigue en el listado.");
    });
  }

  function submitStatus(statusForm) {
    if (statusForm.getAttribute("data-busy") === "1") return;
    var input = statusForm.querySelector('input[name="status"]');
    var button = statusForm.querySelector("button");
    var id = supplierId(statusForm.getAttribute("action") || statusForm.action);
    statusForm.setAttribute("data-busy", "1");
    button.disabled = true;
    var statusHeaders = { Accept: "application/json", "Content-Type": "application/json" };
    fetch("/suppliers/" + id + "/status", {
      method: "PATCH",
      headers: window.nexovaAuth ? window.nexovaAuth.headers(statusHeaders) : statusHeaders,
      body: JSON.stringify({ status: input.value }),
      cache: "no-store"
    }).then(function (response) {
      return response.text().then(function (text) {
        return { ok: response.ok, text: text };
      });
    }).then(function (response) {
      statusForm.setAttribute("data-busy", "0");
      button.disabled = false;
      if (!response.ok) {
        showError(messageFrom(response.text, "La API rechazó el estado."));
        return;
      }
      showNotice("Estado actualizado. El proveedor sigue en el directorio.");
      return loadList(id);
    }).catch(function () {
      statusForm.setAttribute("data-busy", "0");
      button.disabled = false;
      showError("No se pudo cambiar el estado. El listado anterior sigue en pantalla.");
    });
  }
})();
