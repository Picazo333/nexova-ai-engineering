# Rúbrica — 022 inventario en el backoffice

Required = sí cuenta para el cierre. HITL y BLOCKED_HITL no restan al 100%.

| ID | Required | Criterio |
| --- | --- | --- |
| R01 | sí | Módulo `lib/inventory.ts`. Ningún componente llama a `fetch`. |
| R02 | sí | Las peticiones protegidas llevan `Authorization: Bearer` con el JWT de la sesión existente. |
| R03 | sí | Un 4xx o 5xx extrae el mensaje del cuerpo y no se traga. El 400 de stock insuficiente conserva la frase de la API. |
| R04 | sí | `/backoffice/inventory/products` lista los activos con `GET /inventory/products`. |
| R05 | sí | Cada fila muestra `current_stock` y los campos del briefing: nombre, SKU, categoría, oficina. |
| R06 | sí | Indicador visual de stock bajo y saludable. El umbral está comentado en el código. |
| R07 | sí | Cada fila enlaza a registrar una entrada y una salida de ese activo. |
| R08 | sí | El formulario de entrada hace `POST /inventory/orders/inbound` (`AssetEntry`). |
| R09 | sí | El activo se elige por nombre, no escribiendo el id. |
| R10 | sí | Tras el éxito se limpia el formulario y hay confirmación. Un 400 o 500 se ve en la página. |
| R11 | sí | La entrada exige sesión. Sin token va a `/login`. |
| R12 | sí | El formulario de salida hace `POST /inventory/orders/outbound` (`AssetExit`). |
| R13 | sí | Al elegir un activo se muestra su `current_stock` y cambia con la selección, antes de enviar. |
| R14 | sí | Si la cantidad supera el stock mostrado, hay un aviso en el cliente. La API sigue siendo la regla. |
| R15 | sí | El 400 de stock insuficiente aparece junto al campo de cantidad. |
| R16 | sí | `/backoffice/inventory/orders` lista `GET /inventory/orders`. |
| R17 | sí | Cada fila tiene nombre del activo, cantidad, tipo, fecha y `user_uuid`. |
| R18 | sí | Entrada y salida se distinguen con texto y color. |
| R19 | sí | El historial es de solo lectura. |
| R20 | sí | Las cuatro páginas redirigen a login si no hay sesión. |
| R21 | sí | El vocabulario visible es el del briefing de Nexova, no el genérico del README. |
| R22 | sí | La base es `NEXT_PUBLIC_INVENTORY_API_URL`. Vacía usa `http://127.0.0.1:8000`. |
| R23 | sí | `.env.local` está en `.gitignore`. No se versiona un token. |
| R24 | sí | La sección vive en el backoffice Next.js que ya existía. |
| R25 | sí | La integración se comprobó contra la API real y PostgreSQL con la semilla (NXV-IT-001 = 12). Un mock no cuenta como PASS. |
| S01 | sí | Tokens SIGNAL en la UI nueva. |
| S02 | sí | Arial/Helvetica. Sin fuentes remotas. |
| S03 | sí | Carga, vacío y error con reintento o acción siguiente. |
| S04 | sí | axe sin hallazgos serious ni critical en las vistas medidas. |
| S05 | sí | Capturas reales a 390, 768 y 1280. |
| S06 | sí | Video corto del recorrido real. |
| S07 | sí | `prefers-reduced-motion` deja el estado final sin animar. |
| S08 | sí | Lockup oficial en el footer. Hash del horizontal `85459232bf51e7bf7c94225fd4f2cd6b71a681b6d701cb4ffd6d2a142cf57a81`. |
| S09 | sí | Lighthouse de producción, tres corridas, móvil 390×844 y escritorio, simulate. |
| S10 | sí | App interna: `noindex`. Sin sitemap ni schema inventados. |
| S11 | sí | DESIGN-QA.md. |
| E01 | extra | Visible: leyenda de umbral, estados vacíos con acción y confirmación tras la orden. |
| E02 | extra | Técnico: `lib/inventory.ts` con 4xx/5xx explícito, guard de ruta puro y pruebas Jest. |
| D01 | no | HITL_ENVIO_MIGUEL. Subir la URL del fork o del PR a la plataforma del estudiante. |
| D02 | no | HITL_MIGUEL. Revisar el PR y decidir el merge. |
| B01 | no | BLOCKED_HITL. No hay URI de Supabase. PostgreSQL local no cierra ese criterio. |
