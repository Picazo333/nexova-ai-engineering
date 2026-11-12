/**
 * Instrumentation points. Each function calls track() and does not send HTTP.
 * Property keys stay inside the allowlist of event-schemas.json.
 */

import { LOW_STOCK_BELOW } from "@/lib/stock";
import {
  admit,
  canonicalPath,
  currentSessionId,
  rememberTelemetryUser,
  track,
} from "@/lib/telemetry";

export const CATEGORY_MAP_VERSION = "proposed-2026-11-12";
const THRESHOLD_RATIO = 0.1;
const ISO_TIME = /^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$/;
const SKU_OR_ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/;
const EMPLOYEE = /^NXV-EMP-[0-9]+$/;
const LAST_FIELDS = new Set([
  "asset_id",
  "quantity",
  "supplier",
  "office",
  "exit_type",
  "email",
  "password",
  "current_password",
  "new_password",
  "confirmation",
]);

const MAPPED_LIVES = ["hardware", "peripherals", "training_materials"] as const;

function mappedLive(value: string): (typeof MAPPED_LIVES)[number] | null {
  return (MAPPED_LIVES as readonly string[]).includes(value) ? (value as (typeof MAPPED_LIVES)[number]) : null;
}

const PRODUCT_CATEGORY: Record<string, "training_kit" | "onboarding_equipment"> = {
  hardware: "onboarding_equipment",
  peripherals: "onboarding_equipment",
  training_materials: "training_kit",
};

export type LiveCategory = "hardware" | "peripherals" | "office_supplies" | "training_materials";

export type MaterialFact = {
  liveCategory: string;
  productId: string;
  productSku: string;
  office: string;
  quantity: number;
  orderId?: number;
  supplier?: string | null;
  occurredAt?: string | null;
  exitType?: string | null;
  assignedTo?: string | null;
  previousStock?: number;
  currentStock?: number;
};

type OfficeCurrency = { office: "valencia" | "miami"; currency: "EUR" | "USD" };

export function officeCurrency(office: string): OfficeCurrency | null {
  if (office === "Valencia" || office === "valencia") return { office: "valencia", currency: "EUR" };
  if (office === "Miami" || office === "miami") return { office: "miami", currency: "USD" };
  return null;
}

function safeId(value: string): boolean {
  return SKU_OR_ID.test(value);
}

function gapFor(affected: string, fact: MaterialFact, place: OfficeCurrency, live: LiveCategory | null): void {
  const properties: Record<string, unknown> = {
    gap: "missing_programme",
    affected_event: affected,
    product_id: fact.productId,
    product_sku: fact.productSku,
    office: place.office,
  };
  if (live) properties.live_category = live;
  track("catalogue_gap_recorded", properties);
}

function materialBase(fact: MaterialFact, place: OfficeCurrency, category: string): Record<string, unknown> | null {
  if (!safeId(fact.productId) || !safeId(fact.productSku)) return null;
  if (!Number.isInteger(fact.quantity) || fact.quantity < 1) return null;
  return {
    office: place.office,
    product_id: fact.productId,
    product_category: category,
    programme_id: "unassigned",
    quantity: fact.quantity,
    currency: place.currency,
    product_sku: fact.productSku,
    category_map_version: CATEGORY_MAP_VERSION,
  };
}

