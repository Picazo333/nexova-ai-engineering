# Revisión de excelencia — 011

Los extras no cambian el contrato del enunciado. Los dos pedidos en el lanzamiento están implementados.

## Implementados

### E01 — Filtro de estado y memoria al navegar (visible)

El enunciado pide filtrar por país y por categoría. Además hay un select de estado (`active` / `suspended` / todos). País, categoría y estado se escriben en `sessionStorage` y en la query. Si se abre Privacidad y se vuelve al directorio por el menú, sin query, el listado vuelve a pedir esos filtros y el párrafo lo dice: «Se mantienen el país, la categoría y el estado de tu visita anterior.»

Evidencia: `uis/backoffice/js/suppliers.js`, captura `ui-filters-restored-1280.png` (Spain + `job_boards`, 2 proveedores, sin WeWork).

### E02 — Seeder idempotente y validación antes de TinyDB (técnico)

`validated_seed` construye los modelos Pydantic y, si uno falla, no llama a `insert_missing`. El POST y los PATCH hacen lo mismo: el cuerpo se valida y solo después se abre la escritura. Hay tests que sustituyen la función de escritura por una excepción y comprueban que no se dispara. La segunda pasada de `uv run seed` imprime `Se insertaron 0 registros.` y no revierte una tarifa ya cambiada.

Evidencia: `services/api/tests/test_suppliers.py` y `seed-output.txt`.

### Renovación vencida

El briefing pide marcar la renovación de los próximos 60 días. Los contratos semilla están en 2025 y en enero de 2026. Con el reloj del sistema en 2026-11-06, ninguno cae en esa ventana. Marcarlos como «Renovación vencida» es el dato real, no una fecha fingida. La ventana de 60 días se prueba con un alta cuya fecha es hoy + 10 días (`test_upcoming_renewal_is_marked`).

## Rechazados

| Idea | Decisión | Motivo |
| --- | --- | --- |
| Gráfico de gasto mensual por país | REJECT | El enunciado pide tabla y filtros. Un gráfico añadiría una librería y no cambia la tarea. |
| Exportar el directorio a CSV | DEFER | Útil para Patricia, pero no está en el enunciado y el directorio ya se lee por la API. No hace falta para cerrar la rúbrica. |

## Reparaciones durante la evaluación

1. `updated_at` se guardaba sin microsegundos y un PATCH en el mismo segundo no cambiaba el texto. Ahora el timestamp lleva microsegundos.
2. La tabla a 390 px comprimía las columnas. Pasó a un ancho mínimo con scroll horizontal. A 390 px la tabla mide unos 2790 px y el documento no hace overflow.
3. El primer vídeo duraba 3,8 s. Se volvió a grabar: 6,48 s.
