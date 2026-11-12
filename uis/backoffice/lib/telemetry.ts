/**
 * TelemetryService. The backoffice calls track() and nothing else sends events.
 * The envelope is filled here. Callers pass event_type and properties only.
 */

import { readToken } from "@/lib/session";

export const SCHEMA_VERSION = "1.0.0";
export const SESSION_KEY = "nexova.telemetry.session";
export const USER_KEY = "nexova.telemetry.user";

const FLUSH_MS = 10_000;
const BATCH_SIZE = 20;
const MAX_ATTEMPTS = 3;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

const ANONYMOUS_EVENTS = new Set(["login_failed", "password_reset_requested"]);
const FORBIDDEN_KEYS = new Set([
  "email",
  "password",
  "name",
  "access_token",
  "token",
  "authorization",
  "assigned_to",
  "message",
  "detail",
]);
const EMAIL_RE = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/;

export type TelemetryEvent = {
  eventId: string;
  timestamp: string;
  sessionId: string;
  userId: string;
  event_type: string;
  schemaVersion: string;
  requestId: string;
  properties: Record<string, unknown>;
};

export type TelemetryPhase = "empty" | "ready" | "loading" | "error";

export type TelemetrySnapshot = {
  queued: number;
  sent: number;
  phase: TelemetryPhase;
  error: string;
};

type Bucket = { windowStart: number; sent: number; dropped: number };

const queue: TelemetryEvent[] = [];
const listeners = new Set<() => void>();
const buckets = new Map<string, Bucket>();
const correlation: string[] = [];

let timer: ReturnType<typeof setTimeout> | null = null;
let working = false;
let sent = 0;
let lastError = "";
let installed = false;
let pageLoadRecorded = false;
let snapshot: TelemetrySnapshot = { queued: 0, sent: 0, phase: "empty", error: "" };

function storage(): Storage | null {
  try {
    if (typeof sessionStorage === "undefined") return null;
    return sessionStorage;
  } catch {
    return null;
  }
}

function readStorage(key: string): string {
  const value = storage()?.getItem(key) ?? "";
  return UUID_RE.test(value) ? value.toLowerCase() : "";
}

function writeStorage(key: string, value: string): void {
  try {
    storage()?.setItem(key, value);
  } catch {
    /* A blocked sessionStorage leaves sessionId as missing. The panel still works. */
  }
}

function removeStorage(key: string): void {
  try {
    storage()?.removeItem(key);
  } catch {
    /* The next event falls back to anonymous or missing. */
  }
}