export function trackMaterialEvent(eventType: string, fact: MaterialFact): void {
  const place = officeCurrency(fact.office);
  if (!place) return;
  if (fact.liveCategory === "office_supplies") return;
  const category = PRODUCT_CATEGORY[fact.liveCategory];
  const live = mappedLive(fact.liveCategory);
  if (!category) {
    if (safeId(fact.productId) && safeId(fact.productSku)) {
      const properties: Record<string, unknown> = {
        gap: "unmapped_category",
        affected_event: eventType,
        product_id: fact.productId,
        product_sku: fact.productSku,
        office: place.office,
      };
      if (
        fact.liveCategory === "hardware" ||
        fact.liveCategory === "peripherals" ||
        fact.liveCategory === "office_supplies" ||
        fact.liveCategory === "training_materials"
      ) {
        properties.live_category = fact.liveCategory;
      }
      track("catalogue_gap_recorded", properties);
    }
    return;
  }
  const base = materialBase(fact, place, category);
  if (!base) return;
  if (eventType === "inbound_order_created" || eventType === "outbound_order_created") {
    if (fact.orderId == null || !Number.isInteger(fact.orderId) || fact.orderId < 1) return;
    base.order_id = fact.orderId;
  }
  if (eventType === "inbound_order_created") {
    const supplier = fact.supplier?.trim() ?? "";
    if (supplier && !supplier.includes("@") && !/[\r\n]/.test(supplier)) base.supplier = supplier;
    if (fact.occurredAt && ISO_TIME.test(fact.occurredAt)) base.occurred_at = fact.occurredAt;
  }
  if (eventType === "outbound_order_created") {
    if (fact.exitType !== "allocation" && fact.exitType !== "consumption") return;
    base.exit_type = fact.exitType;
    const assignee = fact.assignedTo?.trim() ?? "";
    if (EMPLOYEE.test(assignee)) base.assignee_ref = assignee;
    else if (assignee) base.assignee_redacted = true;
    if (fact.occurredAt && ISO_TIME.test(fact.occurredAt)) base.occurred_at = fact.occurredAt;
  }
  if (eventType === "stock_threshold_triggered") {
    if (fact.previousStock == null || fact.currentStock == null) return;
    if (fact.previousStock < LOW_STOCK_BELOW || fact.currentStock >= LOW_STOCK_BELOW) return;
    if (fact.currentStock < 0) return;
    base.current_stock = fact.currentStock;
    base.previous_stock = fact.previousStock;
    base.threshold = LOW_STOCK_BELOW;
    base.direction = "fell_below";
    base.order_type = "outbound";
    if (fact.orderId != null && Number.isInteger(fact.orderId) && fact.orderId >= 1) base.order_id = fact.orderId;
  }
  track(eventType, base);
  gapFor(eventType, fact, place, live);
}

export function trackKitCostVariance(input: {
  fact: MaterialFact;
  unitCostMinor: number;
  historicalUnitCostMinor: number;
  varianceRatio: number;
}): void {
  if (input.varianceRatio <= THRESHOLD_RATIO) return;
  if (!Number.isInteger(input.unitCostMinor) || input.unitCostMinor < 0) return;
  if (!Number.isInteger(input.historicalUnitCostMinor) || input.historicalUnitCostMinor < 1) return;
  const place = officeCurrency(input.fact.office);
  const category = PRODUCT_CATEGORY[input.fact.liveCategory];
  if (!place || !category) return;
  const supplier = input.fact.supplier?.trim() ?? "";
  if (!supplier || supplier.includes("@") || /[\r\n]/.test(supplier)) return;
  if (input.fact.orderId == null || input.fact.orderId < 1) return;
  const properties: Record<string, unknown> = {
    office: place.office,
    product_id: input.fact.productId,
    product_category: category,
    programme_id: "unassigned",
    quantity: input.fact.quantity,
    currency: place.currency,
    order_id: input.fact.orderId,
    product_sku: input.fact.productSku,
    supplier,
    unit_cost_minor: input.unitCostMinor,
    historical_unit_cost_minor: input.historicalUnitCostMinor,
    variance_ratio: input.varianceRatio,
    threshold_ratio: THRESHOLD_RATIO,
    category_map_version: CATEGORY_MAP_VERSION,
  };
  if (input.fact.occurredAt && ISO_TIME.test(input.fact.occurredAt)) properties.occurred_at = input.fact.occurredAt;
  track("kit_cost_variance_detected", properties);
  const live = mappedLive(input.fact.liveCategory);
  gapFor("kit_cost_variance_detected", input.fact, place, live);
}

