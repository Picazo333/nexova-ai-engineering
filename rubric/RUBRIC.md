# Rúbrica — 014 ai-eng-user-authentication-restore

Fuente: `OFFICIAL_README.md` y `OFFICIAL_README.es.md` del syllabus `ai-eng-user-authentication-restore` (sha `fd2da034894ba93ba738559280ccde074ab1d953`). No hay cláusula que prohíba herramientas de IA («No utilices herramientas de IA», «write each one yourself», «sin copiar», «no uses ChatGPT»). Se ejecutó la solución.

Orden de autoridad: enunciado 4Geeks > SIGNAL. Hay formularios en el portal Next.js, así que SIGNAL aplica a esas pantallas.

`required` = el enunciado lo exige. `cuenta` = entra en el 100% implementable. `BLOCKED_HITL`, `HITL_MIGUEL`, `HITL_ENVIO_MIGUEL` y `NO_APLICA` no restan de ese 100%. Un mock de correo no convierte en PASS un criterio que pide un envío real.

| ID | Required | Cuenta | Criterio |
| --- | --- | --- | --- |
| R01 | sí | sí | Se construye sobre el monorepo existente y se extiende la auth y el frontend de 012 y 013. No es un repositorio nuevo. |
| R02 | sí | sí | `POST /auth/forgot-password` acepta `{ email }`. Si la cuenta existe y está activa, genera un token firmado de 15–60 minutos y prepara el enlace de restablecimiento. |
| R03 | sí | sí | Ese endpoint responde siempre `200` con el mismo cuerpo, esté o no registrado el correo. |
| R04 | sí | sí | `POST /auth/reset-password` acepta `{ token, new_password }`, valida firma, caducidad y que no se haya usado, hashea la nueva contraseña, actualiza al usuario e invalida el token. |
| R05 | sí | sí | Responde `400` si el token es inválido, ha caducado o ya se usó. |
| R06 | sí | sí | `POST /auth/change-password` exige `Authorization` y `{ current_password, new_password }`. Si la actual no coincide, responde `400` y no cambia el hash. |
| R07 | sí | sí | El correo sale por Resend (proveedor elegido) o SendGrid si `EMAIL_TRANSPORT=sendgrid`. La clave se lee en el servidor. El mensaje lleva el enlace y se lee en móvil. `EMAIL_TRANSPORT=mock` es explícito y solo para pruebas. |
| R08 | sí | sí | Ninguna clave va en el código. Los nombres están en `README` y en `.env.example`, con valor vacío. |
| R09 | sí | sí | `/forgot-password` pide el correo, muestra la confirmación anti-enumeración y desactiva el formulario tras el envío. |
| R10 | sí | sí | `/reset-password` lee `token` de la query, pide la nueva contraseña y la confirmación, y en éxito abre `/login` con un aviso. Si el token falla, hay un error claro y un enlace a `/forgot-password`. |
| R11 | sí | sí | `/account/change-password` pide la actual, la nueva y la confirmación. Comprueba que coinciden antes de llamar a la API y muestra éxito o error. |
| R12 | sí | sí | `/login` muestra «¿Olvidaste tu contraseña?» hacia `/forgot-password`. |
| R13 | sí | sí | El token de un solo uso persiste como hash, caduca y no se puede repetir. |
| V01 | sí | no | `POST /auth/forgot-password` envía un correo real con el enlace a una dirección registrada. |
| D01 | sí | no | Entregar el proyecto al instructor o al LMS. |
| D02 | sí | no | Merge del PR a `main` después de la aprobación. |
| H01 | sí | no | Crear la cuenta en Resend o SendGrid y colocar la clave. |
| D03 | sí | sí | El PR dice qué servicio se eligió, qué variable hace falta y qué flujo se probó de extremo a extremo. |
| U01 | sí | sí | Formularios con tokens SIGNAL, Arial/Helvetica, y estados idle, loading, success, empty y error. |
| U02 | sí | sí | Capturas reales a 390, 768 y 1280 px. |
| U03 | sí | sí | Vídeo corto real del recorrido, entre 5 y 10 s. |
| U04 | sí | sí | `prefers-reduced-motion` deja el indicador de carga en el estado final, sin animación. |
| U05 | sí | sí | Lockup oficial en el pie. Horizontal a 400 px desde 640 px; apilado a 280 px por debajo. Hash del horizontal verificado. |
| U06 | sí | sí | Lighthouse sobre el build de producción: tres corridas móvil y tres de escritorio, con la configuración pedida. |
| U07 | sí | sí | Skip link, etiquetas visibles, foco, `noindex`, axe sin hallazgos serious/critical. |
| U08 | sí | sí | Sin desbordamiento horizontal del documento en 390, 768 y 1280. |
| U09 | no | no | SEO completo de landing pública (canonical, Open Graph de campaña, sitemap). |
| X01 | no | no | Extra visible: pantallas distintas para enlace ausente, caducado y ya usado, cada una con la vía para pedir otro. |
| X02 | no | no | Extra técnico: tope por correo y hora, fila de auditoría del enlace, y prueba de dos restablecimientos a la vez. |

El 100% implementable son las filas con `cuenta = sí`: R01–R13, D03 y U01–U08. Son 22.
