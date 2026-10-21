# Hito 2 — Modelos de dominio y utilidades TypeScript (Nexova)

Rama: `feature/domain-models` → `main`

Briefing usado: [`docs/briefings/nexova-BRIEFING.02-coding-fundamentals.es.md`](../briefings/nexova-BRIEFING.02-coding-fundamentals.es.md), copia literal del contexto oficial `content/contexts/02-coding-fundamentals/nexova-BRIEFING.es.md` del syllabus. Las entidades, los campos y las reglas de este hito están en ese documento; el `BRIEFING.md` de la raíz es el briefing general del Milestone 0 y no las define.

## Qué implementé

| Archivo | Contenido |
|---|---|
| `src/types/models.ts` | Interfaces `Candidate`, `Vacancy`, `SelectionProcess` y los tipos `EnglishLevel`, `SeniorityLevel`, `AvailabilityStatus`, `CandidateStatus`, `VacancyStatus`, `ProcessStage`, con los nombres exactos del briefing. Tipos auxiliares (`RankedCandidate`, `SkillCount`, `ValidationResult`) y constantes ordenadas de niveles. |
| `src/utils/collections.ts` | `filterCandidatesBySkills` (todas las habilidades, sin distinguir mayúsculas), `filterCandidatesBySeniority`, `filterCandidatesByAvailability`, `filterCandidatesByExperienceRange`, `sortCandidatesBySalary`, `sortCandidatesByExperience`, `sortCandidatesBySeniorityAndExperience` (dos campos). Ninguna muta el array original. |
| `src/utils/search.ts` | Búsqueda lineal `findCandidateById` y `findCandidateByEmail` (devuelven `null` si no encuentran) y búsqueda binaria `binarySearchCandidateBySalary` (devuelve el índice o `-1`). |
| `src/utils/transformations.ts` | `calculateCandidateScore` (0-100, con las 5 reglas del briefing), `rankCandidatesForVacancy`, `groupCandidatesBySeniority`, `countCandidatesByStatus`, `calculateTotalExpectedSalary`, `calculateAverageSalary`, `findExpectedSalaryRange`, `findTopSkills`, `calculateVacancyFillRate`. |
| `src/utils/validations.ts` | `isValidEmail`, `validateCandidate`, `validateVacancy` (reglas del briefing) y `validateSelectionProcess` (score 0-100 y fechas coherentes). |
| `src/data/sampleData.ts` | Los datos de ejemplo del briefing y algunos registros extra, incluidos datos inválidos a propósito. |
| `src/demo.ts` | Ejecuta cada función e imprime el resultado. |
| `package.json`, `tsconfig.json` | TypeScript `5.9.3` y `tsx` `4.23.15` con versión exacta; modo `strict`. |

Puse `src/` en la raíz porque así lo muestra la estructura de archivos del README del hito. El monorepo no tenía `package.json` ni `tsconfig.json` en la raíz, así que no hubo nada que fusionar. `packages/shared` quedó intacto.

## Desafíos y cómo los resolví

- **Tope de 40 puntos en habilidades.** Las reglas suman hasta 60 (40 por requeridas y 20 por deseables), pero el bloque tiene un máximo de 40. Apliqué `Math.min(..., 40)`. Por eso Carolina Silva saca 100 aunque le falte `React`: cumple 2 de 3 requeridas (20) y tiene las 2 deseables (20).
- **Salario por debajo del mínimo.** El briefing da puntos si el salario esperado está dentro del rango o hasta un 20 % por encima, pero no menciona el caso de estar por debajo. Seguí la regla al pie de la letra: debajo del mínimo suma 0. Si el mentor lo interpreta distinto, solo cambia `scoreSalary`.
- **Mayúsculas en habilidades.** El filtro debía ignorar mayúsculas. Usé el mismo criterio en el scoring y en `findTopSkills` para que `react` y `React` cuenten como la misma habilidad.
- **No mutar.** `Array.prototype.sort` modifica el array, así que primero copio con `[...candidates]`.
- **Redondeo a 2 decimales.** `Math.round((x + Number.EPSILON) * 100) / 100` evita errores como `1.005 → 1.00`.
- **Casos vacíos.** Con listas vacías, el promedio y la tasa devuelven `0`, el rango devuelve `null` y las búsquedas devuelven `null` o `-1`.

## Cómo verificar

```bash
npm install          # instala typescript 5.9.3 y tsx 4.23.15
npx tsc --noEmit     # o: npm run typecheck  → sin salida = 0 errores
npm run demo         # ejecuta src/demo.ts con tsx
npm run demo:node    # alternativa: compila a dist/ y ejecuta con node
```

Resultado esperado del ranking con la vacante de ejemplo: `Carolina Silva=100, Diego Navarro=90, María González=82, Lucía Romero=67, Juan Pérez=10`.
