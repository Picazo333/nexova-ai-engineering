// Scoring, ranking, agrupaciones y reportes sobre los datos de selección.

import {
  CANDIDATE_STATUSES,
  Candidate,
  CandidateStatus,
  ENGLISH_LEVELS,
  RankedCandidate,
  SENIORITY_LEVELS,
  SelectionProcess,
  SeniorityLevel,
  SkillCount,
  Vacancy,
} from "../types/models";

// Redondea a 2 decimales. Number.EPSILON corrige casos como 1.005 -> 1.01.
function roundToTwoDecimals(value: number): number {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

function toLowerCaseList(values: string[]): string[] {
  return values.map((value) => value.toLowerCase());
}

// ---------- Scoring por criterio (cada uno devuelve sus puntos) ----------

/** Habilidades: máximo 40 puntos. */
function scoreSkills(candidate: Candidate, vacancy: Vacancy): number {
  const owned = toLowerCaseList(candidate.skills);
  const required = toLowerCaseList(vacancy.requiredSkills);
  const preferred = toLowerCaseList(vacancy.preferredSkills);

  const requiredMatches = required.filter((skill) => owned.includes(skill)).length;
  const preferredMatches = preferred.filter((skill) => owned.includes(skill)).length;

  let requiredPoints = 0;
  if (requiredMatches === required.length) {
    requiredPoints = 40;
  } else if (requiredMatches >= required.length / 2) {
    requiredPoints = 20;
  }
  const preferredPoints = Math.min(preferredMatches * 10, 20);

  return Math.min(requiredPoints + preferredPoints, 40);
}

/** Experiencia: 20 dentro del rango, 10 si está a 1-2 años, 0 si está más lejos. */
function scoreExperience(candidate: Candidate, vacancy: Vacancy): number {
  const years = candidate.yearsOfExperience;
  let distance = 0;
  if (years < vacancy.minYearsExperience) {
    distance = vacancy.minYearsExperience - years;
  } else if (years > vacancy.maxYearsExperience) {
    distance = years - vacancy.maxYearsExperience;
  }

  if (distance === 0) return 20;
  if (distance <= 2) return 10;
  return 0;
}

/** Seniority: 15 si es exacto, 7 si está un nivel arriba o abajo. */
function scoreSeniority(candidate: Candidate, vacancy: Vacancy): number {
  const gap = Math.abs(
    SENIORITY_LEVELS.indexOf(candidate.seniority) - SENIORITY_LEVELS.indexOf(vacancy.requiredSeniority),
  );
  if (gap === 0) return 15;
  if (gap === 1) return 7;
  return 0;
}

/** Inglés: 15 si cumple o supera el nivel requerido. */
function scoreEnglish(candidate: Candidate, vacancy: Vacancy): number {
  const candidateLevel = ENGLISH_LEVELS.indexOf(candidate.englishLevel);
  const requiredLevel = ENGLISH_LEVELS.indexOf(vacancy.requiredEnglishLevel);
  return candidateLevel >= requiredLevel ? 15 : 0;
}

/**
 * Salario: 10 si el esperado está dentro del rango, 5 si supera el máximo
 * hasta en un 20%. Un salario por debajo del mínimo no está "dentro del
 * rango", así que, siguiendo el briefing al pie de la letra, suma 0.
 */
function scoreSalary(candidate: Candidate, vacancy: Vacancy): number {
  const expected = candidate.expectedSalary;
  if (expected >= vacancy.salaryRangeMin && expected <= vacancy.salaryRangeMax) return 10;
  if (expected > vacancy.salaryRangeMax && expected <= vacancy.salaryRangeMax * 1.2) return 5;
  return 0;
}

// ---------- Funciones públicas ----------

/** Puntaje de match (0-100) entre un candidato y una vacante. */
export function calculateCandidateScore(candidate: Candidate, vacancy: Vacancy): number {
  return (
    scoreSkills(candidate, vacancy) +
    scoreExperience(candidate, vacancy) +
    scoreSeniority(candidate, vacancy) +
    scoreEnglish(candidate, vacancy) +
    scoreSalary(candidate, vacancy)
  );
}

/** Puntúa a todos los candidatos y los devuelve del puntaje más alto al más bajo. */
export function rankCandidatesForVacancy(candidates: Candidate[], vacancy: Vacancy): RankedCandidate[] {
  return candidates
    .map((candidate) => ({ candidate, score: calculateCandidateScore(candidate, vacancy) }))
    .sort((a, b) => b.score - a.score);
}

/** Agrupa candidatos por seniority. Todos los niveles aparecen, aunque estén vacíos. */
export function groupCandidatesBySeniority(candidates: Candidate[]): Record<SeniorityLevel, Candidate[]> {
  const groups: Record<SeniorityLevel, Candidate[]> = {
    Junior: [],
    "Semi-Senior": [],
    Senior: [],
    Lead: [],
    Executive: [],
  };
  // reduce va llenando el acumulador sin tocar el array de entrada.
  return candidates.reduce(
    (acc, candidate) => ({ ...acc, [candidate.seniority]: [...acc[candidate.seniority], candidate] }),
    groups,
  );
}

/** Cuenta candidatos por estado. Todos los estados aparecen, aunque valgan 0. */
export function countCandidatesByStatus(candidates: Candidate[]): Record<CandidateStatus, number> {
  const initial = CANDIDATE_STATUSES.reduce(
    (acc, status) => ({ ...acc, [status]: 0 }),
    {} as Record<CandidateStatus, number>,
  );
  return candidates.reduce((acc, candidate) => ({ ...acc, [candidate.status]: acc[candidate.status] + 1 }), initial);
}

/** Suma de los salarios esperados. */
export function calculateTotalExpectedSalary(candidates: Candidate[]): number {
  return candidates.reduce((total, candidate) => total + candidate.expectedSalary, 0);
}

/** Salario esperado promedio, redondeado a 2 decimales. Lista vacía -> 0. */
export function calculateAverageSalary(candidates: Candidate[]): number {
  if (candidates.length === 0) return 0;
  return roundToTwoDecimals(calculateTotalExpectedSalary(candidates) / candidates.length);
}

/** Salario esperado mínimo y máximo. Lista vacía -> null. */
export function findExpectedSalaryRange(candidates: Candidate[]): { min: number; max: number } | null {
  if (candidates.length === 0) return null;
  const salaries = candidates.map((candidate) => candidate.expectedSalary);
  return { min: Math.min(...salaries), max: Math.max(...salaries) };
}

/** Las N habilidades más comunes (cuántos candidatos tienen cada una). */
export function findTopSkills(candidates: Candidate[], topN: number): SkillCount[] {
  if (topN <= 0) return [];

  // Contamos con un Map cuya clave es la habilidad en minúsculas, igual que en
  // los filtros: "React" y "react" son la misma habilidad. Se muestra con la
  // primera forma en que apareció. Cada candidato suma 1 aunque la repita.
  const counts = new Map<string, SkillCount>();
  for (const candidate of candidates) {
    const uniqueSkills = new Set(toLowerCaseList(candidate.skills));
    for (const key of uniqueSkills) {
      const original = candidate.skills.find((skill) => skill.toLowerCase() === key) ?? key;
      const current = counts.get(key) ?? { skill: original, count: 0 };
      counts.set(key, { skill: current.skill, count: current.count + 1 });
    }
  }

  return Array.from(counts.values())
    .sort((a, b) => b.count - a.count || a.skill.localeCompare(b.skill))
    .slice(0, topN);
}

/** Porcentaje de procesos que terminaron en "Hired" (0-100, 2 decimales). */
export function calculateVacancyFillRate(processes: SelectionProcess[]): number {
  if (processes.length === 0) return 0;
  const hired = processes.filter((process) => process.stage === "Hired").length;
  return roundToTwoDecimals((hired / processes.length) * 100);
}
