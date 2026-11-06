export function emailError(value: string): string | null {
  const text = value.trim().toLowerCase();
  const parts = text.split("@");
  if (parts.length !== 2 || text.includes(" ")) return "El correo no tiene un formato válido.";
  const [local, domain] = parts;
  if (!local || !domain || !domain.includes(".") || domain.startsWith(".") || domain.endsWith(".")) {
    return "El correo no tiene un formato válido.";
  }
  return null;
}

export function passwordError(value: string): string | null {
  if (value !== value.trim() || value.length < 8) {
    return "La contraseña tiene que tener al menos 8 caracteres, sin espacios al borde.";
  }
  if (new TextEncoder().encode(value).length > 72) {
    return "La contraseña no puede superar 72 bytes.";
  }
  return null;
}

export function textLimit(value: string, limit: number, label: string): string | null {
  if (value.trim().length > limit) return `${label} supera los ${limit} caracteres.`;
  return null;
}
