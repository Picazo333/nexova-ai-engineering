# DESIGN-QA — formularios de contraseña

Perfil académico. Autoridad: enunciado 4Geeks, luego SIGNAL. Tipografía Arial/Helvetica. Tokens de `uis/portal/tokens/`. Base clara. Sin hero, sin tres tarjetas decorativas, sin métricas inventadas.

## Qué pregunta cada pantalla

| Ruta | Pregunta | Hecho | Acción siguiente |
| --- | --- | --- | --- |
| `/login` | ¿Hay sesión? | `POST /auth/login`. | Entrar, crear cuenta, o recuperar la contraseña. |
| `/forgot-password` | ¿Pedimos un enlace? | `POST /auth/forgot-password`. La frase no dice si el correo existe. | Enviar enlace. Tras el 200 el formulario se cierra. |
| `/reset-password` | ¿Este enlace todavía sirve? | `token` en la query y `POST /auth/reset-password`. | Guardar contraseña, o pedir otro enlace. |
| `/account/change-password` | ¿La sesión conoce la contraseña actual? | `POST /auth/change-password` con el JWT. | Cambiar contraseña, o volver al perfil. |

## Estados

| Ruta | idle | loading | success | empty | error |
| --- | --- | --- | --- | --- | --- |
| `/forgot-password` | Formulario. `restore-forgot-idle-*`. | «Enviando la solicitud…». `restore-forgot-loading-*`. | «Solicitud registrada» y la frase anti-enumeración. `restore-forgot-success-*`. | No hay un listado. El formulario vacío es el estado inicial. | Red caída: «No se pudo enviar», el correo se conserva. `restore-forgot-error-*`. Un correo mal formado marca el campo y no llama. |
| `/reset-password` | Formulario si hay token. | «Guardando la contraseña…». | Redirección a `/login?notice=password-updated`. `restore-login-ok-*`. | Sin token: «Falta el enlace de recuperación». `restore-reset-empty-*`. | Caducado, usado o inválido, con enlace a `/forgot-password`. `restore-reset-expired-*`, `restore-reset-used-*`. Si la confirmación no coincide, no hay petición. |
| `/account/change-password` | Tres campos. `restore-change-idle-*`. | «Cambiando la contraseña…». | «La contraseña se ha actualizado.» | No es un listado. | Actual incorrecta o confirmación distinta. `restore-change-error-*`. |
| `/login` | Correo y contraseña, más el enlace de recuperación. `restore-login-*`. | «Comprobando la sesión…». | Entra en la vista autenticada. | — | Credenciales rechazadas. El aviso de contraseña actualizada es un estado propio. |

## Motion

| Efecto | Para qué | Disparo | Duración | Amplitud | Limpieza | Respaldo |
| --- | --- | --- | --- | --- | --- | --- |
| `loading-pulse` en `.loading-mark` | Decir que la petición sigue abierta. | Envío del formulario. | `--motion-state` (180 ms), ida y vuelta. | Opacidad de 1 a 0,45. No mueve el control. | `prefers-reduced-motion` y `data-motion=reduced` ponen `animation: none`. | El texto «Enviando la solicitud…» sigue visible. |

Evidencia: `evidence/restore-reduced-1280.png` y `evidence/restore-reduced-motion.txt` (`animationName: none`, `dataset: reduced`). El E2E «reduced motion deja el indicador de carga quieto» lo afirma en el navegador.

## Anchos

Capturas a 390, 768 y 1280 px de los estados de la tabla. El documento no desborda: el script compara `scrollWidth` y `clientWidth`. En 390 el lockup es el apilado (280 px). Desde 640 px, el horizontal (400 px). En las tomas de 768 y 1280 se ve el horizontal.

## Accesibilidad

- Un `h1` por ruta. El error de enlace es `h2`.
- Etiquetas visibles, campos de al menos 48 px, botones de al menos 44 px.
- `aria-invalid` y `aria-describedby` en los errores de campo. El aviso usa `role="alert"` o `role="status"`.
- Skip link y `lang="es"` en el layout. `noindex` en el layout y en las rutas nuevas.
- axe (`wcag2a`, `wcag2aa`, `wcag22aa`) en login, forgot idle, forgot success, reset empty, reset used y change idle: cero serious/critical. `evidence/axe.json`.
- No se certifica WCAG por esa ausencia de hallazgos.

## Rendimiento de laboratorio

Build de producción. Tres corridas por superficie y forma. Configuración comprobada en cada JSON (`bad []` en el resumen).

| Superficie | Forma | LCP mediana / peor | CLS | TBT mediana / peor |
| --- | --- | --- | --- | --- |
| `/forgot-password` | móvil 390×844, RTT 150, 1638,4 kbps, CPU ×4 | 1817 / 1822 ms | 0 | 17 / 19 ms |
| `/forgot-password` | escritorio, RTT 40, 10240 kbps, CPU ×1 | 430 / 432 ms | 0 | 0 / 0 ms |
| `/reset-password` | móvil | 1818 / 1823 ms | 0 | 15 / 18 ms |
| `/reset-password` | escritorio | 433 / 436 ms | 0 | 0 / 0 ms |
| `/login` | móvil | 1814 / 1849 ms | 0 | 16,5 / 32,5 ms |
| `/login` | escritorio | 437 / 438 ms | 0 | 0 / 0 ms |

INP de laboratorio: null. Lighthouse en `simulate` no ejecuta una interacción. No se inventa un INP.

Transferencia medida en esas corridas: JS ≈ 110 KiB, CSS ≈ 3 KiB, total ≈ 135 KiB. Por debajo de 170 KiB de JS, 40 KiB de CSS y 1 MiB de primera pantalla. Los JSON completos están en `/opt/cursor/artifacts/lighthouse/`. En el repo, `evidence/lighthouse-summary.json`.

## Lockup

`signal-horizontal.svg` sha256 `85459232bf51e7bf7c94225fd4f2cd6b71a681b6d701cb4ffd6d2a142cf57a81`.
`signal-stacked.svg` sha256 `11314b300284db342bc15a7c7695c23199f65f68178af45586b62d01e9ea133a`.
Los bytes del portal coinciden con el paquete. `evidence/lockup-hashes.txt`. El crédito del pie dice que no es una asociación oficial.

## SEO

NO_APLICA el SEO de landing. Es un portal interno. `robots` noindex. No hay sitemap ni dominio de campaña.
