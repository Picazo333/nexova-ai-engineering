export const TOKEN_KEY = "nexova-access-token";

export function readToken(): string {
  if (typeof window === "undefined") return "";
  try {
    return localStorage.getItem(TOKEN_KEY) ?? "";
  } catch {
    return "";
  }
}

export function writeToken(token: string): boolean {
  try {
    localStorage.setItem(TOKEN_KEY, token);
    return localStorage.getItem(TOKEN_KEY) === token;
  } catch {
    return false;
  }
}

export function clearToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* The next request still fails closed if storage is blocked. */
  }
}
