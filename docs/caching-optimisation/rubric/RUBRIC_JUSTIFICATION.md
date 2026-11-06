# Justificación — 024

| ID | Estado | Cómo se cumple | Evidencia |
| --- | --- | --- | --- |
| R01 | PASS | Formularios de entrada y de salida: no están en el primer pintado del historial ni del listado. `IncidentResult`: las tablas del análisis no existen hasta que hay un CSV. | `CACHING_REPORT.md` sección «Carga diferida». |
| R02 | PASS | `next/dynamic` en `LazyEntryForm`, `LazyExitForm` e `IncidentResult`. | `uis/backoffice/components/inventory/LazyEntryForm.tsx`. `LazyExitForm.tsx`. `uis/portal/components/IncidentsScreen.tsx`. |
| R03 | PASS | Formatear 7680 fechas con un `Intl` nuevo por fila: mediana 361,19 ms. El resumen sin fechas: 0,086 ms, y no se memoiza. | `docs/caching-optimisation/evidence/measurements.json` `frontend_prepare_7680_rows`. |
| R04 | PASS | `useMemo(() => prepareHistory(orders), [orders])`. Tras compartir el formateador, la pasada queda en 8,13 ms y no se repite si `orders` no cambia. | `uis/backoffice/components/inventory/OrdersScreen.tsx`. `lib/orders-rollup.ts`. `lib/labels.ts`. |
| R05 | PASS | El informe recorre auth, usuarios, perfiles, inventario, proveedores, incidencias, conocimiento, agente y las páginas HTML. | `CACHING_REPORT.md` secciones de backend y «Qué no se cacheó». |
| R06 | PASS | `GET /inventory/orders` (110,50 ms, se repite al filtrar oficina, solo cambia con una escritura) y `GET /suppliers` (12,89 ms a 1500 contratos, mismos filtros, cambia con tarifa, estado, alta o baja). | `measurements.json`. |
| R07 | PASS | TTL 30 s en el historial y 60 s en el directorio. Un TTL de cero se rechaza. A los 60,0 s el listado de proveedores pasa de HIT a MISS. | `services/api/app/cache.py`. `tests/test_cache.py`. |
| R08 | PASS | Entrada y salida correctas vacían el historial. Un 400 de stock no. Alta, tarifa, estado y borrado vacían proveedores. Un 422 no. | `tests/test_inventory.py` `test_orders_cache_hits_until_a_successful_write`. `tests/test_cache.py`. |
| R09 | PASS | `GET /profiles/me` y `GET /auth/me` no llevan `X-Nexova-Cache`. `make_key` privado exige usuario. La clave de `user-a` no la lee `user-b`. El historial es igual para todos los lectores: la clave es `shared` y no acepta un id. | `tests/test_cache.py` `test_private_keys_include_the_user_and_are_not_shared`, `test_profile_and_session_are_not_cached`. |
| R10 | PASS | El informe tiene frontend, backend (coste, frecuencia, TTL, invalidación), el intercambio y lo que no se cacheó. | `CACHING_REPORT.md`. |
| R11 | PASS | Cada decisión nombra la ruta, la mediana, el volumen de filas y el TTL. `GET /inventory/products` se queda fuera con 5,94 ms medidos, no con una frase genérica. | `CACHING_REPORT.md`. |
| R12 | PASS | 30 s en el historial y 60 s en el directorio: por qué ese retraso es aceptable y por qué no es cero ni varios minutos. | `CACHING_REPORT.md` «Intercambio entre frescura y rendimiento». |
| R13 | PASS | Semilla 6/6/3 → 1,33 ms. Volumen 480/5760/1920 → 110,50 ms sin caché, HTTP 256,82 ms el MISS y 2,06 ms el HIT. Proveedores 15 en la semilla, 1500 en la medida: 12,89 ms → HIT 2,43 ms. | `measurements.json`. |
| R14 | PASS | API 179 passed con Postgres. Raíz 64 passed, 1 skipped. Playwright 14 passed. Jest portal 23. Jest backoffice 20 (17 de la línea base + 3). | `process/TELEMETRY.json`. |
| X01 | PASS | Con HIT, el historial dice que la lista salió de la caché y que caduca a los 30 s. Capturas a 390, 768 y 1280. | `OrdersScreen.tsx`. `evidence/orders-hit-1280.png`. |
| X02 | PASS | Reloj falso: sigue en HIT a los 29,9 s y cae a los 30,0 s. Una generación vieja no se guarda. HTTP de proveedores caduca a los 60 s. Claves privadas separadas. | `tests/test_cache.py`. |
| N01 | NO APLICA | No hay Redis. La caché es el diccionario del proceso. Un mock no se presenta como integración. | `CACHING_REPORT.md`. `app/cache.py`. |
| H01 | HITL_ENVIO_MIGUEL | El PR queda abierto contra `feature/performance-web-vitals`. Compartirlo con el instructor o enviarlo al LMS es de Miguel. | `quality/FINAL_AUDIT.md`. |
