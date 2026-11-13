export function parseQuantity(raw: string): number | null {
  const text = raw.trim();
  if (!/^[1-9]\d*$/.test(text)) return null;
  const value = Number(text);
  if (!Number.isSafeInteger(value) || value < 1) return null;
  return value;
}
