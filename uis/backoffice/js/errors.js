(function () {
  var CATALOG = {
    0: "No hay conexión con la API. Los datos escritos se conservan.",
    400: "La solicitud no se puede procesar. Revisa los datos e inténtalo de nuevo.",
    401: "Falta un token válido.",
    403: "No tienes permiso para ese recurso.",
    404: "No encontrado.",
    409: "Ya existe una cuenta con ese correo.",
    413: "El fichero supera el tamaño permitido.",
    422: "Hay datos que no se pueden aceptar. Revisa el formulario.",
    500: "No se pudo completar la operación. Inténtalo de nuevo."
  };
  var LEAK = /traceback|file "|jwt_secret|hashed_password|unexpected token|syntaxerror|sqlite:\/\/|postgres|mongodb:\/\/|\.env\b|\/workspace\/|secret-sentinel|error\s+\d{3}\b/i;

  function catalog(status) {
    if (status >= 500) return CATALOG[500];
    return CATALOG[status] || "No se pudo completar la solicitud.";
  }

  function readable(text) {
    if (!text || text.length > 400) return false;
    if (/^\d{3}$/.test(text)) return false;
    if (LEAK.test(text)) return false;
    return true;
  }

  function parseJson(text) {
    if (!text) return null;
    try {
      return JSON.parse(text);
    } catch (err) {
      return null;
    }
  }

  function human(status, text, fallback) {
    var data = parseJson(text);
    var message = "";
    if (data && typeof data.message === "string") message = data.message;
    else if (data && typeof data.detail === "string") message = data.detail;
    if (status === 409 && readable(message)) return message;
    if (status === 409) return CATALOG[409];
    if (status >= 500) return fallback || catalog(500);
    if (readable(message)) return message;
    return fallback || catalog(status);
  }

  window.nexovaErrors = {
    catalog: catalog,
    human: human,
    parseJson: parseJson
  };
})();
