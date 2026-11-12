# Justificación — 022

Integración real: API de 021 sobre PostgreSQL 16.15, semilla con NXV-IT-001 = 12 antes de la entrada de evidencia. Transcripción: `evidence/http-transcript.txt`.

| ID | Estado | Cómo se cumple | Evidencia |
| --- | --- | --- | --- |
| R01 | PASS | `listAssets`, `getAsset`, `createAssetEntry`, `createAssetExit` y `listOrders` están en `lib/inventory.ts`. El `fetch` único del cliente está en `lib/http.ts`. La sonda del panel (`/api/stack`) pasó a `lib/stack.ts`. Un test recorre `components/` y `app/` y no encuentra `fetch(`. | `uis/backoffice/lib/inventory.ts` línea 109. `uis/backoffice/__tests__/inventory.test.ts`. |
| R02 | PASS | Con sesión, `apiFetch` pone `Authorization: Bearer` leído de `localStorage` con la clave `nexova-access-token`, la misma que el portal. | `uis/backoffice/lib/session.ts`. `uis/backoffice/lib/http.ts` líneas 83-89. Test «manda Authorization Bearer». |
| R03 | PASS | `errorFrom` lee `detail` o `message`. Un cuerpo vacío no se trata como éxito: «La API respondió N sin un mensaje legible». El 400 de stock conserva la frase inglesa de la API. Un 401 borra el token. | `lib/http.ts` línea 36. Test del 400, del 422, del 500 y de la red. `evidence/http-transcript.txt`. |
| R04 | PASS | La ruta es `/backoffice/inventory/products`. Carga `GET /inventory/products`. | `uis/backoffice/app/backoffice/inventory/products/page.tsx`. `lib/inventory.ts` `listAssets`. |
| R05 | PASS | La tabla muestra nombre, SKU, categoría, oficina y el stock calculado. | `components/inventory/AssetsScreen.tsx`. Captura `evidence/products-1280.png`. |
| R06 | PASS | 0 sin stock, menos de 10 bajo, desde 10 saludable. El comentario está en `lib/stock.ts`. En la semilla: NXV-IT-001 saludable (12), NXV-IT-002 bajo (6), NXV-PER-002 sin stock (0). El texto acompaña al color. | `lib/stock.ts` líneas 1-13. `evidence/products-1280.png`. |
| R07 | PASS | Cada fila tiene «Registrar entrada» y «Registrar salida» con el id en la query. | `AssetsScreen.tsx`. |
| R08 | PASS | El formulario envía `asset_id`, `quantity`, `supplier` y `office`. No manda `user_uuid` ni `current_stock`. | `EntryForm.tsx`. `createAssetEntry`. Confirmación en `evidence/inbound-confirm-768.png`. |
| R09 | PASS | El `select` muestra nombre, SKU y oficina. El valor interno es el id. | `EntryForm.tsx` y `ExitForm.tsx`. |
| R10 | PASS | El éxito vacía los campos y enfoca «Entrada registrada». Un fallo deja lo escrito y muestra el mensaje. El 503 sin base se vio en la UI. | `evidence/inbound-confirm-768.png`. `evidence/products-error-390.png`. |
| R11 | PASS | `SessionGate` usa `loginRedirect`. Sin token, `router.replace` a `/login`. | `lib/paths.ts` línea 16. `evidence/login-redirect-1280.png`. |
| R12 | PASS | `createAssetExit` hace POST a `/inventory/orders/outbound`. Un consumo fuerza `assigned_to: null`. | `lib/inventory.ts` línea 124. Test de consumo. |
| R13 | PASS | Al cambiar el activo se llama a `GET /inventory/products/{id}` y se anuncia el stock. Una respuesta vieja se descarta. | `ExitForm.tsx`. `evidence/outbound-400-1280.png` muestra 12 Saludable. |
| R14 | PASS | Si la cantidad entera supera el stock mostrado, el aviso «Aviso» aparece antes de enviar. El botón sigue permitiendo el envío. | `evidence/outbound-warning-390.png` y el video `recorrido-salida-400.webm`. |
| R15 | PASS | El 400 se pinta en `#quantity-api-error`, junto a la cantidad, con la frase de la API. | `evidence/outbound-400-1280.png`. `evidence/http-transcript.txt`. |
| R16 | PASS | `listOrders` llama a `GET /inventory/orders`. | `OrdersScreen.tsx`. `evidence/orders-1280.png`. |
| R17 | PASS | Columnas: tipo, activo, cantidad, fecha UTC, `user_uuid`. El detalle añade proveedor o `exit_type` y `assigned_to`. | `OrdersScreen.tsx`. |
| R18 | PASS | Etiqueta «Entrada» (info) o «Salida» (acción), no solo color. | `OrdersScreen.tsx`. `evidence/orders-1280.png`. |
| R19 | PASS | No hay botones de borrar ni editar. El texto dice que es solo lectura. | `OrdersScreen.tsx`. |
| R20 | PASS | El layout de `/backoffice/inventory` envuelve las cuatro páginas. El test cubre products, inbound, outbound y orders. | `app/backoffice/inventory/layout.tsx`. Test de `loginRedirect`. |
| R21 | PASS | Títulos: Activos, Entrada de activos, Salida de activos, Historial. Entidades Asset, AssetEntry, AssetExit. | Capturas de productos, entrada y salida. |
| R22 | PASS | `inventoryApiBase` lee `NEXT_PUBLIC_INVENTORY_API_URL` y quita la barra final. El ejemplo está vacío. | `lib/http.ts` línea 15. `uis/backoffice/.env.example`. `.env.example`. |
| R23 | PASS | `.gitignore` ignora `.env.local` y `**/.env.local`. No hay token en el diff. | `.gitignore` líneas 3-4. |
| R24 | PASS | Archivos nuevos bajo `uis/backoffice`. No hay otra aplicación. | Árbol `uis/backoffice/app/backoffice/inventory/`. |
| R25 | PASS | `GET /inventory/products` contra el proceso en PostgreSQL devolvió NXV-IT-001 = 12, NXV-IT-002 = 6, NXV-PER-002 = 0. El 400 se reprodujo en esa API, no en un mock. Las pruebas Jest mockean `fetch` solo para el contrato del cliente. | `evidence/http-transcript.txt`. `evidence/products-1280.png`. |
| S01 | PASS | La UI importa `tokens/tokens.css` y `tokens/motion.css`, ya copiados byte a byte. | `app/globals.css`. |
| S02 | PASS | `--font-body` es Arial, Helvetica, sans-serif. No hay `@import` de fuentes. | `tokens/tokens.css`. |
| S03 | PASS | Cargando activos, lista vacía con «Registrar una entrada», error 503 con «Reintentar». Si un refresco falla y ya había filas, se conservan. | `evidence/products-loading-390.png`, `products-empty-390.png`, `products-error-390.png`, `orders-empty-390.png`. |
| S04 | PASS | axe en productos, salida con 400, confirmación, historial, login, vacío y error: 0 serious y 0 critical. | `evidence/axe-summary.json`. |
| S05 | PASS | Capturas de productos, aviso, 400, confirmación, historial, login, carga, vacío, error y reduced en los anchos pedidos. Overflow del documento = 0. | `evidence/*-390.png`, `*-768.png`, `*-1280.png`. |
| S06 | PASS | `recorrido-salida-400.webm` dura 7,8 s: listado, stock 12, aviso y 400. `recorrido-reduced.webm` dura 5,1 s. | `evidence/recorrido-salida-400.webm`. |
| S07 | PASS | `MotionPref` pone `data-motion=reduced`. La captura lo comprobó. El CSS anula transiciones. | `components/MotionPref.tsx`. `evidence/products-reduced-1280.png`. |
| S08 | PASS | Footer con el horizontal desde 640 px (400 px) y el apilado por debajo (280 px). `sha256sum` del horizontal coincide con el encargo. El apilado es `11314b300284db342bc15a7c7695c23199f65f68178af45586b62d01e9ea133a`. No se reescribieron los SVG. | Salida en la captura. `components/FooterLockup.tsx`. |
| S09 | PASS | Tres corridas, `throttlingMethod=simulate`. Móvil 390×844, RTT 150, 1638,4 kbps, CPU ×4. Escritorio RTT 40, 10240 kbps, CPU ×1. `config_ok` en las seis superficies. INP de laboratorio no sale de esta corrida; se guarda TBT. Peor LCP móvil de productos 1970 ms. Peor CLS de productos móvil 0,027. | `evidence/lighthouse-summary.json`. JSON completos fuera del repo, en los artifacts de la corrida. |
| S10 | PASS | `robots: noindex` y cabecera `X-Robots-Tag: noindex`. No hay sitemap ni schema. | `app/layout.tsx`. `next.config.ts`. |
| S11 | PASS | Matriz en `DESIGN-QA.md`. | Ese archivo. |
| E01 | PASS | La leyenda del umbral está en la página. El vacío propone la entrada. La confirmación cita SKU, orden y `user_uuid`. | Capturas de productos, vacío y confirmación. |
| E02 | PASS | Jest del backoffice: 14 pruebas del guard, los umbrales, el Bearer, el 400, el 422, el 500 y la ausencia de `fetch` en componentes. | `uis/backoffice/__tests__/inventory.test.ts`. |
| D01 | HITL_ENVIO_MIGUEL | Falta que Miguel envíe la URL del fork o del PR a la plataforma del estudiante. | Enunciado, sección de entrega. |
| D02 | HITL_MIGUEL | Falta la revisión humana y la decisión de merge. Este trabajo no mergea. | PR contra `feature/milestone-backend-development`. |
| B01 | PASS | Chequeo SELECT vía MCP el 2026-11-12 15:48 CST. El stock leído coincide con la semilla. La conexión TCP al pooler 6543 no se ejecutó desde la caja y queda declarada como límite. | `evidence/supabase-live/03-mcp-check.json`. |
