# Backoffice — incidencias, proveedores e inventario

## Inventario de activos

El proceso Next.js de esta carpeta, puerto 3001, incluye la sección de inventario sobre la API de `services/api` (`/inventory`).

Rutas:

- `/backoffice/inventory/products` — activos (`Asset`) y `current_stock` calculado.
- `/backoffice/inventory/orders/inbound` — entrada de activos (`AssetEntry`).
- `/backoffice/inventory/orders/outbound` — salida de activos (`AssetExit`), con el stock del activo elegido antes de enviar.
- `/backoffice/inventory/orders` — historial de solo lectura.

Las llamadas viven en `lib/inventory.ts`. Los componentes no usan `fetch`. La base es `NEXT_PUBLIC_INVENTORY_API_URL` (vacía: `http://127.0.0.1:8000`). El navegador envía `Authorization: Bearer` con el JWT de `POST /auth/login`, guardado en `localStorage` de este origen bajo `nexova-access-token` (la misma clave que el portal; cada origen tiene su propio almacén).

Sin sesión, esas cuatro rutas vuelven a `/login`. Copia `uis/backoffice/.env.example` a `.env.local` si quieres fijar la URL. `.env.local` no se versiona.

```bash
cd uis/backoffice
npm install
npm test
npm run typecheck
npm run dev
```

La API tiene que estar en marcha con `DATABASE_URL` de PostgreSQL. Sin esa variable, `/inventory` responde 503.

Umbral visual, en `lib/stock.ts`: 0 sin stock, menos de 10 bajo, 10 o más saludable.

## Pantallas que sirve la API

La API (`services/api`) sirve las pantallas HTML de esta carpeta (`css/`, `js/`, `partials/`, `tokens/`, `brand/`). No sustituyen al sitio público de la raíz del repositorio.

Además, el mismo directorio arranca como aplicación Next.js en el puerto 3001 cuando se usa Docker. Ese proceso no reemplaza el HTML de la API: comprueba que la API responde y enlaza al portal y al gestor. Los ficheros estáticos y sus hashes no cambian.

- `/` sube el CSV de tickets de soporte, muestra el resumen y descarga `results.csv`.
- `/incidencias/nueva` registra una incidencia: título, descripción, categoría, estado, origen y sede.
- `/incidencias` lista las incidencias, filtra por estado, origen, sede y categoría, y muestra el resumen.
- `/proveedores` es el directorio de contratos externos: filtros por país, categoría y estado, alta, cambio de tarifa mensual y activar o suspender.
- `/privacidad` describe qué se guarda de cada herramienta.

## Qué hay en pantalla

- Carga con selector de fichero y, además, soltar el CSV en la zona. El teclado usa el selector.
- Totales, reglas de invalidez, categoría, estado y satisfacción.
- Detalle de filas inválidas (línea, ticket y regla), sin correo ni descripción.
- Vista previa del CSV de exportación y botón de descarga.
- Estados de espera, vacío, error y resultado. Si un segundo fichero falla, el análisis anterior sigue visible y el aviso lo dice.
- Página de privacidad en `/privacidad`. Una ruta desconocida responde `404`.

Sin JavaScript el formulario de análisis hace `POST` y la API devuelve la página ya rellena. El alta de incidencias también acepta `POST` en `/incidencias/nueva`: si falta la sesión, conserva lo escrito y lo dice. Con JavaScript, el botón de alta se desactiva mientras dura el envío.

En el panel, el resumen y el listado se piden por separado. Si el resumen falla, el listado sigue en la página. Si el cambio de estado falla, el desplegable vuelve al valor anterior. Cuando el origen del formulario es `branch`, la sede se marca con un borde y el texto «Estás reportando desde una sede concreta». Las etiquetas de sede son las del briefing: Central — Sede Valencia, Valencia — Operaciones, Miami Office y Remoto (empleado sin sede fija).

## Señal visual

Tokens, motion y lockups se copiaron byte a byte desde el paquete SIGNAL v1.1.0:

- `tokens/tokens.css`, `tokens/tokens.json`, `tokens/motion.css`, `tokens/motion.json`
- `brand/lockups/signal-horizontal.svg` (pie, ancho 400px desde 640px)
- `brand/lockups/signal-stacked.svg` (pie, ancho 280px por debajo de 640px)
- `brand/README.md` (procedencia, sin modificar)

La prueba `services/api/tests/test_assets.py` compara esos SHA-256 con el manifiesto. Tipografía Arial/Helvetica. No hay fuentes remotas. El lockup del pie es el crédito visual del encargo; el texto dice que no es una asociación oficial.

Hay dos animaciones de 180 ms (`--motion-state`): el fondo del resultado de incidencias y el fondo de la fila cuya tarifa o estado acaba de cambiar. No corren con `prefers-reduced-motion` ni cuando `html[data-motion=reduced]`. El directorio sigue mostrando el dato nuevo sin esa animación.

En el directorio, el país, la categoría y el estado del filtro se guardan en `sessionStorage` de la pestaña. Al volver desde otra sección, el listado se recupera sin recargar a mano.
