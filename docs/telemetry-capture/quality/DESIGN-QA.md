# DESIGN-QA — 026

La UI nueva es el indicador de telemetría en la cabecera del backoffice y el campo opcional de costo unitario en la entrada. El resto de la pantalla ya estaba. El indicador solo se monta con `next dev` (`NODE_ENV=development`).

| Comprobación | Resultado |
| --- | --- |
| Login a 390, 768 y 1280 | `evidence/login-390.png`, `login-768.png`, `login-1280.png`. El indicador se lee en los tres. A 390 el lockup es el apilado. Desde 640 px el CSS enseña el horizontal de 400 px. |
| Entrada registrada a 390, 768 y 1280 | `evidence/inbound-sent-390.png`, `inbound-sent-768.png`, `inbound-sent-1280.png`. La orden es una respuesta real de `POST /inventory/orders/inbound`. El indicador pasa a enviados. |
| Carga, vacío y error | `products-loading-390.png` («Cargando activos…»). `products-empty-768.png` (sin filas, con enlace a registrar una entrada). `products-error-1280.png` (reintento). El vacío y el error se forzaron en el navegador sobre `GET /inventory/products`. No sustituyen el 200 del stub. |
| `prefers-reduced-motion` | `products-reduced-1280.png`. No hay animación nueva. El indicador queda en texto. `tokens.css` ya anula animaciones con `prefers-reduced-motion: reduce`. |
| Contraste | Tinta `#18202B` sobre blanco: 16,40:1. Muted `#505E70` sobre blanco, el texto del indicador: 6,61:1. Texto de acción `#FFFFFF` sobre `#B53A17`: 5,86:1. Peligro `#A32A26` sobre blanco: 7,20:1. Éxito `#236344` sobre blanco: 7,14:1. Todos por encima de 4,5:1. |
| axe | `evidence/axe-login.json` y `axe-products.json`. 0 violaciones en las dos pasadas. No se certifica WCAG por ese cero. |
| Tipografía | Arial, Helvetica, sans-serif. Sin fuentes remotas nuevas. |
| Foco y objetivo | El botón de reintento del indicador hereda el botón del backoffice: alto mínimo 44 px, borde 1 px, foco `outline` 2 px con offset 3 px de `tokens.css`. En el recorrido normal la cola se vacía sola y el botón no aparece. |
| Vídeo | `recorrido-entrada.webm`, 9,0 s. Recorre el login, la entrada y el registro de la orden. |
| SEO | El backoffice sigue con `noindex` y `X-Robots-Tag`. No se añade sitemap ni schema. |
| Peso | `next build` del backoffice informa 113 kB de First Load JS en las rutas de inventario, sin comprimir. Está por debajo del tope de 170 KiB gzip. No se midió LCP de laboratorio en esta pasada. |

No hay hero, ni métricas de negocio inventadas, ni testimonios. El número de eventos del indicador sale de la cola real. El costo que se ve en el formulario es el que escribe quien opera.