export function uuid(): string {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  const bytes = new Uint8Array(16);
  globalThis.crypto.getRandomValues(bytes);
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = [...bytes].map((byte) => byte.toString(16).padStart(2, "0")).join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

export function endpointUrl(): string {
  const raw = process.env.NEXT_PUBLIC_TELEMETRY_ENDPOINT;
  return typeof raw === "string" ? raw.trim() : "";
}

export function currentSessionId(): string {
  return readStorage(SESSION_KEY) || "missing";
}

export function currentUserId(): string {
  return readStorage(USER_KEY) || "anonymous";
}

export function beginTelemetrySession(userId: string): void {
  if (UUID_RE.test(userId)) writeStorage(USER_KEY, userId.toLowerCase());
  else removeStorage(USER_KEY);
  writeStorage(SESSION_KEY, uuid());
}

export function rememberTelemetryUser(userId: string): void {
  if (UUID_RE.test(userId)) writeStorage(USER_KEY, userId.toLowerCase());
}

export function restoreIdentity(token: string): void {
  const claims = readJwtClaims(token);
  if (claims?.sub) rememberTelemetryUser(claims.sub);
  if (!readStorage(SESSION_KEY)) writeStorage(SESSION_KEY, uuid());
}

export function readJwtClaims(token: string): { sub: string; exp: number } | null {
  const part = token.split(".")[1];
  if (!part) return null;
  try {
    const padded = part.replace(/-/g, "+").replace(/_/g, "/");
    const json = JSON.parse(atob(padded)) as { sub?: unknown; exp?: unknown };
    if (typeof json.sub !== "string" || typeof json.exp !== "number") return null;
    if (!UUID_RE.test(json.sub)) return null;
    return { sub: json.sub.toLowerCase(), exp: json.exp };
  } catch {
    return null;
  }
}

export function openCorrelation(): { id: string; close: () => void } {
  const id = uuid();
  correlation.push(id);
  let closed = false;
  return {
    id,
    close() {
      if (closed) return;
      closed = true;
      const index = correlation.lastIndexOf(id);
      if (index >= 0) correlation.splice(index, 1);
    },
  };
}

function userFor(eventType: string, properties: Record<string, unknown>): string {
  if (ANONYMOUS_EVENTS.has(eventType)) return "anonymous";
  if (eventType === "credential_rejected") {
    const code = properties.failure_code;
    if (code === "missing_token" || code === "bad_signature") return "anonymous";
  }
  return currentUserId();
}

function propertiesAreSafe(properties: Record<string, unknown>): boolean {
  for (const [key, value] of Object.entries(properties)) {
    if (FORBIDDEN_KEYS.has(key)) return false;
    if (typeof value === "string" && EMAIL_RE.test(value)) return false;
  }
  return true;
}

function seal(eventType: string, properties: Record<string, unknown>): TelemetryEvent | null {
  if (!propertiesAreSafe(properties)) return null;
  const requestId = correlation[correlation.length - 1] ?? uuid();
  return {
    eventId: uuid(),
    timestamp: new Date().toISOString(),
    sessionId: currentSessionId(),
    userId: userFor(eventType, properties),
    event_type: eventType,
    schemaVersion: SCHEMA_VERSION,
    requestId,
    properties,
  };
}

function publish(): void {
  const phase: TelemetryPhase = working
    ? "loading"
    : lastError
      ? "error"
      : queue.length === 0 && sent === 0
        ? "empty"
        : "ready";
  const next = { queued: queue.length, sent, phase, error: lastError };
  if (
    snapshot.queued === next.queued &&
    snapshot.sent === next.sent &&
    snapshot.phase === next.phase &&
    snapshot.error === next.error
  ) {
    return;
  }
  snapshot = next;
  listeners.forEach((listener) => listener());
}

export function getTelemetrySnapshot(): TelemetrySnapshot {
  return snapshot;
}

export function subscribeTelemetry(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function pendingEvents(): TelemetryEvent[] {
  return queue.map((event) => ({ ...event, properties: { ...event.properties } }));
}

function clearTimer(): void {
  if (timer) clearTimeout(timer);
  timer = null;
}

function schedule(): void {
  if (timer || working || queue.length === 0) return;
  timer = setTimeout(() => {
    timer = null;
    void flush("timer");
  }, FLUSH_MS);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

async function deliver(batch: TelemetryEvent[]): Promise<boolean> {
  const endpoint = endpointUrl();
  if (!endpoint) {
    lastError = "Falta NEXT_PUBLIC_TELEMETRY_ENDPOINT. El lote se descartó.";
    return false;
  }
  let delay = 200;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ events: batch }),
        keepalive: true,
      });
      if (response.ok) {
        lastError = "";
        return true;
      }
      if (response.status >= 400 && response.status < 500) {
        lastError = "El lote fue rechazado y se descartó.";
        return false;
      }
    } catch {
      /* The next attempt waits. Telemetry does not block the panel. */
    }
    if (attempt < MAX_ATTEMPTS) {
      await sleep(delay);
      delay *= 2;
    }
  }
  lastError = "El lote no llegó tras 3 intentos y se descartó.";
  return false;
}

export async function flushTelemetry(): Promise<void> {
  return flush("manual");
}

async function flush(_reason: "timer" | "size" | "manual"): Promise<void> {
  if (working || queue.length === 0) return;
  working = true;
  const batch = queue.splice(0, queue.length);
  clearTimer();
  publish();
  const ok = await deliver(batch);
  if (ok) sent += batch.length;
  working = false;
  publish();
  if (queue.length >= BATCH_SIZE) void flush("size");
  else if (queue.length > 0) schedule();
}

export function track(eventType: string, properties: Record<string, unknown>): void {
  const event = seal(eventType, properties);
  if (!event) return;
  queue.push(event);
  publish();
  if (queue.length >= BATCH_SIZE) void flush("size");
  else schedule();
}

function onHidden(): void {
  if (document.visibilityState !== "hidden" || queue.length === 0) return;
  const endpoint = endpointUrl();
  const batch = queue.splice(0, queue.length);
  clearTimer();
  if (!endpoint || typeof navigator === "undefined" || typeof navigator.sendBeacon !== "function") {
    queue.unshift(...batch);
    lastError = endpoint ? "Este navegador no pudo usar sendBeacon." : "Falta NEXT_PUBLIC_TELEMETRY_ENDPOINT.";
    schedule();
    publish();
    return;
  }
  const blob = new Blob([JSON.stringify({ events: batch })], { type: "text/plain;charset=UTF-8" });
  const ok = navigator.sendBeacon(endpoint, blob);
  if (!ok) {
    queue.unshift(...batch);
    schedule();
  } else {
    sent += batch.length;
    lastError = "";
  }
  publish();
}

export function installTelemetryRuntime(): void {
  if (installed || typeof window === "undefined") return;
  installed = true;
  const token = readToken();
  if (token) restoreIdentity(token);
  document.addEventListener("visibilitychange", onHidden);
  window.addEventListener("error", onWindowError);
  window.addEventListener("unhandledrejection", onRejection);
  recordPageLoad();
}

function onWindowError(event: ErrorEvent): void {
  const error = event.error instanceof Error ? event.error : new Error(event.message || "Error");
  void recordException(error);
}

