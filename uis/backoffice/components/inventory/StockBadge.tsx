import { stockLabel, stockLevel } from "@/lib/stock";

export function StockBadge({ stock }: { stock: number }) {
  const level = stockLevel(stock);
  return (
    <span className={`stock stock-${level}`} data-testid="stock-level" data-level={level}>
      <span className="stock-count">{stock}</span>
      <span className="stock-label">{stockLabel(level)}</span>
    </span>
  );
}
