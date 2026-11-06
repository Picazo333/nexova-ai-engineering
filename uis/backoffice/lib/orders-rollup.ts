/**
 * Summary plus the strings the history table paints.
 * Formatting every timestamp is the costly part once the history grows.
 * Callers memoize the result with the row array as the only dependency.
 */

import { exitTypeLabel, formatTimestamp, orderTypeLabel } from "@/lib/labels";

export type RollupOrder = {
  order_type: "inbound" | "outbound";
  quantity: number;
  office: string;
};

export type OfficeRollup = {
  office: string;
  orders: number;
  units: number;
};

export type OrderRollup = {
  inbound: number;
  outbound: number;
  unitsIn: number;
  unitsOut: number;
  offices: OfficeRollup[];
};

export function rollupOrders(orders: readonly RollupOrder[]): OrderRollup {
  let inbound = 0;
  let outbound = 0;
  let unitsIn = 0;
  let unitsOut = 0;
  const byOffice = new Map<string, OfficeRollup>();
  for (const order of orders) {
    const office = byOffice.get(order.office) ?? { office: order.office, orders: 0, units: 0 };
    office.orders += 1;
    office.units += order.quantity;
    byOffice.set(order.office, office);
    if (order.order_type === "inbound") {
      inbound += 1;
      unitsIn += order.quantity;
    } else {
      outbound += 1;
      unitsOut += order.quantity;
    }
  }
  const offices = [...byOffice.values()].sort((left, right) => left.office.localeCompare(right.office, "es"));
  return { inbound, outbound, unitsIn, unitsOut, offices };
}

export type HistoryOrder = RollupOrder & {
  id: number;
  created_at: string;
  asset_name: string;
  asset_sku: string;
  user_uuid: string;
  supplier: string | null;
  exit_type: string | null;
  assigned_to: string | null;
};

export type PreparedOrder = HistoryOrder & {
  when: string;
  typeLabel: string;
  detail: string;
};

export function prepareHistory(orders: readonly HistoryOrder[]): { summary: OrderRollup; rows: PreparedOrder[] } {
  const rows = orders.map((order) => {
    const typeLabel = orderTypeLabel(order.order_type);
    const detail =
      order.order_type === "inbound"
        ? `Proveedor: ${order.supplier ?? "—"}. Oficina: ${order.office}.`
        : `${exitTypeLabel(order.exit_type ?? "")} (${order.exit_type ?? "—"}). ${
            order.assigned_to ? `assigned_to ${order.assigned_to}.` : "Sin assigned_to."
          } Oficina: ${order.office}.`;
    return { ...order, when: formatTimestamp(order.created_at), typeLabel, detail };
  });
  return { summary: rollupOrders(orders), rows };
}
