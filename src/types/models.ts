// Modelos de dominio de Nexova (Hito 2).
// Los nombres de interfaces, campos y valores copian EXACTAMENTE el briefing:
// docs/briefings/nexova-BRIEFING.02-coding-fundamentals.es.md

// ---------- Tipos de valores permitidos (uniones de literales) ----------

export type EnglishLevel = "A1" | "A2" | "B1" | "B2" | "C1" | "C2" | "Native";

export type SeniorityLevel =
  | "Junior"
  | "Semi-Senior"
  | "Senior"
  | "Lead"
  | "Executive";

export type AvailabilityStatus = "Immediate" | "2 weeks" | "1 month" | "Not available";

export type CandidateStatus = "Active" | "In process" | "Hired" | "Inactive";

export type VacancyStatus = "Open" | "In progress" | "Closed" | "On hold";

export type ProcessStage =
  | "Screening"
  | "Interview"
  | "Technical test"
  | "Final interview"
  | "Offer"
  | "Rejected"
  | "Hired";

export type SortOrder = "asc" | "desc";

// ---------- Entidades de negocio ----------

/** Una persona en la base de datos de talento de Nexova. */
export interface Candidate {
  id: string; // ej: "C-2024-0451"
  fullName: string;
  email: string;
  phone: string;
  yearsOfExperience: number;
  skills: string[];
  englishLevel: EnglishLevel;
  seniority: SeniorityLevel;
  currentSalary: number; // USD
  expectedSalary: number; // USD
  availability: AvailabilityStatus;
  location: string; // ej: "Valencia, España"
  remoteOnly: boolean;
  status: CandidateStatus;
}

/** Una posición abierta que Nexova intenta cubrir para un cliente. */
export interface Vacancy {
  id: string; // ej: "V-2024-0892"
  title: string;
  companyName: string;
  requiredSkills: string[];
  preferredSkills: string[];
  minYearsExperience: number;
  maxYearsExperience: number;
  requiredEnglishLevel: EnglishLevel;
  requiredSeniority: SeniorityLevel;
  salaryRangeMin: number; // USD
  salaryRangeMax: number; // USD
  isRemote: boolean;
  location: string;
  status: VacancyStatus;
}

/** El avance de un candidato dentro del proceso de selección de una vacante. */
export interface SelectionProcess {
  id: string; // ej: "SP-2024-1523"
  candidateId: string;
  vacancyId: string;
  stage: ProcessStage;
  score: number; // 0-100
  notes: string;
  createdAt: Date;
  updatedAt: Date;
}

// ---------- Tipos auxiliares que devuelven las funciones ----------

/** Un candidato junto con su puntaje contra una vacante. */
export interface RankedCandidate {
  candidate: Candidate;
  score: number;
}

/** Cuántos candidatos tienen una habilidad. */
export interface SkillCount {
  skill: string;
  count: number;
}

/** Resultado de una validación: válido o no, y la lista de errores. */
export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

// ---------- Constantes de apoyo ----------
// Los niveles van de menor a mayor. La posición en el array sirve para
// comparar niveles: un índice más alto significa un nivel más alto.

export const ENGLISH_LEVELS: readonly EnglishLevel[] = ["A1", "A2", "B1", "B2", "C1", "C2", "Native"];

export const SENIORITY_LEVELS: readonly SeniorityLevel[] = [
  "Junior",
  "Semi-Senior",
  "Senior",
  "Lead",
  "Executive",
];

export const CANDIDATE_STATUSES: readonly CandidateStatus[] = ["Active", "In process", "Hired", "Inactive"];