function onRejection(event: PromiseRejectionEvent): void {
  const reason: unknown = event.reason;
  const error = reason instanceof Error ? reason : new Error("Unhandled rejection");
  if (!(reason instanceof Error)) error.name = "UnhandledRejection";
  void recordException(error);
}

export function sanitizedExceptionText(name: string, message: string): string {
  const cleaned = message
    .replace(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g, "[email]")
    .replace(/\d{3,}/g, "[n]")
    .slice(0, 300);
  return `${name}\n${cleaned}`;
}

export async function messageSha256(name: string, message: string): Promise<string> {
  const encoded = new TextEncoder().encode(sanitizedExceptionText(name, message));
  const digest = await crypto.subtle.digest("SHA-256", encoded);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

const recentExceptions = new Map<string, number>();

export async function recordException(error: Error): Promise<void> {
  const name = /^[A-Za-z][A-Za-z0-9_]{0,79}$/.test(error.name) ? error.name : "Error";
  const digest = await messageSha256(name, error.message || "");
  const now = Date.now();
  const seen = recentExceptions.get(digest);
  if (seen != null && now - seen < 2000) return;
  recentExceptions.set(digest, now);
  if (typeof window === "undefined") return;
  const path = canonicalPath(window.location.pathname);
  if (!path) return;
  const admission = admit(`exception:${currentSessionId()}`, 5, now, 60_000);
  if (!admission.send) return;
  const properties: Record<string, unknown> = {
    app: "backoffice",
    path_template: path,
    error_name: name,
    message_sha256: digest,
  };
  if (admission.droppedCount) properties.dropped_count = admission.droppedCount;
  track("frontend_exception_recorded", properties);
}

const PAGE_PATHS = new Set([
  "/",
  "/login",
  "/backoffice/inventory/products",
  "/backoffice/inventory/orders",
  "/backoffice/inventory/orders/inbound",
  "/backoffice/inventory/orders/outbound",
]);

export function canonicalPath(pathname: string): string | null {
  if (pathname === "/backoffice/inventory") return "/backoffice/inventory/products";
  return PAGE_PATHS.has(pathname) ? pathname : null;
}

const SECTIONS: Record<string, string> = {
  "/": "backoffice_home",
  "/login": "backoffice_login",
  "/backoffice/inventory/products": "backoffice_inventory_products",
  "/backoffice/inventory/orders/inbound": "backoffice_inventory_inbound",
  "/backoffice/inventory/orders/outbound": "backoffice_inventory_outbound",
  "/backoffice/inventory/orders": "backoffice_inventory_orders",
};

const sectionSeen = new Map<string, number>();

export function trackSection(pathname: string): void {
  const path = canonicalPath(pathname);
  if (!path) return;
  const section = SECTIONS[path];
  if (!section) return;
  const key = `${currentSessionId()}:${section}`;
  const now = Date.now();
  const previous = sectionSeen.get(key);
  if (previous != null && now - previous < 30_000) return;
  sectionSeen.set(key, now);
  track("section_viewed", { app: "backoffice", section });
}

function recordPageLoad(): void {
  const emit = () => {
    if (pageLoadRecorded || typeof performance === "undefined") return;
    const nav = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
    if (!nav || nav.loadEventEnd <= 0) return;
    const path = canonicalPath(window.location.pathname);
    if (!path) return;
    const navType = nav.type === "reload" || nav.type === "back_forward" || nav.type === "navigate" ? nav.type : null;
    if (!navType) return;
    const duration = nav.loadEventEnd - nav.startTime;
    if (!Number.isFinite(duration) || duration < 0 || duration > 600_000) return;
    pageLoadRecorded = true;
    track("page_load_recorded", {
      app: "backoffice",
      path_template: path,
      duration_ms: duration,
      nav_type: navType,
    });
  };
  if (document.readyState === "complete") emit();
  else window.addEventListener("load", emit, { once: true });
}

export function admit(
  key: string,
  limit: number,
  now: number,
  windowMs: number,
): { send: boolean; droppedCount?: number } {
  const current = buckets.get(key);
  if (!current || now - current.windowStart >= windowMs) {
    const carry = current?.dropped ?? 0;
    buckets.set(key, { windowStart: now, sent: 1, dropped: 0 });
    return { send: true, droppedCount: carry > 0 ? carry : undefined };
  }
  if (current.sent < limit) {
    current.sent += 1;
    return { send: true };
  }
  current.dropped += 1;
  return { send: false };
}

export function resetTelemetryForTests(): void {
  queue.splice(0, queue.length);
  clearTimer();
  working = false;
  sent = 0;
  lastError = "";
  buckets.clear();
  correlation.splice(0, correlation.length);
  sectionSeen.clear();
  recentExceptions.clear();
  pageLoadRecorded = false;
  installed = false;
  snapshot = { queued: 0, sent: 0, phase: "empty", error: "" };
}