export function trackLoginFailed(): void {
  track("login_failed", { failure_code: "invalid_credentials" });
}

export function trackLoginSucceeded(expiresInSeconds: number): void {
  if (!Number.isInteger(expiresInSeconds) || expiresInSeconds < 1 || expiresInSeconds > 86400) return;
  track("login_succeeded", { expires_in_seconds: expiresInSeconds });
}

export function trackOrderValidation(input: {
  status: number;
  route: string;
  fields: Record<string, string>;
  productId?: string;
  productSku?: string;
  office?: string;
  quantity?: number;
  exitType?: string;
}): void {
  let failure: string | null = null;
  if (input.status === 400) failure = "insufficient_stock";
  else if (input.status === 404) failure = "unknown_asset";
  else if (input.status === 422) {
    if (input.fields.current_stock) return;
    if (input.fields.user_uuid) failure = "forbidden_user_uuid";
    else if (input.fields.assigned_to) failure = "assigned_to_rule";
    else if (input.fields.supplier) failure = "empty_supplier";
    else if (input.fields.office) failure = "bad_office";
    else if (input.fields.quantity) failure = "quantity_rule";
  }
  if (!failure) return;
  const route = input.route.split("?")[0];
  if (route !== "/inventory/orders/inbound" && route !== "/inventory/orders/outbound") return;
  const properties: Record<string, unknown> = {
    failure_code: failure,
    route_template: route,
    http_status: input.status,
  };
  if (input.productId && safeId(input.productId)) properties.product_id = input.productId;
  if (input.productSku && safeId(input.productSku)) properties.product_sku = input.productSku;
  const place = input.office ? officeCurrency(input.office) : null;
  if (place) properties.office = place.office;
  if (input.quantity != null && Number.isInteger(input.quantity)) properties.quantity = input.quantity;
  if (input.exitType === "allocation" || input.exitType === "consumption") properties.exit_type = input.exitType;
  track("order_validation_failed", properties);
}

type StockAttempt = {
  sku?: unknown;
  category?: unknown;
  office?: unknown;
  current_stock?: unknown;
  quantity?: unknown;
};

function integerOf(value: unknown): number | null {
  return typeof value === "number" && Number.isInteger(value) ? value : null;
}

export function trackDirectStockRejection(input: {
  status: number;
  path: string;
  body: unknown;
  fields: Record<string, string>;
}): void {
  const path = input.path.split("?")[0];
  if (!path.startsWith("/inventory")) return;
  let parsed: StockAttempt | null = null;
  if (typeof input.body === "string" && input.body) {
    try {
      const value = JSON.parse(input.body) as unknown;
      if (value && typeof value === "object") parsed = value as StockAttempt;
    } catch {
      parsed = null;
    }
  }
  const stock = integerOf(parsed?.current_stock);
  const quantity = integerOf(parsed?.quantity);
  const attempted = input.status === 422 ? stock : stock ?? quantity;
  if (input.status === 422 && (stock == null || !input.fields.current_stock && stock == null)) return;
  if (input.status === 422 && stock == null) return;
  if (input.status === 405 && attempted == null) return;
  if (input.status !== 422 && input.status !== 405) return;
  const sku = typeof parsed?.sku === "string" ? parsed.sku : "";
  const category = typeof parsed?.category === "string" ? parsed.category : "";
  const place = officeCurrency(typeof parsed?.office === "string" ? parsed.office : "");
  const productCategory = PRODUCT_CATEGORY[category];
  if (!place || !productCategory || !safeId(sku) || attempted == null) return;
  if (attempted < -1_000_000 || attempted > 1_000_000) return;
  track("direct_stock_edit_rejected", {
    office: place.office,
    product_id: sku,
    product_category: productCategory,
    programme_id: "unassigned",
    quantity: attempted,
    currency: place.currency,
    product_sku: sku,
    http_status: input.status,
    rejected_field: input.status === 405 ? "method" : "current_stock",
    route_template: path.replace(/\/\d+(?=\/|$)/g, "/{id}"),
    category_map_version: CATEGORY_MAP_VERSION,
  });
  track("catalogue_gap_recorded", {
    gap: "missing_programme",
    affected_event: "direct_stock_edit_rejected",
    product_id: sku,
    product_sku: sku,
    office: place.office,
    live_category: category,
  });
}

