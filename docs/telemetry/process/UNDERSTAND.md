# UNDERSTAND — 025 telemetría

El entregable es un plan y un JSON Schema. El enunciado prohíbe instrumentar en esta entrega.

El briefing de telemetría pide cinco eventos y un piso de propiedades (`office` en minúsculas, tres `product_category`, `programme_id`, `quantity`, `currency` EUR/USD sin conversión, sin nombres de personas).

El código de esta rama es el inventario de equipos: `Asset`, `AssetEntry`, `AssetExit`. `current_stock` no es columna. No hay `programme_id`, ni costo, ni `min_stock`. El único umbral configurado es `LOW_STOCK_BELOW = 10` en el panel. Las categorías vivas son `hardware`, `peripherals`, `office_supplies` y `training_materials`. Las oficinas vivas son `Valencia` y `Miami`.

Ese desfase es el diseño: traducir con una tabla versionada, usar `unassigned` cuando no hay programa, dejar el papel fuera de las cinco métricas, y dejar `kit_cost_variance_detected` especificado hasta que exista `unit_cost_minor`. No se inventan costos ni programas para la semilla.

El cliente trata todo 401 como sesión caducada (`redirectToLogin("expired")` y `leaveForLogin`). `session_expired` solo vale con el claim `exp` y la firma válida. python-jose ya distingue `ExpiredSignatureError` en `app/auth/recovery.py`; `decode_access_token` hoy no.

El catálogo añade autenticación, latencia, carga de página, errores de pantalla, secciones y abandonos, más la validación de órdenes y el alta de activos. Cada uno tiene hipótesis y decisión.
