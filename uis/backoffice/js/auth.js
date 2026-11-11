(function () {
  var KEY = "nexova-access-token";
  var loginForm = document.getElementById("session-login");
  var registerForm = document.getElementById("session-register");
  if (!loginForm || !registerForm) {
    return;
  }

  var statusEl = document.getElementById("session-status");
  var errorEl = document.getElementById("session-error");
  var loginButton = document.getElementById("session-login-submit");
  var registerButton = document.getElementById("session-register-submit");
  var showRegister = document.getElementById("session-show-register");
  var logoutButton = document.getElementById("session-logout");

  loginForm.noValidate = true;
  registerForm.noValidate = true;

  function token() {
    try {
      return sessionStorage.getItem(KEY) || "";
    } catch (err) {
      return "";
    }
  }

  function headers(extra) {
    var out = {};
    var key;
    if (extra) {
      for (key in extra) {
        if (Object.prototype.hasOwnProperty.call(extra, key)) {
          out[key] = extra[key];
        }
      }
    }
    var value = token();
    if (value) {
      out.Authorization = "Bearer " + value;
    }
    return out;
  }

  function showError(message) {
    errorEl.hidden = false;
    errorEl.textContent = message;
    errorEl.focus();
  }

  function clearError() {
    errorEl.hidden = true;
    errorEl.textContent = "";
  }

  function setBusy(busy) {
    loginButton.disabled = busy;
    registerButton.disabled = busy;
    showRegister.disabled = busy;
    loginButton.setAttribute("aria-busy", busy ? "true" : "false");
    registerButton.setAttribute("aria-busy", busy ? "true" : "false");
  }

  function remember(value) {
    try {
      sessionStorage.setItem(KEY, value);
      return true;
    } catch (err) {
      showError("Esta pestaña no puede guardar el token. La API sigue pidiendo Authorization.");
      return false;
    }
  }

  function announce(me) {
    var name = me.profile && me.profile.name ? " (" + me.profile.name + ")" : "";
    statusEl.textContent = "Sesión iniciada como " + me.email + name + ". Rol: " + me.role + ".";
    logoutButton.hidden = false;
    showRegister.hidden = true;
  }

  function signedOutCopy() {
    statusEl.textContent = "No hay una sesión en esta pestaña. El análisis y el directorio piden un token.";
    logoutButton.hidden = true;
    showRegister.hidden = false;
  }

  function publish() {
    window.dispatchEvent(new Event("nexova-session"));
  }

  function messageFrom(text, fallback) {
    try {
      var data = JSON.parse(text);
      if (data && typeof data.message === "string" && data.message) return data.message;
      if (data && typeof data.detail === "string" && data.detail) return data.detail;
    } catch (err) {
      /* The fallback stays readable when the body is HTML. */
    }
    return fallback;
  }

  function readMe() {
    return fetch("/auth/me", {
      headers: headers({ Accept: "application/json" }),
      cache: "no-store"
    }).then(function (response) {
      return response.text().then(function (text) {
        return { ok: response.ok, status: response.status, text: text };
      });
    });
  }

  function login(email, password) {
    setBusy(true);
    clearError();
    statusEl.textContent = "Comprobando la sesión…";
    return fetch("/auth/login", {
      method: "POST",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, password: password }),
      cache: "no-store"
    }).then(function (response) {
      return response.text().then(function (text) {
        return { ok: response.ok, text: text };
      });
    }).then(function (response) {
      if (!response.ok) {
        setBusy(false);
        statusEl.textContent = "";
        showError(messageFrom(response.text, "No se pudo iniciar sesión."));
        return;
      }
      var data = JSON.parse(response.text);
      if (!data.access_token || !remember(data.access_token)) {
        setBusy(false);
        return;
      }
      return readMe().then(function (me) {
        setBusy(false);
        if (!me.ok) {
          showError(messageFrom(me.text, "El token no se pudo comprobar."));
          return;
        }
        clearError();
        announce(JSON.parse(me.text));
        publish();
      });
    }).catch(function () {
      setBusy(false);
      statusEl.textContent = "";
      showError("No hay conexión con la API. Los datos del formulario se conservan.");
    });
  }

  window.nexovaAuth = { token: token, headers: headers };

  loginForm.addEventListener("submit", function (event) {
    event.preventDefault();
    if (loginButton.disabled) return;
    login(loginForm.email.value.trim(), loginForm.password.value);
  });

  showRegister.addEventListener("click", function () {
    registerForm.hidden = !registerForm.hidden;
    if (!registerForm.hidden) {
      document.getElementById("register-email").focus();
    }
  });

  registerForm.addEventListener("submit", function (event) {
    event.preventDefault();
    if (registerButton.disabled) return;
    var email = registerForm.email.value.trim();
    var password = registerForm.password.value;
    if (password.length < 8) {
      showError("La contraseña tiene que tener al menos 8 caracteres.");
      return;
    }
    setBusy(true);
    clearError();
    statusEl.textContent = "Creando la cuenta…";
    var body = {
      email: email,
      password: password,
      name: registerForm.name.value.trim() || null,
      phone: registerForm.phone.value.trim() || null,
      address: registerForm.address.value.trim() || null
    };
    fetch("/users", {
      method: "POST",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store"
    }).then(function (response) {
      return response.text().then(function (text) {
        return { ok: response.ok, text: text };
      });
    }).then(function (response) {
      if (!response.ok) {
        setBusy(false);
        statusEl.textContent = "";
        showError(messageFrom(response.text, "No se pudo crear la cuenta. Los datos se conservan."));
        return;
      }
      registerForm.reset();
      registerForm.hidden = true;
      return login(email, password);
    }).catch(function () {
      setBusy(false);
      statusEl.textContent = "";
      showError("No hay conexión con la API. Los datos del formulario se conservan.");
    });
  });

  logoutButton.addEventListener("click", function () {
    try {
      sessionStorage.removeItem(KEY);
    } catch (err) {
      /* Reloading still drops the in-memory copy. */
    }
    window.location.reload();
  });

  if (token()) {
    statusEl.textContent = "Comprobando la sesión…";
    readMe().then(function (me) {
      if (!me.ok) {
        try {
          sessionStorage.removeItem(KEY);
        } catch (err) {
          /* The next request will still fail closed. */
        }
        signedOutCopy();
        showError(messageFrom(me.text, "La sesión guardada ya no es válida."));
        return;
      }
      announce(JSON.parse(me.text));
      publish();
    }).catch(function () {
      signedOutCopy();
      showError("No hay conexión con la API para comprobar la sesión.");
    });
  }
})();
