import { clearToken, readToken } from "@/lib/session";

export class ApiError extends Error {
  status: number;
  fields: Record<string, string>;

  constructor(status: number, message: string, fields: Record<string, string> = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.fields = fields;
  }
}

export function inventoryApiBase(): string {
  const raw = process.env.NEXT_PUBLIC_INVENTORY_API_URL?.trim();
  if (raw) return raw.replace(/\/$/, "");
  return "http://127.0.0.1:8000";
}

let leaving = false;

export function redirectToLogin(reason?: "expired"): void {
  if (typeof window === "undefined" || leaving) return;
  leaving = true;
  const next = `${window.location.pathname}${window.location.search}`;
  const params = new URLSearchParams({ next });
  if (reason) params.set("reason", reason);
  window.location.assign(`/login?${params.toString()}`);
}

function fieldText(raw: string): string {
  return raw.replace(/^Value error,\s*/i, "").trim();
}

export function errorFrom(status: number, body: unknown): ApiError {
  const fields: Record<string, string> = {};
  let message = "";
  if (body && typeof body === "object") {
    const record = body as { detail?: unknown; message?: unknown };
    if (typeof record.detail === "string" && record.detail.trim()) {
      message = record.detail.trim();
    } else if (typeof record.message === "string" && record.message.trim()) {
      message = record.message.trim();
    } else if (Array.isArray(record.detail)) {
      const parts: string[] = [];
      for (const item of record.detail) {
        if (!item || typeof item !== "object") continue;
        const loc = (item as { loc?: unknown }).loc;
        const raw = (item as { msg?: unknown }).msg;
        if (typeof raw !== "string" || !raw.trim()) continue;
        const text = fieldText(raw);
        parts.push(text);
        if (Array.isArray(loc)) {
          const name = [...loc].reverse().find((part) => part !== "body" && typeof part === "string");
          if (typeof name === "string" && !fields[name]) fields[name] = text;
        }
      }
      message = parts.join(" ");
    }
  }
  if (!message) {
    message =
      status === 0
        ? "No hay conexión con la API. Los datos escritos se conservan."
        : `La API respondió ${status} sin un mensaje legible.`;
  }
  return new ApiError(status, message, fields);
}

export function messageOf(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return "No se pudo completar la operación.";
}

export type CacheMark = "" | "HIT" | "MISS";

type Options = { auth?: boolean; onCache?: (mark: CacheMark) => void };

function cacheMarkOf(response: Response): CacheMark {
  const read = response.headers?.get?.bind(response.headers);
  if (!read) return "";
  const value = read("X-Nexova-Cache");
  if (value === "HIT" || value === "MISS") return value;
  return "";
}

export async function apiFetch<T>(path: string, init: RequestInit = {}, options?: Options): Promise<T> {
  const auth = options?.auth !== false;
  const headers = new Headers(init.headers);
  if (!headers.has("Accept")) headers.set("Accept", "application/json");
  if (init.body != null && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (auth) {
    const token = readToken();
    if (!token) {
      redirectToLogin();
      throw new ApiError(401, "Falta la sesión. Entra de nuevo para continuar.");
    }
    headers.set("Authorization", `Bearer ${token}`);
  }
  let response: Response;
  try {
    response = await fetch(`${inventoryApiBase()}${path}`, { ...init, headers, cache: "no-store" });
  } catch {
    throw new ApiError(0, "No hay conexión con la API. Los datos escritos se conservan.");
  }
  const text = await response.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text) as unknown;
    } catch {
      body = null;
    }
  }
  if (response.status === 401 && auth) {
    clearToken();
    redirectToLogin("expired");
    throw errorFrom(401, body);
  }
  if (!response.ok) {
    throw errorFrom(response.status, body);
  }
  options?.onCache?.(cacheMarkOf(response));
  return body as T;
}
