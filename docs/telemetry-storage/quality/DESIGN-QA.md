# DESIGN-QA — 027

Esta entrega no cambia UI. El enunciado dice que el frontend no se toca. SIGNAL dice que, en CLI/API/docs, el lockup no aplica y no se añade una pantalla para mostrar marca.

| Comprobación | Resultado |
| --- | --- |
| Capturas 390, 768 y 1280 | NO APLICA. No hay pantalla nueva. |
| Vídeo | NO APLICA. No hay recorrido de UI. |
| Carga, vacío y error de una vista | NO APLICA. Los estados de esta entrega son HTTP: 200 con conteos, 422 si el sobre no es un arreglo, 503 si hay eventos válidos y no hay base. |
| Contraste, foco, 44 px | NO APLICA. No se pinta un control. |
| `prefers-reduced-motion` | NO APLICA. No hay animación nueva. |
| axe | NO APLICA. No hay documento HTML nuevo. |
| Lockup | NO APLICA. No hay footer que editar. El del backoffice queda como estaba. |
| SEO | NO APLICA. No hay landing. La API no gana sitemap ni schema. |
| Copy | El 422 dice «El lote no tiene el formato de telemetría.» o «El lote supera 500 eventos.» El 503 usa la frase de catálogo y no repite la URI de la base. El log no imprime el evento rechazado. |

`git diff 6cc066f -- uis` no tiene archivos. `evidence/uis-diff.txt`.
