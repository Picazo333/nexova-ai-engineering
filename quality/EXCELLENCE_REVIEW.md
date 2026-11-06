# Revisión de excelencia — 015

Los extras no sustituyen la rúbrica. El despliegue al VPS sigue en BLOCKED_HITL.

## Extra visible — IMPLEMENTADO

`make up` anuncia las tres URLs antes de levantar Compose: portal en el puerto 3000, backoffice en el 3001 y `GET /health` de la API.

El panel del puerto 3001 muestra, en una tabla, el destino interno al que llegó. En la corrida real esa celda dice `services:8000` y el estado «En marcha». No es un texto fijo de adorno: sale de `GET /api/stack`, que en el servidor llama a `API_INTERNAL_URL`.

Evidencia: `Makefile`, `README.es.md`, `evidence/container-success-1280.png`, `evidence/stack-internal.json`.

## Extra técnico — IMPLEMENTADO

1. **Contrato ejecutable.** `tests/infra/test_compose_contract.py` comprueba la red con nombre, los `.dockerignore`, la ausencia de literales de secreto, que `.env` está ignorado y que no hay historial de ese fichero, y que el rellenado del `.env` no pisa un `JWT_SECRET` ya puesto.
2. **Healthchecks y usuario no root.** La UI comprueba 3000 y 3001. La API comprueba `/health`. Los procesos corren como uid 1000 (`node` y `app`).
3. **Recarga sin rebuild.** Un cambio en el host apareció en el puerto 3001 a los 3 s y en `/health` al segundo, sin `docker compose build`. El marcador se retiró después.

Evidencia: `evidence/compose-ps.txt`, `evidence/hot-reload.txt`, `evidence/pytest-root.txt` (7 pruebas de contrato dentro de las 64).

## Rechazado

No se convirtió `uis/backoffice` en un clon del portal. El HTML de incidencias y proveedores ya lo sirve la API y los tests de assets comparan bytes. Duplicarlo rompería esa entrega.

No se añadió un sitio público Next nuevo. El sitio público sigue en la raíz del repositorio.

## Diferido

Medir el tiempo de arranque en frío de `next dev` dentro del contenedor en un portátil con Docker Desktop. Aquí el healthcheck esperó y pasó; no hay una cifra de un Mac que se pueda citar.
