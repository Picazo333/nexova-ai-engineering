# DESIGN-QA — inventario del backoffice

Herramienta interna. Sin hero comercial. Título, filtro, tabla o formulario, y pie con el lockup.

Autoridad: el enunciado pide claridad operativa. El `h1` de estas pantallas usa el tamaño de título de panel ya existente (1,5 rem), no el display de una landing.

| ID | Comprobación | Ancho | Resultado |
| --- | --- | --- | --- |
| QA-01 | Activos con semilla, NXV-IT-001 = 12 Saludable, NXV-IT-002 Bajo, NXV-PER-002 Sin stock | 390, 768, 1280 | PASS. `products-*.png` |
| QA-02 | Aviso de cantidad por encima del stock | 390, 768, 1280 | PASS. `outbound-warning-*.png` |
| QA-03 | 400 de la API junto a la cantidad | 390, 768, 1280 | PASS. `outbound-400-*.png` |
| QA-04 | Confirmación de entrada y formulario vacío | 390, 768, 1280 | PASS. `inbound-confirm-*.png` |
| QA-05 | Historial con entrada y salida | 390, 768, 1280 | PASS. `orders-*.png` |
| QA-06 | Sin sesión, redirect a login | 390, 768, 1280 | PASS. `login-redirect-*.png` |
| QA-07 | Cargando activos | 390, 768, 1280 | PASS. `products-loading-*.png` |
| QA-08 | Vacío real (esquema sin semilla) | 390, 768, 1280 | PASS. `products-empty-*.png`, `orders-empty-*.png` |
| QA-09 | Error 503 real, con reintento | 390, 768, 1280 | PASS. `products-error-*.png` |
| QA-10 | `data-motion=reduced` | 390 y 1280 | PASS. `products-reduced-*.png` y `recorrido-reduced.webm` |
| QA-11 | Overflow del documento | los tres | 0 px en la captura |
| QA-12 | Tabla con scroll local y nombre accesible | 390 | PASS. La tabla mínima es 44 rem dentro de la región |
| QA-13 | axe serious/critical | 1280 y 390 | 0 |
| QA-14 | Lockup | &lt;640 apilado 280 px; ≥640 horizontal 400 px | PASS. Hash horizontal del encargo |
| QA-15 | Contraste de badges | texto blanco sobre success, warning, danger, info y action | Todos ≥ 5,86:1 |
| QA-16 | Lighthouse producción | 390×844 y escritorio, 3 corridas | PASS. Peor LCP móvil 1970 ms. Peor CLS contado 0,053 (home escritorio). TBT ≤ 17,5 ms |
| QA-17 | Teclado | foco 2 px, offset 3 px, controles ≥ 44 px, campos ≥ 48 px | Tokens y CSS. axe no marcó target-size |
| QA-18 | Motion | fondo de confirmación 180 ms, easing del token, cancelado con reduced-motion | PASS |

El video principal dura 7,8 s y no usa un botón Repetir: recorre el listado, el stock y el 400.

No se certificó WCAG por la puntuación de una herramienta. No hubo hallazgos serious ni critical de axe en las vistas medidas.
