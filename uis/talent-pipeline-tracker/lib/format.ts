const DATE_FORMAT = new Intl.DateTimeFormat("es-ES", {
  dateStyle: "long",
  timeStyle: "short",
  timeZone: "Europe/Madrid",
});

export function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return DATE_FORMAT.format(date);
}

export function formatExperience(years: number): string {
  const numeric = Number.isInteger(years) ? String(years) : String(years);
  return years === 1 ? `${numeric} año` : `${numeric} años`;
}

export function formatNotesCount(count: number): string {
  return count === 1 ? "1 nota" : `${count} notas`;
}
