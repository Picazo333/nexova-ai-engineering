# Revisión de excelencia

Commit `2bbaf910cbad5c309f0b85b245b5f8285e9c27fa`.

## Extra visible — IMPLEMENT

Aviso único (`ErrorBanner` en el portal, clase `error-banner` en el backoffice) con la frase, un botón de reintentar o la instrucción de volver a enviar, el enlace de inicio donde la página no es ya el inicio, y la línea «Si se repite, contacta con el soporte interno de Nexova.» No hay dirección de correo inventada.

La espera usa el mismo bloque: texto en `role="status"` y una marca cuadrada. En el portal es `LoadingState`. En el backoffice es la clase `loading-state`.

Evidencia: capturas del login a 390, 768 y 1280, del análisis sin fichero a los tres anchos, de la carga del login y del análisis, y el vídeo `error-banner-recorrido.mp4`.

## Extra técnico — IMPLEMENT

`services/api/app/http_catalog.py` traduce el código HTTP a una frase y deja pasar la frase del router solo si es corta y no contiene traza, secreto ni ruta. El 409 y el 422 de la entrega anterior se conservan. El 422 de FastAPI ya no repite el campo `input` (la contraseña corta no vuelve en el JSON).

El mismo criterio está en `uis/portal/lib/http-messages.ts` y en `uis/backoffice/js/errors.js`.

Evidencia: `services/api/tests/test_error_catalog.py` y `uis/portal/__tests__/http-messages.test.ts`, dentro de las 115 y las 19 pruebas en verde.

## Otras decisiones

| Propuesta | Decisión | Motivo |
| --- | --- | --- |
| Redibujar el sitio público con tokens SIGNAL y el lockup | REJECT | El enunciado prohíbe el refactor que no sea manejo de errores. El sitio de marketing es de un hito anterior y tiene su propio pie. El lockup sigue en el portal y en el backoffice, que son las UI de esta plataforma. Los hashes coinciden con el manifiesto. |
| Animación larga del aviso | REJECT | El aviso tiene que leerse al primer pantallazo. La única motion es la marca de carga, 180 ms, y se apaga con `prefers-reduced-motion` y con `data-motion="reduced"`. |
| Toast que desaparece solo | REJECT | Un aviso que se cierra solo se pierde. El patrón es un banner que permanece hasta el siguiente intento. |
| Cliente HTTP de terceros con modo mock | NO APLICA | La API no llama a ningún servicio externo. |

## Reparaciones después de la primera ejecución

1. El botón «Analizar fichero» sin CSV no abría el aviso: el `required` del input cortaba el `submit` antes del script. `app.js` pone `noValidate` y el aviso propio es el que se ve. Playwright volvió a pasar (10).
2. La primera corrida de Lighthouse de escritorio falló porque la emulación móvil quedaba en true. Se fijó `--screenEmulation.mobile=false` y se rehicieron las tres corridas. El JSON de cada una trae `formFactor: desktop`, RTT 40, 10240 kbps y CPU ×1.

## Conteo forense (2026-11-06)

Required aplicables: **29/29 PASS** (R01–R21 + E01–E02 + S01–S06). H01 HITL_ENVIO_MIGUEL fuera del porcentaje. TELEMETRY canónica: borrador local pendiente de publicar → estado REPAIR_DOCS_PENDIENTE.
