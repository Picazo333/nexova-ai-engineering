# DESIGN-QA — 024

La UI tocada es el historial del backoffice (resumen, nota de caché) y la carga diferida de los dos formularios y del resultado de análisis del portal. El resto de la pantalla ya estaba.

| Comprobación | Resultado |
| --- | --- |
| Historial con HIT a 390, 768 y 1280 | `evidence/orders-hit-390.png`, `orders-hit-768.png`, `orders-hit-1280.png`. La nota de caché se lee en los tres. El lockup horizontal cabe a 1280. A 390 se usa el apilado, por encima de 280 px de ancho en la captura. |
| Carga, vacío y error | `orders-loading-390.png` («Cargando el historial…»). `orders-empty-768.png` (sin filas, con enlace a registrar una entrada). `orders-error-1280.png` (reintento). El vacío y el error se forzaron en el navegador contra `GET /inventory/orders`; el HIT es la API real con la semilla. |
| Formulario de entrada a 390 | `entry-form-390.png`. El chunk diferido llega y el botón «Registrar entrada de activos» está visible. |
| `prefers-reduced-motion` | `orders-reduced-1280.png`. La nota y la tabla quedan en el estado final. No se añadió animación nueva. `tokens.css` ya anula animaciones con `prefers-reduced-motion: reduce`. |
| Teclado y nombres | La tabla sigue en un `region` con nombre. La nota de caché es `role="status"`. El filtro de oficina conserva su etiqueta. |
| axe | `evidence/axe.json`. Historial con HIT: 0 violaciones. Formulario de salida: 0 violaciones. No se certifica WCAG por ese cero. |
| Contraste | La nota usa `.note` (`--color-muted` #505E70 sobre superficie blanca), el mismo par que el resto del backoffice. Los tags Entrada y Salida no cambian. |
| Tipografía | Arial, Helvetica, sans-serif. Sin fuentes remotas nuevas. |
| Vídeo | `recorrido-historial.webm`, 7,44 s: historial, recarga con la nota de caché, desplazamiento de la tabla y apertura del formulario de entrada. |
| SEO | El backoffice sigue con `noindex`. No se añade sitemap ni schema. |

No hay hero, ni métricas de negocio, ni testimonios. El resumen del historial sale de las filas que devolvió la API.
