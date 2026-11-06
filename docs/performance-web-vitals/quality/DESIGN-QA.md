# DESIGN-QA — 023

El cambio visible del sitio es ninguno: el CSS compilado pinta igual. El del portal es la caja fija del lockup, con la misma proporción que el SVG. El del backoffice es el texto de la sonda, que ya existía como error y ahora ocupa su sitio desde el primer pintado, y el icono.

| Comprobación | Resultado |
| --- | --- |
| Inicio, solicitud y 404 a 390, 768 y 1280, pantalla completa, antes y después | Diferencia media de píxel 0 en las nueve parejas. |
| Tipografía del sitio | Sigue Inter / Newsreader locales. El cómputo de `font-family` no cambió. |
| Portal y backoffice | Arial, Helvetica, tokens y lockup que ya estaban. Los SVG no están en el diff. |
| `prefers-reduced-motion` | No se tocó `MotionPref` ni `motion.css`. Playwright `reduced motion deja el indicador de carga quieto` pasó. |
| Lockup | `StableLockup` usa los mismos `src`, el mismo `alt` («4Geeks por Divinivid») y las mismas medidas 280×140 / 400×64. |
| Contraste y estados | No se cambian colores. El aviso de la sonda sigue en `.alert` cuando hay error. |
| SEO del sitio público | Sigue en 100. No se añadieron meta nuevas. |

No hay un rediseño. La galería de la auditoría es una página aparte en `audit/index.html`.
