// Operaciones de colecciones: filtrar y ordenar arrays de candidatos.
// Ninguna función modifica el array que recibe: siempre devuelven uno nuevo.

import { AvailabilityStatus, Candidate, SENIORITY_LEVELS, SeniorityLevel, SortOrder } from "../types/models";

/** Candidatos que tienen TODAS las habilidades pedidas (sin importar mayúsculas). */
export function filterCandidatesBySkills(candidates: Candidate[], requiredSkills: string[]): Candidate[] {
  const wanted = requiredSkills.map((skill) => skill.toLowerCase());
  return candidates.filter((candidate) => {
    const owned = candidate.skills.map((skill) => skill.toLowerCase());
    return wanted.every((skill) => owned.includes(skill));
  });
}

/** Candidatos con el nivel de seniority indicado. */
export function filterCandidatesBySeniority(candidates: Candidate[], seniority: SeniorityLevel): Candidate[] {
  return candidates.filter((candidate) => candidate.seniority === seniority);
}

/** Candidatos cuya disponibilidad coincide con cualquiera de los estados dados. */
export function filterCandidatesByAvailability(
  candidates: Candidate[],
  availability: AvailabilityStatus[],
): Candidate[] {
  return candidates.filter((candidate) => availability.includes(candidate.availability));
}

/** Candidatos con años de experiencia entre minYears y maxYears (ambos incluidos). */
export function filterCandidatesByExperienceRange(
  candidates: Candidate[],
  minYears: number,
  maxYears: number,
): Candidate[] {
  return candidates.filter(
    (candidate) => candidate.yearsOfExperience >= minYears && candidate.yearsOfExperience <= maxYears,
  );
}

/** Ordena por salario esperado. Copia el array con [...] para no mutar el original. */
export function sortCandidatesBySalary(candidates: Candidate[], order: SortOrder): Candidate[] {
  const direction = order === "asc" ? 1 : -1;
  return [...candidates].sort((a, b) => (a.expectedSalary - b.expectedSalary) * direction);
}

/** Ordena por años de experiencia, sin mutar el original. */
export function sortCandidatesByExperience(candidates: Candidate[], order: SortOrder): Candidate[] {
  const direction = order === "asc" ? 1 : -1;
  return [...candidates].sort((a, b) => (a.yearsOfExperience - b.yearsOfExperience) * direction);
}

/**
 * Ordena por dos campos: primero seniority y, si empatan, por experiencia.
 * El mismo orden (asc o desc) se aplica a los dos campos.
 */
export function sortCandidatesBySeniorityAndExperience(candidates: Candidate[], order: SortOrder): Candidate[] {
  const direction = order === "asc" ? 1 : -1;
  return [...candidates].sort((a, b) => {
    const seniorityDiff = SENIORITY_LEVELS.indexOf(a.seniority) - SENIORITY_LEVELS.indexOf(b.seniority);
    if (seniorityDiff !== 0) {
      return seniorityDiff * direction;
    }
    return (a.yearsOfExperience - b.yearsOfExperience) * direction;
  });
}
