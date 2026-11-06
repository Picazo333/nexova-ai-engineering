const INVENTORY_PAGES = new Set([
  "/backoffice/inventory",
  "/backoffice/inventory/products",
  "/backoffice/inventory/orders",
  "/backoffice/inventory/orders/inbound",
  "/backoffice/inventory/orders/outbound",
]);

export const INVENTORY_HOME = "/backoffice/inventory/products";

export function isProtectedInventoryPath(pathname: string): boolean {
  if (pathname.includes("..") || pathname.includes("\\")) return false;
  return pathname === "/backoffice/inventory" || pathname.startsWith("/backoffice/inventory/");
}

export function loginRedirect(pathname: string, search: string, token: string): string | null {
  if (token) return null;
  if (!isProtectedInventoryPath(pathname)) return null;
  const next = `${pathname}${search || ""}`;
  return `/login?next=${encodeURIComponent(next)}`;
}

export function safeNext(value: string | null): string {
  if (!value) return INVENTORY_HOME;
  let decoded = value;
  try {
    decoded = decodeURIComponent(value);
  } catch {
    return INVENTORY_HOME;
  }
  if (!decoded.startsWith("/") || decoded.startsWith("//") || decoded.includes("\\") || decoded.includes("://")) {
    return INVENTORY_HOME;
  }
  const queryAt = decoded.indexOf("?");
  const path = queryAt === -1 ? decoded : decoded.slice(0, queryAt);
  if (path.includes("..") || !INVENTORY_PAGES.has(path)) return INVENTORY_HOME;
  if (path === "/backoffice/inventory") {
    return queryAt === -1 ? INVENTORY_HOME : `${INVENTORY_HOME}${decoded.slice(queryAt)}`;
  }
  return decoded;
}

export function viewLabel(path: string): string {
  const base = path.split("?")[0];
  if (base.endsWith("/inbound")) return "la entrada de activos";
  if (base.endsWith("/outbound")) return "la salida de activos";
  if (base.endsWith("/orders")) return "el historial de entradas y salidas";
  if (base.endsWith("/products")) return "los activos";
  return "el inventario";
}
