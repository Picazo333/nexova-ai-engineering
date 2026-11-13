# Informe de auditoría adversaria — actividad 41

- **Auditor:** Rodrigo Salcedo (independiente; no es el autor)
- **Fecha:** 13 de noviembre de 2026, 11:00 CST (America/Mexico_City, UTC-6)
- **Slug:** `ai-eng-performance-web-vitals`
- **Tarea LMS:** 1022010 (GET 13 nov 2026: `task_status=PENDING`, `revision_status=PENDING`, `github_url` vacío)
- **Repo / PR:** [Picazo333/nexova-ai-engineering#25](https://github.com/Picazo333/nexova-ai-engineering/pull/25)
- **Rama:** `feature/performance-web-vitals`
- **Head auditado:** `81912f3a0dbff0a28b760efb2d7b885530e2c464` (13 nov 2026, 10:42:04 CST; sobre el padre `bff4950` que añade este checkpoint, código de rendimiento en `3bc16b5`–`1d690a3`, 6 nov)
- **Fuente de criterios:** enunciado oficial `/workspace/ejecucion/023-ai-eng-performance-web-vitals/source/OFFICIAL_README.md` @ syllabus `fd2da034`, casillas L129–L135. No se usó la rúbrica ampliada del autor como fuente de verdad. No hay recibo independiente del 12 nov para esta actividad.
- **Alcance:** primera pasada adversaria, modo ligero. Se contrastaron entregables, resumen Lighthouse, diffs de correcciones, hooks extraídos, modo de medición y escaneo de secretos (sin reimprimir valores). No se relanzó Lighthouse (es costoso; la evidencia de laboratorio ya está en el repo). Sin merge, sin comentarios en el PR, sin escrituras al LMS, sin créditos de pago.

## Veredicto

**PASA** (READY). 7/7 criterios oficiales de evaluación (L129–L135) PASS. 0 GRAVE. Solo GRAVE bloquea.

HITL abiertos, no restan: envío al LMS, merge.

## Criterios oficiales (L129–L135)

| Línea | Criterio | Dictamen | Evidencia de esta pasada |
|---|---|---|---|
| L129 | Lighthouse antes y después en ambos frontends, modo producción (`build` + `start`, no `dev`), capturas en el repo. | **PASS** | Sitio corporativo: `python3 -m http.server 4173` sobre HTML estático (no hay proceso Next). Portal y backoffice: `npm run build` y `npm run start`. Documentado en `AUDIT.md`. Capturas en `audit/before/` y `audit/after/` (14 PNG por ronda). Resumen de tres corridas y mediana en `docs/performance-web-vitals/evidence/lighthouse-summary.json` (Lighthouse 13.6.0, `throttlingMethod: simulate`, formFactor mobile 390×844 / desktop 1350×940). INP no se inventó: se usó TBT. |
| L130 | `AUDIT.md` identifica problemas concretos con causa raíz, no solo la lista de Lighthouse. | **PASS** | Causas: script bloqueante `@tailwindcss/browser@4` en el `<head>` (LCP del inicio 2,71 s); `GET /favicon.ico` 404 y `GET /api/stack` 500 sin `API_INTERNAL_URL` (Best Practices 96); CLS del lockup por `height: auto`. |
| L131 | Se extrajo e integró al menos un componente o Custom Hook reutilizable. | **PASS** | `useAssetCatalog` + `lib/catalog.ts` usados en `EntryForm` y `ExitForm`. `StableLockup` + `lockupFrame` usados en `FooterLockup`. Ambos casos están documentados en `AUDIT.md`. |
| L132 | `REPORT.md` muestra una mejora medible en al menos una puntuación Lighthouse por frontend. | **PASS** | Sitio: Performance móvil 94→98 (inicio) y 98→100 (solicitud); LCP 2710→2253 ms. Backoffice: Best Practices 96→100 (panel, login y activos). El enunciado habla de dos frontends (sitio y backoffice); ambos mejoran. El portal ya estaba en 100/100/100/63 (`noindex`); se documenta con honestidad. Un 100 no es criterio (nota L137). |
| L133 | Si se instalaron agent skills, hay evidencia de su uso. | **PASS** (condicional) | No se instaló como paquete del repo. `AUDIT.md` cita la skill `core-web-vitals` (addyosmani/web-quality-skills, leída el 6 nov 2026) y aplica la corrección de JS bloqueante que esa skill marca. |
| L134 | Las correcciones atacan causas reales, no cambios superficiales que inflen la puntuación. | **PASS** | Se quitó el compilador de Tailwind del `<head>` y se sirve `assets/css/site.css` (43 KB, Tailwind 4.1.16). El favicon se publica y `/favicon.ico` se reescribe. `GET /api/stack` sin URL válida responde 200 con el mismo cuerpo que ya pintaba `StackStatus`. La caja del lockup deja de usar `height: auto`. |
| L135 | La calidad del código se mantiene: sin funciones rotas ni regresiones de puntuación. | **PASS** | Ninguna puntuación de Performance / Accessibility / Best Practices / SEO baja. El autor declara Jest backoffice 17 passed (14 previos + 3 del catálogo) y portal 23 (20 + 3 del lockup). TBT del portal-home móvil sube 16→26,5 ms dentro de la mediana, con Performance aún en 100: ruido de laboratorio, no una caída de score (IRRELEVANTE). |

## Comprobaciones adversarias (esta pasada)

- El CDN de Tailwind ya no aparece en `index.html`, `application.html` ni `404.html`. `assets/css/site.css` empieza por el banner de Tailwind v4.1.16.
- `useAssetCatalog` está importado en los dos formularios; `StableLockup` en el pie del portal.
- `GET /api/stack` sin `API_INTERNAL_URL` (o con URL inválida) devuelve 200 y `{ ok: false, message }`; un upstream caído sigue en 502. Evita el `errors-in-console` sin ocultar el fallo.
- Escaneo de secretos (patrones de claves, PEM, JWT, `ghp_`, Resend): solo asignaciones de fixtures de tests y runbooks ya conocidos (`test-jwt-secret-local-only`). Sin `.env` con valores. No se reimprimen valores.
- No se relanzó Lighthouse ni las suites Jest en esta pasada (evidencia de laboratorio y declaración de Jest en `REPORT.md`; el código de los hooks está integrado).

## Hallazgos

Véase la tabla del checkpoint. GRAVE 0, MENOR 1 (base del PR distinta de `main`), IRRELEVANTE 2 (JSON bruto de Lighthouse fuera del repo; TBT del portal con score intacto).

## Reproducibilidad

El modo de medición está documentado (producción, no `dev`). Regenerar el CSS: comando en `REPORT.md` con `@tailwindcss/cli@4.1.16`. Un 100 no es obligatorio. El JSON bruto de cada corrida quedó fuera del repo (`/opt/cursor/artifacts/lighthouse/`); el enunciado pide capturas, que sí están, más el resumen con las tres cifras.
