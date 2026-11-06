# DESIGN-QA — sesión del backoffice

La UI de esta entrega es el panel de sesión sobre el backoffice que ya existía. No es una landing. No se inventa SEO de campaña ni un dominio.

## Bloques

| Bloque | Pregunta | Hecho | Acción |
| --- | --- | --- | --- |
| Sesión | ¿Hay un token en esta pestaña? | El estado lo dice el texto de `#session-status`. | Entrar, crear cuenta o cerrar sesión. |
| Directorio sin token | ¿Puedo ver tarifas y correos? | No. El listado dice que hace falta una sesión y el HTML no trae los nombres del briefing. | Entrar. El JS vuelve a pedir el fragmento con `Authorization`. |
| Directorio con token | ¿Siguen ahí los contratos? | Sí. Misma tabla que en 011. | Filtrar, registrar, cambiar tarifa o estado. |
| Incidencias | ¿El CSV se analiza sin sesión? | No. El `fetch` lleva el token. Sin token, el error es el de la API. | Entrar y pulsar Analizar fichero. |
| Swagger | ¿Cómo se prueba el 401 y el 403? | La guía de `/docs` numera los pasos. | Try it out / Authorize. |

## Estados de la sesión

| Estado | Dónde se ve |
| --- | --- |
| Reposo, sin token | `home-signed-out-*.png`, `directory-locked-*.png`. Texto: no hay sesión. |
| Carga | `session-loading-390.png`. Texto: «Comprobando la sesión…». Botones deshabilitados. |
| Error | `session-error-390.png`. Alerta: la contraseña tiene que tener al menos 8 caracteres. Los campos se conservan. |
| Sesión iniciada | `home-signed-in-*.png`, `directory-open-*.png`. Correo, nombre y rol. Botón Cerrar sesión. |

No hay un porcentaje de progreso inventado. Cerrar sesión borra `sessionStorage` y recarga.

## Anchos

Capturas de página completa a 390, 768 y 1280 px. En las dieciséis tomas de home y directorio, `scrollWidth - clientWidth` fue 0.

El listado de proveedores queda debajo del panel de sesión y de los filtros. En una ventana de 800 px de alto hay que bajar para ver las filas. Las capturas de página completa sí las muestran (`directory-open-1280.png`).

## Lighthouse

Laboratorio local, `throttling-method=simulate`, RTT 40 ms, throughput 10240 kbps, CPU ×1. No se usó el throttling móvil de CPU ×4.

| Página | Forma | LCP | CLS | TBT | INP |
| --- | --- | --- | --- | --- | --- |
| `/` | escritorio 1350×940 | 252 ms | 0 | 0 ms | no medido en laboratorio |
| `/` | móvil 390×844 | 247 ms | 0 | 0 ms | no medido en laboratorio |
| `/proveedores` | escritorio | 251 ms | 0 | 0 ms | no medido en laboratorio |
| `/proveedores` | móvil 390×844 | 244 ms | 0 | 0 ms | no medido en laboratorio |

Fuente: `docs/user-authentication/evidence/lighthouse-summary.json`. INP no aparece en el informe de laboratorio de Lighthouse; no se inventa. TBT es el dato de bloqueo que sí devolvió la herramienta.

Presupuestos de transferencia: el test `test_front_end_transfer_budgets` incluye `auth.js` junto al JS ya existente y sigue bajo 170 KiB gzip. El CSS, con el panel de sesión, sigue bajo 40 KiB gzip.

## Accesibilidad aplicada

- Un `h1` por página, el panel de sesión es `h2` y va después de ese `h1`.
- Labels visibles en correo, contraseña, nombre, teléfono y dirección.
- Campos a 48 px de alto mínimo, botones a 44 px.
- Error en `role="alert"`. El estado de la sesión es `role="status"`.
- El foco visible sigue siendo el outline de 2 px ya definido en `app.css`.
- `prefers-reduced-motion` no cambia este panel: no se añadió motion. Los botones conservan la transición corta que ya tenía el backoffice.
- Contraste: texto `#18202B` sobre `#FFFFFF`, acción `#B53A17` con texto blanco. Son los tokens ya verificados en 009/011.
- El lockup del pie no se modificó.

## Qué no se certificó

No hay informe de axe en esta pasada. No se declara conformidad WCAG por una puntuación. La revisión es de implementación y de capturas, no una auditoría formal.
