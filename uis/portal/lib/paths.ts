const ALLOWED = new Set(["/", "/proveedores", "/account/profile", "/account/change-password"]);

export function safeNext(value: string | null): string {
  if (!value) return "/";
  let decoded = value;
  try {
    decoded = decodeURIComponent(value);
  } catch {
    return "/";
  }
  if (!decoded.startsWith("/") || decoded.startsWith("//") || decoded.includes("\\")) {
    return "/";
  }
  const path = decoded.split("?")[0] ?? "";
  if (!ALLOWED.has(path)) return "/";
  return decoded;
}

export function viewLabel(path: string): string {
  const base = path.split("?")[0];
  if (base === "/proveedores") return "el directorio de proveedores";
  if (base === "/account/profile") return "tu perfil";
  if (base === "/account/change-password") return "el cambio de contraseña";
  return "el análisis de tickets";
}
