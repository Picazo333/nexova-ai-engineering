# EXCELLENCE REVIEW — 026

## Qué queda por encima del enunciado

El indicador de desarrollo dice cuántos eventos hay en cola y cuántos se enviaron, con carga, vacío y error. Los tests de Jest construyen los eventos obligatorios y los comprueban contra `event-schemas.json`. El stub también acepta el cuerpo `text/plain` de `sendBeacon`, para que el cierre de pestaña no dependa de un preflight.

## Qué se dejó fuera a propósito

El portal, el alta de producto y el restablecimiento de contraseña no tienen captura. El enunciado coloca el servicio en el backoffice y pide amplitud, no una pantalla nueva para cada evento del catálogo.

`credential_rejected` con `bad_signature`, `inactive_or_unknown`, `subject_mismatch` o `foreign_credentials` lo puede clasificar el servidor, que tiene el secreto. El navegador no adivina el código. Sí emite `missing_token` y `session_expired` cuando puede comprobarlo.

## Reparación de R22

`web_vital_recorded` se añade en el catálogo 1.1.0. Los 19 eventos de 1.0.0 conservan sus claves y su `schemaVersion`. El evento nuevo exige `1.1.0`. `useReportWebVitals` llama a `track()`. FID y las rutas fuera de la lista no se emiten. El validador sigue en 0 FAIL.

## Reparaciones de la pasada anterior

El 422 del stub salía en HTML porque `/telemetry` no estaba en las rutas de API. Se añadió y el cuerpo de error es JSON.

El tipo de la categoría viva no cabía en el array de categorías con fila en la tabla. El helper `mappedLive` lo estrecha.

La captura del estado vacío interceptaba la ruta demasiado tarde y la navegación ya había resuelto el listado real. La ruta se instala antes de entrar.

El vídeo de Playwright medía 13,36 s. Se recortó y se reencodificó a 9,0 s.

## Límites

La foto del panel Network de Chrome no está. La evidencia del 200 es la petición que hizo el propio Chrome a través de Playwright, el cuerpo `{ "received": 6 }` y el log del stub con `inbound_order_created`, `catalogue_gap_recorded` y `kit_cost_variance_detected`.

`outbound_order_created`, `stock_threshold_triggered` y `direct_stock_edit_rejected` están en el código y en los tests de esquema. No salieron en el lote de la captura de pantalla. El lote de esa captura sí incluye dos obligatorios: la entrada y la desviación de costo.

El indicador de Next en desarrollo tapaba el lockup. `devIndicators` queda en false. No cambia el build de producción.

Esta revisión no es la aprobación visual del dueño. El estado sigue en `PENDIENTE_REVISION_ORQUESTADOR`.
