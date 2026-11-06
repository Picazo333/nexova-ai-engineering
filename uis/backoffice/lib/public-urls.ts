export function portalUrl(): string {
  const raw = process.env.NEXT_PUBLIC_PORTAL_URL?.trim();
  return raw || "http://127.0.0.1:3000";
}

export function apiOrigin(): string {
  const raw = process.env.NEXT_PUBLIC_API_ORIGIN?.trim();
  return (raw || "http://127.0.0.1:8000").replace(/\/$/, "");
}
