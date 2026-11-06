/**
 * Umbrales propios del panel de operaciones. La API no los define.
 * current_stock es calculado: suma de AssetEntry.quantity menos suma de AssetExit.quantity.
 * - 0: sin stock
 * - 1 a 9: stock bajo
 * - 10 o más: stock saludable
 * El corte de 10 deja el NXV-IT-002 de la semilla (6) en bajo y el NXV-IT-001 (12) en saludable.
 */
export const LOW_STOCK_BELOW = 10;

export type StockLevel = "out" | "low" | "healthy";

export function stockLevel(currentStock: number): StockLevel {
  if (currentStock <= 0) return "out";
  if (currentStock < LOW_STOCK_BELOW) return "low";
  return "healthy";
}

export function stockLabel(level: StockLevel): string {
  if (level === "out") return "Sin stock";
  if (level === "low") return "Bajo";
  return "Saludable";
}
