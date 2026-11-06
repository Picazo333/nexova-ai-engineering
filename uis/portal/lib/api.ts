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

export function apiBase(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (raw) return raw.replace(/\/$/, "");
  return "http://127.0.0.1:8000";
}

let leaving = false;

export function leaveForLogin(): void {
  if (leaving || typeof window === "undefined") return;
  leaving = true;
  clearToken();
  const next = `${window.location.pathname}${window.location.search}`;
  const params = new URLSearchParams({ reason: "expired", next });
  window.location.assign(`/login?${params.toString()}`);
}

function fieldErrors(body: unknown): Record<string, string> {
  if (!body || typeof body !== "object") return {};
  const detail = (body as { detail?: unknown }).detail;
  if (!Array.isArray(detail)) return {};
  const fields: Record<string, string> = {};
  for (const item of detail) {
    if (!item || typeof item !== "object") continue;
    const loc = (item as { loc?: unknown }).loc;
    const raw = (item as { msg?: unknown }).msg;
    if (!Array.isArray(loc) || typeof raw !== "string") continue;
    const name = [...loc].reverse().find((part) => part !== "body" && typeof part === "string");
    if (typeof name !== "string") continue;
    fields[name] = raw.replace(/^Value error,\s*/, "");
  }
  return fields;
}

function messageFrom(body: unknown, status: number): string {
  if (status === 409) return "Ya existe una cuenta con ese correo.";
  if (body && typeof body === "object") {
    const record = body as { message?: unknown; detail?: unknown };
    if (typeof record.message === "string" && record.message) return record.message;
    if (typeof record.detail === "string" && record.detail) return record.detail;
  }
  if (status === 401) return "El correo o la contraseña no coinciden con una cuenta activa.";
  return "No se pudo completar la solicitud.";
}

type Options = { auth?: boolean };

export async function apiFetch<T>(path: string, init: RequestInit = {}, options?: Options): Promise<T> {
  const auth = options?.auth !== false;
  const headers = new Headers(init.headers);
  if (!headers.has("Accept")) headers.set("Accept", "application/json");
  if (auth) {
    const token = readToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  let response: Response;
  try {
    response = await fetch(`${apiBase()}${path}`, { ...init, headers, cache: "no-store" });
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
    leaveForLogin();
    return new Promise<T>(() => {});
  }
  if (!response.ok) {
    const fields = fieldErrors(body);
    if (response.status === 409) fields.email = "Ya existe una cuenta con ese correo.";
    throw new ApiError(response.status, messageFrom(body, response.status), fields);
  }
  return body as T;
}

export async function apiDownload(path: string): Promise<Blob> {
  const headers = new Headers({ Accept: "text/csv" });
  const token = readToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let response: Response;
  try {
    response = await fetch(`${apiBase()}${path}`, { headers, cache: "no-store" });
  } catch {
    throw new ApiError(0, "No hay conexión con la API. Los datos escritos se conservan.");
  }
  if (response.status === 401) {
    leaveForLogin();
    return new Promise<Blob>(() => {});
  }
  if (!response.ok) {
    const text = await response.text();
    let body: unknown = null;
    try {
      body = JSON.parse(text) as unknown;
    } catch {
      body = null;
    }
    throw new ApiError(response.status, messageFrom(body, response.status));
  }
  return response.blob();
}
