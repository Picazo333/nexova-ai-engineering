# Auditoría final — 012 Autenticación

Fecha de la pasada: 2026-11-06.

## Resultado

30/30 criterios required en PASS. Extras E01 y E02 en PASS. Criterios de UI U01–U04 en PASS. Ningún FAIL. Ningún BLOCKED.

El recuento de rutas antiguas protegidas es 10, no 5 inventadas. La suite completa queda en 45 passed.

## Comprobaciones de cierre

| Comprobación | Resultado |
| --- | --- |
| `pytest` | 45 passed, 1 warning de Starlette sobre httpx. Salida en `evidence/pytest.txt`. |
| HTTP real | 201 registro, 200 login / perfil / proveedores con token, 401 sin token, token mal formado y token caducado, 403 al tocar a otro usuario. `evidence/http-transcript.txt`. El secreto de `.env` no está en esa transcripción. |
| Swagger | `/docs` renderiza la guía. Capturas a 1280 y 390. |
| UI | Capturas a 390, 768 y 1280, con sesión y sin ella. Sin desbordamiento horizontal. |
| Lighthouse | Tres corridas. Escritorio: RTT 40 ms, CPU ×1. Móvil: 390×844, RTT 150 ms, 1638.4 kbps, CPU ×4. Mediana móvil de LCP: 1057 ms en `/` y 1056 ms en `/proveedores`. Peor móvil: 1058 ms y 1079 ms. CLS 0 y TBT 0. Dentro del presupuesto. INP no medido en laboratorio. |
| Tests 009 y 011 | Siguen en la misma suite y en verde. El cliente de prueba adjunta un JWT real; no se relajaron las aserciones de negocio. |
| Merge | No se ha hecho merge. |
| LMS | No se ha enviado nada. |

## Límites

- El secreto local no está en el repositorio. Quien clone el proyecto tiene que crear `services/api/.env` a partir de `.env.example`.
- INP no forma parte del JSON de Lighthouse en laboratorio. No se rellena con un número.
- Los JSON completos de Lighthouse no van en el repositorio. Están en `/opt/cursor/artifacts/lighthouse/`. El resumen, con las tres corridas, la mediana y la peor, es `evidence/lighthouse-summary.json`.
- No hay informe axe. No se certifica WCAG.
- Los permisos finos por rol, más allá de «dueño o admin» en credenciales, quedan fuera porque el enunciado no los exige.

## Estado

PENDIENTE_REVISION_ORQUESTADOR. No está READY_TO_SUBMIT.
