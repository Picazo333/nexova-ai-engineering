# Revisión de excelencia — 022

## Extra visible — IMPLEMENTADO

Leyenda del umbral en la página de activos, estados vacíos con una acción siguiente y confirmación después de registrar la orden, con SKU, número de orden y `user_uuid`.

El enunciado ya pedía el indicador y la confirmación. Lo que se añade y se ve es la leyenda (0 / menos de 10 / desde 10), el vacío de activos y de historial, y el filtro por oficina Valencia o Miami, que usa el query real `office` de la API.

Evidencia: `evidence/products-1280.png`, `evidence/products-empty-390.png`, `evidence/orders-empty-390.png`, `evidence/inbound-confirm-768.png`.

## Extra técnico — IMPLEMENTADO

`lib/http.ts` no convierte un 4xx o un 5xx en éxito. El 400 de stock insuficiente se muestra tal cual. `loginRedirect` es una función pura cubierta por Jest. Los componentes no llaman a `fetch`.

Evidencia: `uis/backoffice/__tests__/inventory.test.ts` (14 passed) y `evidence/http-transcript.txt`.

## Rechazado

No se añadió un alta de activos en esta UI. El enunciado pide consultar, entrar, salir y el historial. Crear activos es otra ruta de la API y no hacía falta para el brief.

No se compartió el `localStorage` del portal con un truco de cookies. Son orígenes distintos. El backoffice entra con el mismo `POST /auth/login` y la misma clave.

## Diferido

Medir INP con un usuario real. Lighthouse simulate no lo emite. El sustituto de laboratorio es TBT, por debajo de 20 ms en la peor corrida móvil de productos.

## Reparaciones de esta pasada

1. El primer arranque de Next perdió `.next` al coincidir con otros procesos. Se reinició un solo dev server.
2. El 400 no aparecía porque la asignación sin `assigned_to` se quedaba en la validación del cliente. El recorrido rellena `NXV-EMP-1042` y entonces la API responde 400.
3. `overflow-wrap: anywhere` partía «Valencia». Quedó solo en `.mono`.
4. Los videos salían de menos de 3 s. Se alargaron a 7,8 s y 5,1 s.
5. Un `.env` local con `DATABASE_URL` hacía fallar `test_products_without_database_url_are_503` porque `load_local_env` volvía a poner la variable. Se quitó del `.env` local. El fichero no se versiona. La suite quedó en 169 passed.
6. El CLS móvil de la ruta anónima de productos era 0,234: el pie saltaba al redirigir a login y el SVG no reservaba caja. El marco del lockup tiene alto fijo y el `main` crece para empujar el pie. Tras el cambio, el peor CLS móvil de productos es 0,027.
