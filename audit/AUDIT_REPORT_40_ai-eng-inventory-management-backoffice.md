# Informe de auditoría adversaria — actividad 40

- **Auditor:** Rodrigo Salcedo (independiente; no es el autor)
- **Fecha:** 13 de noviembre de 2026, 10:52 CST (America/Mexico_City, UTC-6)
- **Slug:** `ai-eng-inventory-management-backoffice`
- **Tarea LMS:** 1022082 (GET 13 nov 2026: `PENDING`, `github_url` vacío)
- **Repo / PR:** [Picazo333/nexova-ai-engineering#24](https://github.com/Picazo333/nexova-ai-engineering/pull/24)
- **Rama:** `feature/inventory-management-backoffice`
- **Head auditado:** `b7ceed40ad3c1552dad156e1a07320127c82bc34` (13 nov 2026, 10:42:03 CST; documentación de ESTADO sobre el checkpoint `dbca757`). El código de UI sigue en `b9c1995` / docs de evidencia en `383db6a` (revisión previa del 12 nov, READY, mismo código).
- **Fuente de criterios:** enunciado oficial `/workspace/ejecucion/022-ai-eng-inventory-management-backoffice/source/OFFICIAL_README.md` @ syllabus `fd2da034`, casillas L114–L123.
- **Alcance:** tests Jest y API con PostgreSQL desechable local (puerto 55432, auth trust, sin contraseña, apagado al terminar), entradas inválidas ya cubiertas por la batería, secretos, adhesión literal (rutas, vocabulario del briefing, módulo de integración). Sin merge, sin LMS, sin créditos, sin Lighthouse de pago.

## Veredicto

**PASA** (READY). 10/10 criterios oficiales PASS. 0 GRAVE. Solo GRAVE bloquea.

HITL abiertos, no restan: envío al LMS, merge. B01 (Supabase) no es criterio del enunciado oficial.

## Criterios oficiales (L114–L123)

| Línea | Criterio | Dictamen | Evidencia de esta pasada |
|---|---|---|---|
| L114 | Módulo de integración; ningún `fetch` en componentes. | **PASS** | `uis/backoffice/lib/inventory.ts` centraliza las llamadas. Jest `los componentes no llaman a fetch` recorre `components` y páginas. El `fetch` vive en `lib/http.ts` (`apiFetch` con `Authorization: Bearer`). |
| L115 | Las peticiones protegidas llevan `Authorization` con el token de sesión. | **PASS** | `lib/http.ts` L84–89: token de `localStorage` (`nexova-access-token`). Test «manda Authorization Bearer». |
| L116 | La página de productos carga datos vivos y muestra `current_stock` con indicador. | **PASS** | `AssetsScreen.tsx`; `StockBadge` y umbral en `lib/stock.ts` (`LOW_STOCK_BELOW = 10`). Ruta `/backoffice/inventory/products`. |
| L117 | El formulario de entrada envía y muestra confirmación o error legible. | **PASS** | `createAssetEntry` → `POST /inventory/orders/inbound`. `EntryForm.tsx`. |
| L118 | El de salida muestra `current_stock` del activo elegido, de forma reactiva, antes de enviar. | **PASS** | `ExitForm.tsx` (StockBadge al cambiar la selección). |
| L119 | Aviso en el cliente si la cantidad supera el stock mostrado. | **PASS** | `data-testid="stock-warning"` en `ExitForm.tsx`. Jest cubre cantidades no enteras. |
| L120 | Un 400 de la salida se ve junto al campo de cantidad. | **PASS** | `id="quantity-api-error"`; test Jest «el 400 de stock insuficiente conserva el mensaje de la API». API: `test_outbound_over_stock_is_400_before_any_write` y `test_two_exits_cannot_oversell_the_same_asset`. |
| L121 | El historial lista órdenes con distinción entrada/salida, nombre, cantidad, fecha y `user_uuid`. | **PASS** | `OrdersScreen.tsx`; `listOrders` en `inventory.ts`. Ruta `/backoffice/inventory/orders`. |
| L122 | Las cuatro páginas redirigen a login si no hay sesión. | **PASS** | Layout `app/backoffice/inventory/layout.tsx` con `SessionGate` (`/login`). Rutas presentes: `products`, `orders/inbound`, `orders/outbound`, `orders`. Jest: «sin token, las cuatro páginas redirigen». |
| L123 | Nombres y etiquetas coinciden con el briefing (Nexova). | **PASS** | Vocabulario Asset / AssetEntry / AssetExit, «Activos», SKU, oficinas Valencia y Miami (`OfficeFilter`, `AssetsScreen`, `InventoryNav`). |

`.env.local` está en `.gitignore` (L3–4). `NEXT_PUBLIC_INVENTORY_API_URL` se lee en `http.ts`.

## Pruebas corridas (esta pasada)

Desde `/tmp/r040`, `UV_PROJECT_ENVIRONMENT=/tmp/venv-r040`, Postgres desechable local:

- `cd services/api && uv sync --group dev`.
- `NEXOVA_TEST_DATABASE_URL` (URI sin contraseña, `127.0.0.1:55432`) → `uv run pytest tests/test_inventory.py`: **12 passed** en 1,86 s.
- Batería completa de la API: **169 passed** en 6,70 s.
- `cd uis/backoffice && npm install && npx jest --coverage`: **14 passed**, 1 suite.

## Seguridad y secretos

Sin `.env` ni `.env.local` en el índice. Escaneo sin claves reales. Escrituras de inventario exigen usuario TinyDB + JWT. El GET público de `/inventory/products` es diseño de 021 (H1, IRRELEVANTE): la UI sí está protegida. Postgres de auditoría apagado y su datadir se elimina.

## Hallazgos

Véase el checkpoint. GRAVE 0, MENOR 0, IRRELEVANTE 2.

## Reproducibilidad

Jest y la API se reprodujeron desde el clone según el README (`npm install` / `uv sync` + pytest). La UI viva contra un backend exige Postgres y, si se quiere Supabase, la URI de Miguel (HITL, no criterio oficial).
