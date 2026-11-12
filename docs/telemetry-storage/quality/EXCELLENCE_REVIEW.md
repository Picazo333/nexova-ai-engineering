# EXCELLENCE REVIEW — 027

## Qué queda por encima del enunciado

El log cuenta insertados y rechazados y clasifica el rechazo (`envelope`, `schema`, `not_object`) sin volcar el dict. Un correo que no está en la allowlist no aparece en la respuesta ni en el log.

El test de rechazo parcial y el del catálogo completo comprueban, contra Postgres, que el lote válido es una sola sentencia `INSERT`. El log del servidor, durante el curl, muestra lo mismo: dos lotes, dos sentencias, siete filas.

Si no hay base, un lote válido responde 503. El navegador reintenta. Un 200 vacío habría borrado la cola.

La tabla tiene RLS activo y ninguna política. El rol dueño inserta. La clave anónima de Supabase, cuando Miguel aplique el SQL, no lee la tabla.

El validador abre `docs/telemetry/event-schemas.json`. El cambio de `$id` a `event-envelope-1.1.0.json` no obliga a mover el archivo ni a tocar el código.

## Qué se dejó fuera a propósito

Supabase. No hay proyecto y no se crea uno. La tabla local no cierra H01, H02 ni H03.

El backoffice no se modifica. Por eso no hay órdenes nuevas disparadas desde la UI en esta rama. Los ejemplos del plan sí se guardan por el endpoint, que es el contrato de esta fase.

No se añade una pantalla de administración. El extra visible de una API es el log.

## Reparaciones

La primera pasada de pytest falló porque el script SQL se partía en un punto y coma del comentario. El separador ahora respeta comillas. La segunda pasada, ya con el merge de `6cc066f`, dejó 179 passed en `tests/` y 196 en el pytest por defecto.

## Límites

`level` es NOT NULL. El enunciado escribe `default 'info'` y no dice NULL. Un nivel ausente no es `info`, `warn` ni `error`.

`tags` no es solo `properties`. También lleva los cinco campos del sobre que el plan usa y que la tabla no tiene como columna. Está escrito en la sección 13. Las claves de la allowlist no se mezclan con claves de más: el esquema las rechaza antes del INSERT.

El tope de un request es 500 eventos. El navegador manda como mucho 20. Por encima, 422, y el frontend descarta ese sobre. No es el lote normal.

`rag-tests` sigue rojo por `tests/api`. No se toca el workflow.

Esta revisión no es la aprobación del dueño. El estado sigue en `PENDIENTE_REVISION_ORQUESTADOR`.
