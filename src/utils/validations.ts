// Validaciones de negocio: revisan los datos ANTES de procesarlos o guardarlos.
// Cada regla que falla agrega un mensaje a `errors`; si no hay errores, es válido.

import { Candidate, SelectionProcess, ValidationResult, Vacancy } from "../types/models";

/** Validación básica de email: un solo @ que no va al inicio y un punto después del @. */
export function isValidEmail(email: string): boolean {
  if (email.includes(" ")) return false;

  const atIndex = email.indexOf("@");
  const hasSingleAt = atIndex > 0 && email.indexOf("@", atIndex + 1) === -1;
  if (!hasSingleAt) return false;

  // Debe haber al menos un carácter entre @ y el punto, y algo después del punto.
  const dotIndex = email.lastIndexOf(".");
  return dotIndex > atIndex + 1 && dotIndex < email.length - 1;
}

function isPositiveNumber(value: number): boolean {
  return Number.isFinite(value) && value > 0;
}

/** Reglas de Candidate según el briefing. */
export function validateCandidate(candidate: Candidate): ValidationResult {
  const errors: string[] = [];

  if (!Number.isFinite(candidate.yearsOfExperience) || candidate.yearsOfExperience < 0 || candidate.yearsOfExperience > 50) {
    errors.push("yearsOfExperience debe estar entre 0 y 50");
  }
  if (!isPositiveNumber(candidate.currentSalary)) {
    errors.push("currentSalary debe ser mayor que 0");
  }
  if (!isPositiveNumber(candidate.expectedSalary)) {
    errors.push("expectedSalary debe ser mayor que 0");
  }
  if (!Array.isArray(candidate.skills) || candidate.skills.length < 1) {
    errors.push("skills debe contener al menos 1 habilidad");
  }
  if (!isValidEmail(candidate.email ?? "")) {
    errors.push("email no tiene un formato válido");
  }
  if ((candidate.phone ?? "").trim() === "") {
    errors.push("phone no debe estar vacío");
  }

  return { valid: errors.length === 0, errors };
}

/** Reglas de Vacancy según el briefing. */
export function validateVacancy(vacancy: Vacancy): ValidationResult {
  const errors: string[] = [];

  if (!Array.isArray(vacancy.requiredSkills) || vacancy.requiredSkills.length < 1) {
    errors.push("requiredSkills debe contener al menos 1 habilidad");
  }
  if (!Number.isFinite(vacancy.minYearsExperience) || vacancy.minYearsExperience < 0) {
    errors.push("minYearsExperience debe ser mayor o igual a 0");
  }
  if (!(vacancy.maxYearsExperience >= vacancy.minYearsExperience)) {
    errors.push("maxYearsExperience debe ser mayor o igual a minYearsExperience");
  }
  if (!isPositiveNumber(vacancy.salaryRangeMin) || !isPositiveNumber(vacancy.salaryRangeMax)) {
    errors.push("salaryRangeMin y salaryRangeMax deben ser mayores que 0");
  }
  if (!(vacancy.salaryRangeMax >= vacancy.salaryRangeMin)) {
    errors.push("salaryRangeMax debe ser mayor o igual a salaryRangeMin");
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Reglas de SelectionProcess. El briefing no da una lista explícita para esta
 * entidad; estas reglas salen de su definición (score de 0 a 100, referencias
 * a candidato y vacante) y de la regla general de fechas coherentes del hito.
 */
export function validateSelectionProcess(process: SelectionProcess): ValidationResult {
  const errors: string[] = [];

  if (process.candidateId.trim() === "") {
    errors.push("candidateId no debe estar vacío");
  }
  if (process.vacancyId.trim() === "") {
    errors.push("vacancyId no debe estar vacío");
  }
  if (!Number.isFinite(process.score) || process.score < 0 || process.score > 100) {
    errors.push("score debe estar entre 0 y 100");
  }

  const created = process.createdAt.getTime();
  const updated = process.updatedAt.getTime();
  if (Number.isNaN(created) || Number.isNaN(updated)) {
    errors.push("createdAt y updatedAt deben ser fechas válidas");
  } else if (updated < created) {
    errors.push("updatedAt no puede ser anterior a createdAt");
  }

  return { valid: errors.length === 0, errors };
}
