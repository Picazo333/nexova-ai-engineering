// Demo: ejecuta cada función con los datos de ejemplo e imprime el resultado.
// Ejecutar:  npm run demo   (o: npx tsc && node dist/demo.js)

import {
  invalidCandidate,
  invalidProcess,
  invalidVacancy,
  sampleCandidates,
  sampleProcesses,
  sampleVacancy,
} from "./data/sampleData";
import { Candidate } from "./types/models";
import {
  filterCandidatesByAvailability,
  filterCandidatesByExperienceRange,
  filterCandidatesBySeniority,
  filterCandidatesBySkills,
  sortCandidatesByExperience,
  sortCandidatesBySalary,
  sortCandidatesBySeniorityAndExperience,
} from "./utils/collections";
import { binarySearchCandidateBySalary, findCandidateByEmail, findCandidateById } from "./utils/search";
import {
  calculateAverageSalary,
  calculateCandidateScore,
  calculateTotalExpectedSalary,
  calculateVacancyFillRate,
  countCandidatesByStatus,
  findExpectedSalaryRange,
  findTopSkills,
  groupCandidatesBySeniority,
  rankCandidatesForVacancy,
} from "./utils/transformations";
import { isValidEmail, validateCandidate, validateSelectionProcess, validateVacancy } from "./utils/validations";

const names = (list: Candidate[]): string => list.map((c) => c.fullName).join(", ") || "(ninguno)";
const show = (label: string, value: unknown): void => console.log(`${label}: ${typeof value === "string" ? value : JSON.stringify(value)}`);

console.log("== Colecciones ==");
show("filterCandidatesBySkills [typescript, REACT]", names(filterCandidatesBySkills(sampleCandidates, ["typescript", "REACT"])));
show("filterCandidatesBySeniority Senior", names(filterCandidatesBySeniority(sampleCandidates, "Senior")));
show("filterCandidatesByAvailability [Immediate, 2 weeks]", names(filterCandidatesByAvailability(sampleCandidates, ["Immediate", "2 weeks"])));
show("filterCandidatesByExperienceRange 4-8", names(filterCandidatesByExperienceRange(sampleCandidates, 4, 8)));
show("sortCandidatesBySalary asc", sortCandidatesBySalary(sampleCandidates, "asc").map((c) => c.expectedSalary));
show("sortCandidatesBySalary desc", sortCandidatesBySalary(sampleCandidates, "desc").map((c) => c.expectedSalary));
show("sortCandidatesByExperience desc", sortCandidatesByExperience(sampleCandidates, "desc").map((c) => c.yearsOfExperience));
show("sortCandidatesBySeniorityAndExperience asc", sortCandidatesBySeniorityAndExperience(sampleCandidates, "asc").map((c) => `${c.seniority}/${c.yearsOfExperience}`));
show("array original intacto (salarios)", sampleCandidates.map((c) => c.expectedSalary));
show("filtro sobre array vacío", names(filterCandidatesBySkills([], ["TypeScript"])));

console.log("\n== Búsqueda ==");
show("findCandidateById C-2024-0453", findCandidateById(sampleCandidates, "C-2024-0453")?.fullName ?? null);
show("findCandidateById C-0000", findCandidateById(sampleCandidates, "C-0000"));
show("findCandidateByEmail JUAN.PEREZ@EMAIL.COM", findCandidateByEmail(sampleCandidates, "JUAN.PEREZ@EMAIL.COM")?.fullName ?? null);
const sortedBySalary = sortCandidatesBySalary(sampleCandidates, "asc");
show("binarySearchCandidateBySalary 6500 (índice)", binarySearchCandidateBySalary(sortedBySalary, 6500));
show("binarySearchCandidateBySalary 9999 (índice)", binarySearchCandidateBySalary(sortedBySalary, 9999));
show("binarySearchCandidateBySalary en array vacío", binarySearchCandidateBySalary([], 4200));

console.log("\n== Scoring y reportes ==");
show("calculateCandidateScore Carolina Silva", calculateCandidateScore(sampleCandidates[2], sampleVacancy));
show("rankCandidatesForVacancy", rankCandidatesForVacancy(sampleCandidates, sampleVacancy).map((r) => `${r.candidate.fullName}=${r.score}`));
const groups = groupCandidatesBySeniority(sampleCandidates);
show("groupCandidatesBySeniority", Object.fromEntries(Object.entries(groups).map(([level, list]) => [level, list.length])));
show("countCandidatesByStatus", countCandidatesByStatus(sampleCandidates));
show("calculateTotalExpectedSalary", calculateTotalExpectedSalary(sampleCandidates));
show("calculateAverageSalary", calculateAverageSalary(sampleCandidates));
show("calculateAverageSalary []", calculateAverageSalary([]));
show("findExpectedSalaryRange", findExpectedSalaryRange(sampleCandidates));
show("findTopSkills top 3", findTopSkills(sampleCandidates, 3));
show("calculateVacancyFillRate", calculateVacancyFillRate(sampleProcesses));

console.log("\n== Validaciones ==");
show("isValidEmail maria.gonzalez@email.com", isValidEmail("maria.gonzalez@email.com"));
show("isValidEmail correo-sin-arroba.com", isValidEmail("correo-sin-arroba.com"));
show("validateCandidate (válido)", validateCandidate(sampleCandidates[0]));
show("validateCandidate (inválido)", validateCandidate(invalidCandidate));
show("validateVacancy (válida)", validateVacancy(sampleVacancy));
show("validateVacancy (inválida)", validateVacancy(invalidVacancy));
show("validateSelectionProcess (válido)", validateSelectionProcess(sampleProcesses[0]));
show("validateSelectionProcess (inválido)", validateSelectionProcess(invalidProcess));
