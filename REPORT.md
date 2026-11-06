# Informe de las correcciones

Cada fila es la mediana de tres corridas Lighthouse 13.6.0, producción, `simulate`. El JSON completo de cada corrida está fuera del repo, en `/opt/cursor/artifacts/lighthouse/`. El resumen con las tres cifras y la peor está en `docs/performance-web-vitals/evidence/lighthouse-summary.json`.

## 1. CSS compilado en el sitio corporativo

Se quitó `<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4">` de `index.html`, `application.html` y `404.html`. El bloque `@theme` pasó a `assets/css/site.source.css` y el resultado minificado es `assets/css/site.css` (43 KB). Las páginas enlazan esa hoja. Regenerar:

```bash
npx --yes @tailwindcss/cli@4.1.16 -i assets/css/site.source.css -o assets/css/site.css --minify
```

hace falta `tailwindcss@4.1.16` resoluble desde `assets/css`. El comando está comentado en la fuente.

| Página | Modo | Performance | LCP | FCP | TBT | CLS |
| --- | --- | --- | --- | --- | --- | --- |
| Inicio | móvil | 94 → 98 | 2710 → 2253 ms | 2110 → 1415 ms | 46 → 0 ms | 0 → 0 |
| Inicio | escritorio | 100 → 100 | 611 → 524 ms | 571 → 282 ms | 0 → 0 | 0 → 0 |
| Solicitud | móvil | 98 → 100 | 1972 → 1053 ms | 1972 → 1053 ms | 45 → 0 ms | 0 → 0 |
| Solicitud | escritorio | 100 → 100 | 535 → 291 ms | 535 → 291 ms | 0 → 0 | 0 → 0 |

El LCP del inicio baja de por encima de 2.5 s a 2.25 s. Sigue habiendo una hoja bloqueante: Lighthouse estima unos 450 ms en `site.css`. Es el CSS que la página necesita, no un compilador. No se duplica en los tres HTML para arañar el último punto.

La comparación de pantalla completa antes/después, a 390, 768 y 1280 px, dio diferencia media de píxel 0 en inicio, solicitud y 404. Playwright del portal (`e2e/public.spec.ts`) cargó `assets/css/site.css` y pasó.

## 2. Consola del backoffice

`app/icon.svg` es el mismo SVG que ya servía la API. `next.config.ts` reescribe `/favicon.ico` hacia `/icon.svg` (200, `image/svg+xml`). Sin eso Chrome seguía pidiendo `/favicon.ico` y Lighthouse lo contaba como error aunque existiera `<link rel="icon" href="/icon.svg">`.

`GET /api/stack` sin `API_INTERNAL_URL`, o con una URL que no es URL, responde 200 y el mismo cuerpo `{ ok: false, message }`. Un upstream configurado que no responde sigue en 502. El panel muestra el mensaje desde el primer pintado, en un párrafo con `min-height: 3rem`, para que la tabla no salte cuando la sonda termina.

| Página | Modo | Best practices | CLS | Performance |
| --- | --- | --- | --- | --- |
| Panel | móvil | 96 → 100 | 0.023 → 0 | 100 → 100 |
| Panel | escritorio | 96 → 100 | 0.059 → 0.008 | 100 → 100 |
| Entrar | móvil | 96 → 100 | 0 → 0 | 100 → 100 |
| Activos | móvil | 96 → 100 | 0.027 → 0.027 | 99 → 99 |

El 0.008 de escritorio es la celda «Sin conexión», que cambia de texto dentro de la tabla. Está por debajo de 0.1. El 0.027 de activos es el pie al pasar del guard al login. No se aplana el layout de las dos pantallas para borrar ese salto.

## 3. Lockup del portal y catálogo de activos

`StableLockup` y `lockupFrame` fijan 280×140 por debajo de 640 px y 400×64 desde ahí. El CSS del portal deja de usar `height: auto`. En `/login` el CLS ya era 0 y sigue en 0. En `/` el CLS del redirect sigue en 0.022 (móvil) y 0.033 (escritorio). Las puntuaciones siguen en 100 / 100 / 100 / 63. El 63 es el `noindex`.

`useAssetCatalog` sustituye el efecto duplicado de `EntryForm` y `ExitForm`. No cambia las rutas que Lighthouse ve sin sesión. Jest del backoffice: 17 passed (los 14 de antes más 3 del catálogo). Jest del portal: 23 passed (los 20 de antes más 3 de la caja del lockup).

## Qué movió más

Quitar el compilador de Tailwind del sitio. Es el único cambio que saca un LCP de la zona «necesita mejora» (2.71 s) y sube dos puntuaciones de Performance (94→98 en el inicio, 98→100 en la solicitud). En el backoffice, la subida de puntuación es Best Practices 96→100, en el panel, el login y activos. El portal no tenía una puntuación honesta que subir: performance, accesibilidad y best practices ya estaban en 100.
