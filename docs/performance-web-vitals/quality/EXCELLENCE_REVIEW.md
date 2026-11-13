# Revisión de excelencia — 023

| Extra | Decisión | Motivo | Evidencia |
| --- | --- | --- | --- |
| Galería `/audit/` antes/después, con las puntuaciones al lado de cada captura | IMPLEMENT | Se ve al abrir `audit/index.html`. Cubre el sitio, el backoffice y el portal. No cambia las pantallas de producto. | `audit/index.html`. |
| `StableLockup` + `lockupFrame`, con test de la caja y de la proporción del SVG | IMPLEMENT | El enunciado pide un componente o hook. El test fija 280×140 y 400×64, que son las medidas que ya pintaba el pie. | `uis/portal/components/StableLockup.tsx`. `uis/portal/__tests__/lockup.test.ts`. |
| `useAssetCatalog` y las transiciones puras, con test | IMPLEMENT | Quita el efecto copiado en entrada y salida. El test no levanta el DOM: cubre conservar filas, sustituirlas y guardar el error. | `uis/backoffice/lib/catalog.ts`. Jest 17 passed. |
| Un paquete compartido para `MotionPref` y `session.ts` | REJECT | Están duplicados, y el enunciado lo permite documentar. Unirlos cruza los dos Next. No sube ninguna métrica. | `AUDIT.md`. |
| Quitar `noindex` para subir el SEO de 63 a 100 | REJECT | El portal y el backoffice son internos. Indexarlos infla la puntuación y contradice el `robots` que ya estaba. | `uis/portal/app/layout.tsx`. `uis/backoffice/next.config.ts` cabecera `X-Robots-Tag`. |
| Inlinear los 43 KB de `site.css` en los tres HTML para intentar el 100 del inicio | REJECT | Lighthouse estima ~450 ms de la hoja. Es el CSS real de la página. Duplicarlo en tres documentos no quita bytes y complica regenerarlo. El LCP ya está por debajo de 2.5 s (2253 ms). | `REPORT.md` sección 1. |
| Igualar la altura del guard y del login para borrar el CLS 0.022 | REJECT | El salto es el cambio de pantalla en la redirección por `localStorage`. Aplastar las dos vistas sería un cambio de diseño. El login directo sigue en CLS 0. | `AUDIT.md`. |

La skill de web vitals se usó como guía de causa, no como lista para perseguir el 100.
