import { readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";

import Ajv from "ajv";
import addFormats from "ajv-formats";

import {
  messageSha256,
  pendingEvents,
  resetTelemetryForTests,
  sanitizedExceptionText,
  track,
} from "@/lib/telemetry";
import {
  resetFlowsForTests,
  trackDirectStockRejection,
  trackKitCostVariance,
  trackLoginFailed,
  trackMaterialEvent,
  trackOrderValidation,
} from "@/lib/telemetry-catalog";

const memory = new Map<string, string>();

const sessionStorageMock = {
  getItem: (key: string) => memory.get(key) ?? null,
  setItem: (key: string, value: string) => {
    memory.set(key, value);
  },
  removeItem: (key: string) => {
    memory.delete(key);
  },
};

Object.defineProperty(global, "sessionStorage", { value: sessionStorageMock, configurable: true });

process.env.NEXT_PUBLIC_TELEMETRY_ENDPOINT = "http://127.0.0.1:8000/telemetry/events";

const schema = JSON.parse(
  readFileSync(path.resolve(__dirname, "../../../docs/telemetry/event-schemas.json"), "utf8"),
) as object;
const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);
const validate = ajv.compile(schema);

function expectValid(eventType: string): void {
  const event = pendingEvents().find((item) => item.event_type === eventType);
  expect(event).toBeDefined();
  const ok = validate(event);
  if (!ok) {
    throw new Error(`${eventType} ${ajv.errorsText(validate.errors, { separator: " | " })}`);
  }
}

