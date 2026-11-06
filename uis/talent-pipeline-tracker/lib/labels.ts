import { CANDIDATE_STAGES, CANDIDATE_STATUSES } from "@/types/candidate";

const STATUS_LABELS: Record<string, string> = {
  received: "Recibida",
  in_progress: "En proceso",
  selected: "Seleccionada",
  discarded: "Descartada",
};

const STAGE_LABELS: Record<string, string> = {
  pending: "Pendiente",
  review: "Revisión",
  personal_interview: "Entrevista personal",
  technical_interview: "Entrevista técnica",
  offer_presented: "Oferta presentada",
};

export function labelStatus(value: string): string {
  return STATUS_LABELS[value] ?? value;
}

export function labelStage(value: string): string {
  return STAGE_LABELS[value] ?? value;
}

export function statusOptions(current?: string): string[] {
  return withCurrent(CANDIDATE_STATUSES, current);
}

export function stageOptions(current?: string): string[] {
  return withCurrent(CANDIDATE_STAGES, current);
}

function withCurrent(values: readonly string[], current?: string): string[] {
  if (!current || values.includes(current)) return [...values];
  return [current, ...values];
}
