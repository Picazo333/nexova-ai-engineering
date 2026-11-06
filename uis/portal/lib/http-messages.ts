/** HTTP status to a sentence a person can act on. Mirrors services/api/app/http_catalog.py. */

export const HTTP_CATALOG: Record<number, string> = {
  0: "No hay conexión con la API. Los datos escritos se conservan.",
  400: "La solicitud no se puede procesar. Revisa los datos e inténtalo de nuevo.",
  401: "Falta un token válido.",
  403: "No tienes permiso para ese recurso.",
  404: "No encontrado.",
  405: "Ese método no está admitido en esta ruta.",
  409: "Ya existe una cuenta con ese correo.",
  413: "El fichero supera el tamaño permitido.",
  422: "Hay datos que no se pueden aceptar. Revisa el formulario.",
  500: "No se pudo completar la operación. Inténtalo de nuevo.",
};

const LEAK =
  /traceback|file "|jwt_secret|hashed_password|unexpected token|syntaxerror|sqlite:\/\/|postgres(?:ql)?:\/\/|mongodb(?:\+srv)?:\/\/|mysql:\/\/|\.env\b|\/workspace\/|secret-sentinel|error\s+\d{3}\b/i;

const LOGIN_FAILURE = "El correo o la contraseña no coinciden con una cuenta activa.";

export function isReadableMessage(candidate: string | undefined): boolean {
  const text = candidate?.trim() ?? "";
  if (!text || text.length > 400) return false;
  if (/^\d{3}$/.test(text)) return false;
  if (LEAK.test(text)) return false;
  return true;
}

/** Prefer a safe sentence from the API. Replace traces, status codes, and parse errors. */
export function humanMessage(status: number, candidate?: string): string {
  if (status === 409) return HTTP_CATALOG[409];
  if (status === 0) return HTTP_CATALOG[0];
  if (status >= 500) return HTTP_CATALOG[500];
  if (candidate && isReadableMessage(candidate)) return candidate.trim();
  if (status === 401) return LOGIN_FAILURE;
  return HTTP_CATALOG[status] ?? "No se pudo completar la solicitud.";
}

export function fieldMessage(candidate: string): string {
  const text = candidate.replace(/^Value error,\s*/, "").trim();
  if (!isReadableMessage(text)) return "Revisa este campo.";
  return text;
}
