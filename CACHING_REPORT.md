# Informe de caché — Nexova

Medido el 6 de noviembre de 2026 en PostgreSQL 16.15 local (`postgresql:///nexova_audit`) y en los builds de producción de Next.js 15.5.29. El script reproducible es `services/api/scripts/measure_reads.py`. Los números de esta página salen de `docs/caching-optimisation/evidence/measurements.json`.

La semilla del briefing no basta para ver el coste: 6 activos, 6 entradas y 3 salidas. `list_orders` en ese volumen tiene mediana **1,33 ms**. Con el volumen de `app/inventory/volume.py` (480 activos, 5760 entradas, 1920 salidas, claves foráneas reales, oficinas y proveedores variados) la misma función sube a mediana **110,50 ms** (p95 125,95 ms). El directorio del briefing tiene 15 contratos. Con 1500 contratos variados, el recorrido y la validación de `list_suppliers` tienen mediana **12,89 ms**.

El seeder de volumen no arranca con la API. Solo lo ejecuta el script de medida.

## Decisiones en el frontend

### Carga diferida

Tres piezas, con `next/dynamic`. Las dos que cambian el peso de la ruta son los formularios. La tercera saca de la carga inicial un panel que aún no existe.

| Pieza | Por qué se difiere | Antes (`next build`) | Después |
| --- | --- | --- | --- |
| `LazyEntryForm` en `/backoffice/inventory/orders/inbound` | El formulario, el catálogo y la confirmación no hacen falta para pintar el historial ni el listado de activos. Quien abre «Entrada de activos» es quien los necesita. | Ruta 4,41 kB, first load 107 kB | Ruta 1,64 kB, first load 104 kB. El formulario queda en un chunk aparte de 4283 B gzip. |
| `LazyExitForm` en `/backoffice/inventory/orders/outbound` | Misma razón. La salida además calcula el aviso de stock antes de enviar. | Ruta 5,3 kB, first load 108 kB | Ruta 1,64 kB, first load 104 kB. Chunk del formulario: 5167 B gzip. |
| `IncidentResult` en el inicio del portal | Las dos tablas del análisis no existen hasta que hay un CSV analizado. En la primera pintura el estado es «Aún no hay un análisis». | Ruta de `/` 3,65 kB, first load 106 kB | El componente vive en `995.*.js`, 2103 B (707 B gzip), y no está en el chunk de la página. La línea de la ruta sube a 4,2 kB y el first load a 107 kB: el cargador de `next/dynamic` pesa más que el ahorro en esa línea. El ahorro es no descargar las tablas hasta que hay resultado. |

Mientras llega el chunk, el formulario muestra «Cargando el formulario de entrada…» o el de salida, y el resultado del portal «Cargando el resultado del análisis…». Son los `LoadingState` que ya existían.

### `useMemo`

`OrdersScreen` recalcula el historial cuando cambia la fase (carga, error, reintento) aunque el array `orders` sea el mismo. Antes, cada fila llamaba a `formatTimestamp`, y esa función construía un `Intl.DateTimeFormat` nuevo.

Medido en Node 22 con 7680 filas, el tamaño del historial de volumen:

| Pasada | Mediana |
| --- | --- |
| Un `Intl.DateTimeFormat` nuevo por fila (el código anterior) | 361,19 ms |
| Un solo formateador, 7680 fechas | 8,13 ms |
| 20 lecturas del valor ya preparado | 0,009 ms en total |

`rollupOrders` solo, sin fechas, mediana 0,086 ms. Eso no justifica un `useMemo` y no se memoiza aparte.

`prepareHistory(orders)` formatea la fecha, arma el detalle y resume entradas, salidas y oficinas. El componente lo guarda así:

```tsx
const history = useMemo(() => prepareHistory(orders), [orders]);
```

La única dependencia es `orders`. Las funciones de etiquetas son estables y viven en el módulo. Con las 9 órdenes de la semilla el coste es bajo; la función es la misma que en el historial de 7680 filas cuesta 8 ms después de compartir el formateador, y 361 ms antes.

En la pantalla, el resumen visible sale de ese valor. Con la semilla: «6 entradas (88 unidades) y 3 salidas (17 unidades). Miami: 2 órdenes. Valencia: 7 órdenes.»

## Decisiones en el backend

Hay un middleware de tiempos en `create_app` (`api.timing`): método, ruta, consulta, estado y milisegundos. La caché es un diccionario del proceso con TTL (`app/cache.py`). No hay Redis. La API de este repo corre en un solo proceso de uvicorn, sin `--workers`. Una escritura de ese proceso puede vaciar las claves que acaba de invalidar. El TTL sigue siendo obligatorio: sin caducidad, un olvido o un segundo proceso dejaría el dato para siempre.

La marca `X-Nexova-Cache: HIT|MISS` va en un objeto mutable del request. La ruta síncrona corre en un hilo y una asignación a un `ContextVar` no vuelve al middleware.

### `GET /inventory/orders`

Incluye `?office=Valencia` y `?office=Miami`. Cada filtro tiene su clave.

