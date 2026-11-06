export const DEFAULT_API_URL = "https://playground.4geeks.com/tracker/api/v1";

export function getApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  return configured && configured.length > 0 ? configured.replace(/\/$/, "") : DEFAULT_API_URL;
}
