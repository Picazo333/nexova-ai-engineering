const CATEGORY_LABELS: Record<string, string> = {
  hardware: "Hardware",
  peripherals: "Periféricos",
  office_supplies: "Material de oficina",
  training_materials: "Material de formación",
};

const EXIT_LABELS: Record<string, string> = {
  allocation: "Asignación",
  consumption: "Consumo",
};

export function categoryLabel(code: string): string {
  return CATEGORY_LABELS[code] ?? code;
}

export function exitTypeLabel(code: string): string {
  return EXIT_LABELS[code] ?? code;
}

export function orderTypeLabel(code: string): string {
  if (code === "inbound") return "Entrada";
  if (code === "outbound") return "Salida";
  return code;
}

export function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const formatted = new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  }).format(date);
  return `${formatted} UTC`;
}
