# Auditoría de rendimiento

Medición de laboratorio con Lighthouse 13.6.0 en Chrome headless, contra servidores de producción. Tres corridas por superficie y por forma. La cifra que se cita es la mediana. La peor va en `docs/performance-web-vitals/evidence/lighthouse-summary.json`.

INP no se publica en este modo. Lighthouse con `throttlingMethod: simulate` no emite Interaction to Next Paint. El sustituto de laboratorio es TBT. No hay un INP inventado.

Cada JSON trae `configSettings` comprobado: móvil `formFactor: mobile`, 390×844, RTT 150 ms, 1638.4 kbps, CPU ×4; escritorio `formFactor: desktop`, 1350×940, RTT 40 ms, 10240 kbps, CPU ×1.

## Cómo se sirvió

| Superficie | Arranque | Por qué no es `next dev` |
| --- | --- | --- |
| Sitio corporativo (`index.html`, `application.html`) | `python3 -m http.server 4173` sobre los ficheros estáticos | No hay proceso Next. El HTML de la raíz es el sitio público. |
| Portal (`uis/website` → `uis/portal`, puerto 3000) | `npm run build` y `npm run start` | El ticket llama website a este proceso. |
| Backoffice (`uis/backoffice`, puerto 3001) | `npm run build` y `npm run start` | Panel interno. |

## Puntuaciones iniciales

Cuatro puntuaciones por página y modo. Performance, accesibilidad, best practices y SEO, en ese orden.

| Página | Móvil | Escritorio | LCP móvil | CLS móvil | TBT móvil | FCP móvil | TTFB móvil |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Sitio, inicio | 94 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 2710 ms | 0 | 46 ms | 2110 ms | 0 ms |
| Sitio, solicitud | 98 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | 1972 ms | 0 | 45 ms | 1972 ms | 0 ms |
| Portal, entrar | 100 / 100 / 100 / 63 | 100 / 100 / 100 / 63 | 759 ms | 0 | 16 ms | 759 ms | 8 ms |
| Portal, `/` (acaba en login) | 100 / 100 / 100 / 63 | 100 / 100 / 100 / 63 | 1891 ms | 0.022 | 16 ms | 759 ms | 3 ms |
| Backoffice, panel | 100 / 100 / 100 / 63 | 100 / 100 / 100 / 63 | 763 ms | 0.023 | 20 ms | 763 ms | 2 ms |
| Backoffice, entrar | 100 / 100 / 100 / 63 | 100 / 100 / 100 / 63 | 761 ms | 0 | 15 ms | 761 ms | 6 ms |
| Backoffice, activos (acaba en login) | 99 / 100 / 96 / 63 | 100 / 100 / 100 / 63 | 1985 ms | 0.027 | 24 ms | 761 ms | 6 ms |

El SEO 63 del portal y del backoffice es `is-crawlable` en cero. Los dos avisan `noindex` a propósito. No es un fallo de contenido.

## Causas raíz

### El inicio espera al compilador de Tailwind

En móvil, el LCP del inicio es la fotografía del héroe (`img.block` dentro del `picture`, `hero-p1-m-800.avif`), con `fetchpriority=high` y descubrible en el HTML. El desglose sin throttling apenas suma 150 ms. La métrica simulada sube a 2.71 s porque el `<head>` carga `https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4` como script bloqueante. Lighthouse estima 1063 ms de espera en ese script (unos 60 KB) y, encima, el navegador compila el CSS antes de pintar. TBT 46 ms y FCP 2.11 s salen de ahí. La solicitud repite el mismo script: LCP y FCP coinciden en 1.97 s.

La skill `core-web-vitals` (addyosmani/web-quality-skills, leída el 2026-11-06, no instalada como paquete del repo) marca como corrección el JavaScript bloqueante en el `<head>`. El CSS que el script generaba ya estaba escrito en las tres páginas (`index.html`, `application.html`, `404.html`): el bloque `@theme` es idéntico.

### El panel registra errores de red que la página ya entiende

Best practices 96 en el backoffice. `errors-in-console` falla por dos peticiones:

- `GET /favicon.ico` → 404. El SVG vivía en la raíz del paquete para la API (`favicon.svg`). El proceso Next no lo publicaba. El portal no falla porque enlaza `/favicon.svg`.
- `GET /api/stack` → 500 cuando falta `API_INTERNAL_URL`. La ruta devolvía el JSON `{ ok: false, message }` que `StackStatus` ya pinta. Chrome igual anota el 500. En login y en activos solo aparece el favicon; en el panel, los dos.

El CLS 0.023 del panel (0.059 en escritorio) es el párrafo de error que se inserta encima de la tabla cuando la sonda termina. El nodo que se mueve es `div.table-scroll`.

### El pie se mueve en la redirección de sesión, no porque el SVG cambie de alto

En el portal, abrir `/` sin token acaba en `/login?next=%2F`. El CLS 0.022 es estable al milésimo en las tres corridas y el nodo es `footer.site-footer`. Entrar directo a `/login` tiene CLS 0. El salto es el cambio de layout entre «Comprobando la sesión» y el formulario, no una imagen sin tamaño en la carga directa.

En activos pasa lo mismo: la URL final mostrada es el login y el CLS 0.027 es el pie. El LCP ~2.0 s incluye la espera de hidratar y redirigir. El login directo pinta en 0.76 s.

El lockup apilado del portal tenía `height: auto` con atributos 280×140. El SVG es 600×300, la misma proporción, así que el alto intrínseco ya coincidía. Reservarlo igual no movió ese CLS. Se deja reservado para que un SVG tardío no pueda crecer el pie. No se igualan las alturas de las dos pantallas: sería un cambio de diseño para perseguir el 0.022.

## Duplicados que se pueden extraer

1. **Carga del catálogo de activos.** `EntryForm` y `ExitForm` repetían el mismo efecto: fase `loading` / `ready` / `error`, conservar las filas si la respuesta llega tarde, y el mensaje de `messageOf`. La abstracción es `useAssetCatalog` más las transiciones puras de `lib/catalog.ts` (`beginCatalog`, `settleCatalog`, `failCatalog`). Los formularios siguen validando y enviando como antes.

2. **Caja del lockup.** El portal declaraba 280×140 y 400×64 en el `<img>` y otro alto en CSS (`auto`). El punto de corte visual es 640 px, el mismo del backoffice. `lockupFrame` devuelve la caja y `StableLockup` pinta los dos SVG con esos números. La proporción 280/140 = 600/300 y 400/64 = 1000/160, que es la de los ficheros.

`MotionPref` y `session.ts` están copiados entre portal y backoffice. No se unifican en un paquete compartido: eso cruzaría el grafo de los dos Next y el enunciado pide no reestructurar la arquitectura.

## Qué no se toca

- `noindex` del portal y del backoffice. Subir el SEO de 63 a 100 sería indexar herramientas internas.
- El compilador no se sustituye por otra librería de estilos. El CSS generado usa las mismas utilidades. La comparación de píxeles del inicio, la solicitud y el 404 a 390, 768 y 1280 px dio diferencia media 0.
- Los SVG del lockup no se reescriben.
