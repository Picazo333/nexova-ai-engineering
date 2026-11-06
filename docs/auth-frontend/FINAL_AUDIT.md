# Auditoría final — 013

Fecha de cierre de la medición: 2026-11-06.

| Resultado | Cantidad |
| --- | --- |
| PASS | 26 |
| FAIL | 0 |
| BLOCKED | 0 |

Criterios: R01–R21, U01–U03, E01–E02. La justificación está en `RUBRIC_JUSTIFICATION.md`.

## Qué se revisó al final

- El guard es de cliente. No hay `middleware.ts`.
- El token de las vistas protegidas está en `localStorage` y viaja en `Authorization: Bearer`.
- Un 401 autenticado borra el token, avisa de sesión vencida y devuelve a la ruta permitida.
- El website de la raíz y las páginas HTML de la API no redirigen al portal.
- Pytest del monorepo: 45 passed. Playwright del portal: 9 passed.
- Lighthouse: 30 informes. `configSettings` verificado en cada uno. Móvil RTT 150 y CPU ×4. Escritorio RTT 40 y CPU ×1. En el repo solo está el resumen.
- No se versiona ningún secreto. `.env.example` del portal tiene el placeholder vacío.
- No se hizo merge.

## Estado

PENDIENTE_REVISION_ORQUESTADOR

No se envía nada al LMS.
