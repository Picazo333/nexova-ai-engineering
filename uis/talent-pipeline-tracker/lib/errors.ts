export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function isAbortError(error: unknown): boolean {
  return (
    (error instanceof DOMException && error.name === "AbortError") ||
    (error instanceof Error && error.name === "AbortError")
  );
}

export function toErrorMessage(error: unknown): string {
  if (isAbortError(error)) return "La petición se canceló.";
  if (error instanceof ApiError) {
    if (error.status === 404) return "No existe una candidatura con ese identificador.";
    return `El tracker respondió ${error.status}: ${error.message}`;
  }
  if (error instanceof TypeError) {
    return "No hay conexión con el tracker. Revisa la red e inténtalo de nuevo.";
  }
  if (error instanceof Error && error.message) return error.message;
  return "No se pudo completar la operación.";
}
