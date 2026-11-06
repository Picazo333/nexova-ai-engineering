# Justificación — 023

| ID | Estado | Cómo se cumple | Evidencia |
| --- | --- | --- | --- |
| R01 | PASS | Inicio y solicitud, móvil y escritorio, tres corridas. Inicio móvil 94/100/100/100, LCP 2710 ms. Solicitud móvil 98/100/100/100. | `AUDIT.md`. `docs/performance-web-vitals/evidence/lighthouse-summary.json`. `audit/before/site-home-mobile.png`. |
| R02 | PASS | Panel, login y activos. Panel móvil 100/100/96/63, CLS 0.023. Activos móvil performance 99, best practices 96. | `audit/before/backoffice-home-mobile.png`. `audit/before/backoffice-products-mobile.png`. |
| R03 | PASS | Portal en `next start` puerto 3000. Login móvil 100/100/100/63, LCP 759 ms, CLS 0. `/` redirige a login y mide el viaje. | `audit/before/portal-login-mobile.png`. `audit/before/portal-home-mobile.png`. |
| R04 | PASS | Portal y backoffice: `npm run build` y `npm run start`. El sitio público es HTML estático servido por un servidor de ficheros. Ninguna corrida usa `next dev`. `configSettings.throttlingMethod` es `simulate` en los 42 JSON de antes y los de después. | `AUDIT.md` sección «Cómo se sirvió». |
| R05 | PASS | 14 PNG en `audit/before/`, una por página y modo. Son capturas del informe HTML de la corrida central. | `audit/before/`. |
| R06 | PASS | Puntuaciones, causa del script de Tailwind, de la consola y del CLS, y los dos refactors. | `AUDIT.md`. |
| R07 | PASS | Catálogo duplicado en los dos formularios de inventario. Caja del lockup duplicada entre atributos y CSS. `MotionPref` y `session.ts` se documentan y no se extraen a un paquete nuevo. | `AUDIT.md` sección «Duplicados». |
| R08 | PASS | `useAssetCatalog` usado por `EntryForm` y `ExitForm`. `StableLockup` usado por `FooterLockup`. | `uis/backoffice/components/inventory/useAssetCatalog.ts`. `uis/portal/components/StableLockup.tsx`. |
| R09 | PASS | El script del CDN desaparece. El favicon deja de ser 404. La sonda sin configurar deja de ser un 500 que la UI ya mostraba. No se quita el `noindex`. La diferencia de píxeles del sitio a tres anchos es 0. | `REPORT.md`. `index.html` enlace a `assets/css/site.css`. |
| R10 | PASS | La medición del sitio se repitió solo sobre el HTML ya compilado, antes de mezclarla con el backoffice. La del portal y el backoffice se repitió sobre el build nuevo. Los commits separan el CSS, el lockup, el backoffice y los documentos. | Historial de la rama. `REPORT.md`. |
| R11 | PASS | Las mismas URLs, mismas tres corridas. Capturas en `audit/after/`. | `audit/after/site-home-mobile.png` (98). `audit/after/backoffice-home-mobile.png` (best practices 100, CLS 0). |
| R12 | PASS | Tres correcciones, tablas antes/después, y el mayor impacto es el CSS compilado. | `REPORT.md`. |
| R13 | PASS | Sitio: performance móvil 94→98 y 98→100. Backoffice: best practices 96→100 en panel, login y activos. El portal ya estaba en 100/100/100; el SEO 63 es el `noindex` y no se toca. | `REPORT.md`. |
| R14 | PASS | API 169 passed con Postgres. Raíz 64 passed y 1 skipped. Playwright 14 passed. Jest portal 23 (20 previos + 3). Jest backoffice 17 (14 previos + 3). | Salida de esta corrida, citada en `process/TELEMETRY.json`. |
| R15 | PASS | La skill se leyó y se citan las correcciones que clasifica como necesarias (script bloqueante, caja de imagen). No se vendió como paquete del repo. No hay una instalación fantasma. | `docs/performance-web-vitals/process/SOURCE.md`. `AUDIT.md`. |
| R16 | HITL_ENVIO_MIGUEL | El PR queda abierto. Compartir el repositorio con el instructor es de Miguel. | Checklist de `quality/FINAL_AUDIT.md`. |
| X01 | PASS | `audit/index.html` muestra inicio, solicitud, panel y login del portal, con la mediana anotada al lado de la captura. | `audit/index.html`. |
| X02 | PASS | `lockupFrame` y `useAssetCatalog` / `lib/catalog.ts`, con tests que cubren el corte de 640 px, la proporción de los SVG y las tres transiciones del catálogo. | `uis/portal/__tests__/lockup.test.ts`. `uis/backoffice/__tests__/catalog.test.ts`. |
