export const CATEGORY_LABELS: Record<string, string> = {
  job_boards: "Bolsas de empleo",
  ats_software: "Software de selección (ATS)",
  assessment_tools: "Pruebas de evaluación",
  training_platforms: "Plataformas de formación",
  payroll_and_hr_software: "Nómina y software de RR. HH.",
  video_interview: "Entrevista en vídeo",
  background_check: "Verificación de antecedentes",
  office_and_facilities: "Oficina e instalaciones",
  it_and_software_licenses: "Licencias de TI y software",
};

export const COUNTRY_LABELS: Record<string, string> = {
  Spain: "España",
  USA: "Estados Unidos",
};

export const STATUS_LABELS: Record<string, string> = {
  active: "Activo",
  suspended: "Suspendido",
};

export function categoryLabel(code: string): string {
  return CATEGORY_LABELS[code] ?? code;
}

export function countryLabel(code: string): string {
  return COUNTRY_LABELS[code] ?? code;
}

export function statusLabel(code: string): string {
  return STATUS_LABELS[code] ?? code;
}