const openFlows = new Set<string>();

export function armFlow(flow: string): void {
  openFlows.add(`${currentSessionId()}:${flow}`);
}

export function cancelFlow(flow: string): void {
  openFlows.delete(`${currentSessionId()}:${flow}`);
}

export function abandonFlow(flow: string, elapsedMs: number, lastField?: string): void {
  const key = `${currentSessionId()}:${flow}`;
  if (!openFlows.has(key)) return;
  openFlows.delete(key);
  const elapsed = Math.max(0, Math.min(86_400_000, Math.round(elapsedMs)));
  const properties: Record<string, unknown> = { app: "backoffice", flow, elapsed_ms: elapsed };
  if (lastField && LAST_FIELDS.has(lastField)) properties.last_field = lastField;
  track("flow_abandoned", properties);
}

function routeTemplate(path: string): string {
  return path.split("?")[0].replace(/\/\d+(?=\/|$)/g, "/{id}");
}

export function observeHttp(input: {
  method: string;
  path: string;
  status: number;
  durationMs: number;
  cache: "" | "HIT" | "MISS";
  body: BodyInit | null | undefined;
  hadToken: boolean;
  missingToken: boolean;
  tokenExpPassed: boolean;
  tokenSub: string | null;
  fields: Record<string, string>;
}): void {
  const path = input.path.split("?")[0];
  if (path.startsWith("/telemetry")) return;
  const method = input.method.toUpperCase();
  const allowed = method === "GET" || method === "POST" || method === "PUT" || method === "PATCH" || method === "DELETE";
  if (input.missingToken) {
    const admission = admit("missing_token", 60, Date.now(), 60_000);
    if (admission.send) {
      const properties: Record<string, unknown> = { failure_code: "missing_token", surface: "backoffice" };
      if (admission.droppedCount) properties.dropped_count = admission.droppedCount;
      track("credential_rejected", properties);
    }
  }
  if (input.hadToken && input.status === 401 && input.tokenExpPassed && input.tokenSub) {
    rememberTelemetryUser(input.tokenSub);
    track("session_expired", { surface: "backoffice", reason: "exp_claim" });
  }
  if (input.status === 0 || (input.status >= 500 && input.status <= 504)) {
    if (allowed) {
      const properties: Record<string, unknown> = {
        app: "backoffice",
        http_method: method,
        route_template: routeTemplate(path),
        status_code: input.status,
      };
      if (Number.isFinite(input.durationMs) && input.durationMs >= 0) properties.duration_ms = input.durationMs;
      track("api_response_failed", properties);
    }
  }
  const slow = input.durationMs >= 1000 || input.status >= 500;
  if (slow && allowed && input.status >= 100 && input.status <= 599) {
    const template = routeTemplate(path);
    const admission = admit(`latency:${template}`, 30, Date.now(), 60_000);
    if (admission.send) {
      const properties: Record<string, unknown> = {
        http_method: method,
        route_template: template,
        status_code: input.status,
        duration_ms: Math.min(600_000, input.durationMs),
        cache_mark: input.cache || "none",
      };
      if (admission.droppedCount) properties.dropped_count = admission.droppedCount;
      track("api_latency_recorded", properties);
    }
  }
  if ((input.status === 422 || input.status === 405) && path.startsWith("/inventory")) {
    trackDirectStockRejection({
      status: input.status,
      path,
      body: typeof input.body === "string" ? input.body : undefined,
      fields: input.fields,
    });
  }
}

export function resetFlowsForTests(): void {
  openFlows.clear();
}