- Coste medido, sin caché, 7680 movimientos: mediana **110,50 ms**, p95 125,95 ms. HTTP (lectura + JSON) en el primer pedido: **256,82 ms**.
- Frecuencia: la pantalla de historial lo pide al entrar y otra vez al cambiar de oficina. El mismo URL se repite en una recarga.
- Estabilidad: el historial solo cambia con una entrada o una salida correctas. Un 400 de stock no escribe y no invalida.
- TTL: **30 segundos**.
- Invalidación: `POST /inventory/orders/inbound` y `POST /inventory/orders/outbound`, después del commit. El middleware vacía el namespace solo si el estado es menor que 400. Se vacían todas las variantes de oficina, porque el listado sin filtro también cambió.
- Después: la segunda petición y las siguientes llevan `HIT`. Mediana **2,06 ms** (Valencia, 2,03 ms). El cuerpo JSON ya codificado es lo que se guarda: volver a serializar 7680 modelos dejaba el HIT en ~114 ms y no merecía la pena.

`user_uuid` de cada fila es quien registró el movimiento, no quien mira. La respuesta es la misma para cualquier lector. La clave es `inventory.orders|shared|office=…`. Una clave por usuario copiaría las mismas filas.

### `GET /suppliers`

Incluye los filtros `country`, `category` y `status`. Cada combinación tiene su clave.

- Coste medido, sin caché, 1500 contratos: mediana **12,89 ms** (España, 9,43 ms). HTTP del primer pedido: **22,66 ms**.
- Frecuencia: el directorio HTML y el portal piden el mismo filtro cada vez que se abre o se cambia el país.
- Estabilidad: cambia al crear, al cambiar tarifa o estado, o al borrar.
- TTL: **60 segundos**.
- Invalidación: `create_supplier`, `update_rate`, `update_status`, `delete_supplier` y `insert_missing` cuando inserta filas. Eso cubre JSON y el formulario HTML. Un 422 no escribe y la lista sigue en HIT.
- Después: HIT mediana **2,43 ms** (España, 1,87 ms).

La respuesta no depende del usuario. Cualquier sesión autenticada ve los mismos contratos. La clave compartida es `suppliers.list.json|shared|…`. El listado en objetos, usado por el HTML, vive en otro namespace (`suppliers.list`) y se invalida junto con el JSON.

## Intercambio entre frescura y rendimiento

El historial tolera 30 segundos. No es un saldo. Quien acaba de registrar una entrada recibe el 201 con la fila nueva, y la siguiente lectura de `GET /inventory/orders` es un MISS porque la escritura vació el namespace. Un lector que no escribió puede ver el historial anterior como máximo 30 segundos, y solo si la escritura ocurrió en otro proceso: en el proceso único del repo la invalidación es inmediata tras el commit. No bajé el TTL a cero porque el primer pedido HTTP cuesta 257 ms y la pantalla lo repite. No lo subí a varios minutos porque el historial es la forma de comprobar un movimiento.

El directorio tolera 60 segundos por la misma razón, con un margen mayor: una tarifa no se consulta como un saldo, y el cambio explícito (PATCH de tarifa o de estado) vacía la caché antes de responder. El minuto cubre un olvido futuro de invalidación. Un proceso de nómina no debería leer esta lista como fuente de un pago.

Queda una carrera estrecha: una lectura que empezó antes del commit y termina después no puede volver a guardar lo que vio. `put` rechaza la escritura si la generación del namespace ya cambió.

## Qué no se cacheó y por qué

- `GET /inventory/products` y `?office=`. Con 480 activos y 7680 movimientos la mediana es **5,94 ms** (Valencia 4,14 ms). En HTTP, la primera respuesta tarda 12,45 ms y las siguientes 9,49 ms, sin cabecera de caché. La agregación SQL ya hace el trabajo en una sentencia. No llega al corte en el que el historial sí llega (110 ms). Cachearlo añadiría una caducidad al stock que la pantalla de activos enseña, a cambio de unos milisegundos.
- `GET /inventory/products/{id}`: mediana **1,33 ms**.
- `GET /profiles/me` y `GET /auth/me`: 2,29 ms y 1,90 ms, sin cabecera de caché. Son la sesión. Un perfil cacheado en una clave compartida filtraría el teléfono y la dirección de una persona a otra. `make_key(..., private=True)` exige el id de usuario y rechaza el id en blanco. Una clave `shared` rechaza llevar un usuario. El test guarda el perfil de `user-a` y comprueba que `user-b` no lo lee. Esas rutas no usan la caché: el dato es barato y tiene que coincidir con la escritura que acaba de hacerse.
- `GET /users` y `GET /users/{id}`: credenciales. No se cachean.
- `POST /knowledge/query` y `GET /knowledge/status`: la pregunta no se repite y el estado de Qdrant cambia al indexar.
- `POST /agent/query`: no es una lectura estable.
- Los POST de inventario, proveedores, usuarios y auth: escriben. No se cachean. Invalidan, cuando corresponde.

## Marca visible

En el historial del backoffice, si la respuesta trae `HIT`, se lee: «Lista leída de la caché en memoria de la API. Caduca a los 30 segundos, o antes si alguien registra una entrada o una salida.» El navegador del backoffice está en otro origen; CORS expone `X-Nexova-Cache`. No es un panel de métricas. Dice de dónde salió esta lista.