describe("TelemetryService", () => {
  beforeEach(() => {
    memory.clear();
    resetTelemetryForTests();
    resetFlowsForTests();
    jest.useFakeTimers();
    global.fetch = jest.fn(async () => ({ ok: true, status: 200 })) as unknown as typeof fetch;
  });

  afterEach(() => {
    resetTelemetryForTests();
    jest.useRealTimers();
  });

  test("track rellena el sobre y no deja que el componente lo pase", () => {
    trackLoginFailed();
    const [event] = pendingEvents();
    expect(event.event_type).toBe("login_failed");
    expect(event.schemaVersion).toBe("1.0.0");
    expect(event.sessionId).toBe("missing");
    expect(event.userId).toBe("anonymous");
    expect(event.eventId).toMatch(/^[0-9a-f-]{36}$/);
    expect(event.timestamp.endsWith("Z")).toBe(true);
    expect(event.properties).toEqual({ failure_code: "invalid_credentials" });
    expect(Object.keys(event)).not.toContain("email");
    expectValid("login_failed");
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test("un lote de 20 sale en el momento y uno menor espera 10 segundos", async () => {
    for (let index = 0; index < 19; index += 1) trackLoginFailed();
    expect(global.fetch).not.toHaveBeenCalled();
    trackLoginFailed();
    await Promise.resolve();
    expect(global.fetch).toHaveBeenCalledTimes(1);
    const body = JSON.parse(String((global.fetch as jest.Mock).mock.calls[0][1].body)) as { events: unknown[] };
    expect(body.events).toHaveLength(20);
    (global.fetch as jest.Mock).mockClear();
    trackLoginFailed();
    await jest.advanceTimersByTimeAsync(9_999);
    expect(global.fetch).not.toHaveBeenCalled();
    await jest.advanceTimersByTimeAsync(1);
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  test("al ocultar la pestaña el lote sale con sendBeacon", () => {
    const beacon = jest.fn(() => true);
    const listeners = new Map<string, () => void>();
    Object.defineProperty(global, "navigator", { value: { sendBeacon: beacon }, configurable: true });
    Object.defineProperty(global, "document", {
      value: {
        visibilityState: "visible",
        readyState: "complete",
        addEventListener: (name: string, fn: () => void) => listeners.set(name, fn),
      },
      configurable: true,
    });
    Object.defineProperty(global, "window", {
      value: {
        addEventListener: jest.fn(),
        location: { pathname: "/login" },
      },
      configurable: true,
    });
    Object.defineProperty(global, "performance", {
      value: { getEntriesByType: () => [] },
      configurable: true,
    });
    const { installTelemetryRuntime } = require("@/lib/telemetry") as typeof import("@/lib/telemetry");
    installTelemetryRuntime();
    track("section_viewed", { app: "backoffice", section: "backoffice_login" });
    document.visibilityState = "hidden";
    listeners.get("visibilitychange")?.();
    expect(beacon).toHaveBeenCalledTimes(1);
    const [url, blob] = beacon.mock.calls[0] as [string, Blob];
    expect(url).toBe("http://127.0.0.1:8000/telemetry/events");
    expect(blob.type).toContain("text/plain");
    expect(pendingEvents()).toHaveLength(0);
  });

  test("reintenta con espera y descarta al tercer fallo de red", async () => {
    global.fetch = jest.fn(async () => {
      throw new Error("network");
    }) as unknown as typeof fetch;
    trackLoginFailed();
    await jest.advanceTimersByTimeAsync(10_000);
    await jest.advanceTimersByTimeAsync(200);
    await jest.advanceTimersByTimeAsync(400);
    expect(global.fetch).toHaveBeenCalledTimes(3);
    expect(pendingEvents()).toHaveLength(0);
  });

  test("no encola un evento con correo", () => {
    track("login_failed", { failure_code: "invalid_credentials", email: "person@example.com" });
    expect(pendingEvents()).toHaveLength(0);
  });

  test("los eventos de material y el rechazo de stock cumplen el esquema", () => {
    trackMaterialEvent("inbound_order_created", {
      liveCategory: "hardware",
      productId: "4",
      productSku: "NXV-IT-001",
      office: "Valencia",
      quantity: 2,
      orderId: 9,
      supplier: "TechDistrib Valencia S.L.",
      occurredAt: "2026-11-12T09:04:00Z",
    });
    trackMaterialEvent("outbound_order_created", {
      liveCategory: "training_materials",
      productId: "6",
      productSku: "NXV-TRN-001",
      office: "Valencia",
      quantity: 1,
      orderId: 10,
      exitType: "allocation",
      assignedTo: "NXV-EMP-1042",
      occurredAt: "2026-11-12T09:05:00Z",
    });
    trackMaterialEvent("stock_threshold_triggered", {
      liveCategory: "peripherals",
      productId: "3",
      productSku: "NXV-PER-001",
      office: "Miami",
      quantity: 5,
      orderId: 11,
      previousStock: 12,
      currentStock: 7,
    });
    trackMaterialEvent("inbound_order_created", {
      liveCategory: "office_supplies",
      productId: "5",
      productSku: "NXV-OFF-001",
      office: "Valencia",
      quantity: 1,
      orderId: 12,
      supplier: "Papel",
    });
    trackKitCostVariance({
      fact: {
        liveCategory: "hardware",
        productId: "4",
        productSku: "NXV-IT-001",
        office: "Valencia",
        quantity: 2,
        orderId: 13,
        supplier: "TechDistrib Valencia S.L.",
        occurredAt: "2026-11-12T09:06:00Z",
      },
      unitCostMinor: 13000,
      historicalUnitCostMinor: 10000,
      varianceRatio: 0.3,
    });
    trackDirectStockRejection({
      status: 422,
      path: "/inventory/products",
      body: JSON.stringify({
        name: "Con stock",
        sku: "NXV-PER-012",
        category: "peripherals",
        office: "Miami",
        current_stock: 40,
      }),
      fields: { current_stock: "extra" },
    });
    trackOrderValidation({
      status: 400,
      route: "/inventory/orders/outbound",
      fields: {},
      productId: "2",
      productSku: "NXV-IT-002",
      office: "Miami",
      quantity: 9,
      exitType: "consumption",
    });
    for (const eventType of [
      "inbound_order_created",
      "outbound_order_created",
      "stock_threshold_triggered",
      "kit_cost_variance_detected",
      "direct_stock_edit_rejected",
      "order_validation_failed",
      "catalogue_gap_recorded",
    ]) {
      expectValid(eventType);
    }
    expect(pendingEvents().some((event) => event.properties.product_sku === "NXV-OFF-001")).toBe(false);
    expect(pendingEvents().some((event) => JSON.stringify(event).includes("Con stock"))).toBe(false);
  });

  test("el hash de una excepción sigue el saneado del plan", async () => {
    expect(sanitizedExceptionText("TypeError", "Cannot read properties of undefined")).toBe(
      "TypeError\nCannot read properties of undefined",
    );
    expect(await messageSha256("TypeError", "Cannot read properties of undefined")).toBe(
      "b7b32534990c138f77d0b6a7d0d9d0d58ad07faca7c6d5ab1d69c54bcc459036",
    );
    expect(sanitizedExceptionText("Error", "cuenta persona@example.com pidió 12345")).toBe(
      "Error\ncuenta [email] pidió [n]",
    );
  });

  test("el envío de telemetría no está fuera del servicio", () => {
    const root = path.resolve(__dirname, "..");
    const offenders: string[] = [];
    function walk(dir: string): void {
      for (const entry of readdirSync(dir)) {
        if (entry === "node_modules" || entry === ".next" || entry === "__tests__") continue;
        const full = path.join(dir, entry);
        if (statSync(full).isDirectory()) {
          walk(full);
          continue;
        }
        if (!/\.(ts|tsx)$/.test(entry)) continue;
        const text = readFileSync(full, "utf8");
        if (text.includes("/telemetry/events") && !full.endsWith(`${path.sep}lib${path.sep}telemetry.ts`)) {
          offenders.push(full);
        }
        if (/\baxios\b/.test(text)) offenders.push(full);
      }
    }
    walk(root);
    expect(offenders).toEqual([]);
  });
});
