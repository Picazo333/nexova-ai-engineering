// Búsquedas: lineal (array en cualquier orden) y binaria (array ya ordenado).

import { Candidate } from "../types/models";

/** Búsqueda lineal por id: revisa uno por uno. Devuelve null si no lo encuentra. */
export function findCandidateById(candidates: Candidate[], id: string): Candidate | null {
  for (const candidate of candidates) {
    if (candidate.id === id) {
      return candidate;
    }
  }
  return null;
}

/** Búsqueda lineal por email, sin importar mayúsculas. Devuelve null si no lo encuentra. */
export function findCandidateByEmail(candidates: Candidate[], email: string): Candidate | null {
  const target = email.trim().toLowerCase();
  for (const candidate of candidates) {
    if (candidate.email.toLowerCase() === target) {
      return candidate;
    }
  }
  return null;
}

/**
 * Búsqueda binaria por salario esperado.
 * REQUISITO: sortedCandidates debe venir ordenado por expectedSalary ascendente
 * (por ejemplo, con sortCandidatesBySalary(lista, "asc")).
 * Devuelve el índice de un candidato con ese salario, o -1 si no existe.
 * Si varios tienen el mismo salario, devuelve cualquiera de sus índices.
 */
export function binarySearchCandidateBySalary(sortedCandidates: Candidate[], targetSalary: number): number {
  let low = 0;
  let high = sortedCandidates.length - 1;

  // En cada vuelta miramos el centro y descartamos la mitad donde no puede estar.
  while (low <= high) {
    const middle = Math.floor((low + high) / 2);
    const middleSalary = sortedCandidates[middle].expectedSalary;

    if (middleSalary === targetSalary) {
      return middle;
    }
    if (middleSalary < targetSalary) {
      low = middle + 1; // el objetivo está a la derecha
    } else {
      high = middle - 1; // el objetivo está a la izquierda
    }
  }
  return -1;
}
