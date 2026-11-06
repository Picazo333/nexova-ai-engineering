import type { CandidateWrite } from "@/types/candidate";

export interface CandidateFormValues {
  full_name: string;
  email: string;
  phone: string;
  position: string;
  linkedin_url: string;
  cv_url: string;
  experience_years: string;
}

export type CandidateField = keyof CandidateFormValues;
export type FieldErrors = Partial<Record<CandidateField, string>>;

export function emptyCandidateForm(): CandidateFormValues {
  return {
    full_name: "",
    email: "",
    phone: "",
    position: "",
    linkedin_url: "",
    cv_url: "",
    experience_years: "",
  };
}

export function validateCandidateForm(values: CandidateFormValues): FieldErrors {
  const errors: FieldErrors = {};
  if (!values.full_name.trim()) errors.full_name = "Escribe el nombre completo.";
  if (!values.email.trim()) errors.email = "Escribe el correo.";
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email.trim())) {
    errors.email = "El correo debe incluir @ y un dominio.";
  }
  if (!values.phone.trim()) errors.phone = "Escribe el teléfono.";
  if (!values.position.trim()) errors.position = "Escribe el puesto.";
  if (!values.experience_years.trim()) {
    errors.experience_years = "Indica los años de experiencia.";
  } else if (!Number.isFinite(Number(values.experience_years))) {
    errors.experience_years = "Los años de experiencia deben ser un número.";
  } else if (Number(values.experience_years) < 0) {
    errors.experience_years = "Los años de experiencia no pueden ser negativos.";
  }
  if (values.linkedin_url.trim() && !isHttpUrl(values.linkedin_url.trim())) {
    errors.linkedin_url = "El enlace de LinkedIn debe empezar por http:// o https://.";
  }
  if (values.cv_url.trim() && !isHttpUrl(values.cv_url.trim())) {
    errors.cv_url = "El enlace del CV debe empezar por http:// o https://.";
  }
  return errors;
}

export function toCandidateWrite(values: CandidateFormValues): CandidateWrite {
  return {
    full_name: values.full_name.trim(),
    email: values.email.trim(),
    phone: values.phone.trim(),
    position: values.position.trim(),
    linkedin_url: values.linkedin_url.trim() || null,
    cv_url: values.cv_url.trim() || null,
    experience_years: Number(values.experience_years),
  };
}

export function validateNoteContent(content: string): string | null {
  if (!content.trim()) return "Escribe la nota antes de guardarla.";
  return null;
}

function isHttpUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}
