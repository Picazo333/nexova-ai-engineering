import { ApiError, apiFetch } from "@/lib/http";

/**
 * Único acceso del backoffice a `/inventory`.
 * Los componentes importan estas funciones y no llaman a fetch.
 * current_stock llega calculado: el cliente no lo envía.
 * user_uuid lo escribe la API con el id de TinyDB del JWT.
 */

export type Asset = {
  id: number;
  name: string;
  sku: string;
  category: string;
  office: string;
  current_stock: number;
};

export type OrderType = "inbound" | "outbound";
export type ExitType = "allocation" | "consumption";
export type Office = "Valencia" | "Miami";

export type InventoryOrder = {
  id: number;
  order_type: OrderType;
  asset_id: number;
  asset_name: string;
  asset_sku: string;
  asset_category: string;
  quantity: number;
  office: string;
  created_at: string;
  user_uuid: string;
  supplier: string | null;
  exit_type: string | null;
  assigned_to: string | null;
};

export type AssetEntryInput = {
  asset_id: number;
  quantity: number;
  supplier: string;
  office: Office;
};

export type AssetExitInput = {
  asset_id: number;
  quantity: number;
  exit_type: ExitType;
  assigned_to: string | null;
  office: Office;
};

function isAsset(value: unknown): value is Asset {
  if (!value || typeof value !== "object") return false;
  const row = value as Asset;
  return (
    typeof row.id === "number" &&
    typeof row.name === "string" &&
    typeof row.sku === "string" &&
    typeof row.category === "string" &&
    typeof row.office === "string" &&
    typeof row.current_stock === "number"
  );
}

function isOrder(value: unknown): value is InventoryOrder {
  if (!value || typeof value !== "object") return false;
  const row = value as InventoryOrder;
  return (
    typeof row.id === "number" &&
    (row.order_type === "inbound" || row.order_type === "outbound") &&
    typeof row.asset_name === "string" &&
    typeof row.quantity === "number" &&
    typeof row.created_at === "string" &&
    typeof row.user_uuid === "string"
  );
}

function asAssets(value: unknown): Asset[] {
  if (!Array.isArray(value) || !value.every(isAsset)) {
    throw new ApiError(500, "La API devolvió un listado de activos que no se puede leer.");
  }
  return value;
}

function asAsset(value: unknown): Asset {
  if (!isAsset(value)) throw new ApiError(500, "La API devolvió un activo que no se puede leer.");
  return value;
}

function asOrder(value: unknown): InventoryOrder {
  if (!isOrder(value)) throw new ApiError(500, "La API devolvió una orden que no se puede leer.");
  return value;
}

function asOrders(value: unknown): InventoryOrder[] {
  if (!Array.isArray(value) || !value.every(isOrder)) {
    throw new ApiError(500, "La API devolvió un historial que no se puede leer.");
  }
  return value;
}

function officeQuery(office?: string): string {
  if (office !== "Valencia" && office !== "Miami") return "";
  return `?office=${encodeURIComponent(office)}`;
}

export function listAssets(office?: string): Promise<Asset[]> {
  return apiFetch<unknown>(`/inventory/products${officeQuery(office)}`).then(asAssets);
}

export function getAsset(assetId: number): Promise<Asset> {
  return apiFetch<unknown>(`/inventory/products/${assetId}`).then(asAsset);
}

export function createAssetEntry(input: AssetEntryInput): Promise<InventoryOrder> {
  return apiFetch<unknown>("/inventory/orders/inbound", {
    method: "POST",
    body: JSON.stringify(input),
  }).then(asOrder);
}

export function createAssetExit(input: AssetExitInput): Promise<InventoryOrder> {
  const body = {
    asset_id: input.asset_id,
    quantity: input.quantity,
    exit_type: input.exit_type,
    assigned_to: input.exit_type === "allocation" ? input.assigned_to : null,
    office: input.office,
  };
  return apiFetch<unknown>("/inventory/orders/outbound", {
    method: "POST",
    body: JSON.stringify(body),
  }).then(asOrder);
}

export function listOrders(office?: string): Promise<InventoryOrder[]> {
  return apiFetch<unknown>(`/inventory/orders${officeQuery(office)}`).then(asOrders);
}
