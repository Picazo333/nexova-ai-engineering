# DESIGN-QA — panel Next del puerto 3001

Alcance: solo la UI nueva. El portal y el HTML de la API no se rediseñaron. Orden de autoridad: enunciado > SIGNAL.

## Bloque

| Pregunta | Hecho | Acción |
| --- | --- | --- |
| ¿La API del otro contenedor responde? | `GET /api/stack` llama a `http://services:8000/health`. | Reintentar, o abrir el portal. |
| ¿Hay incidencias en este proceso? | Este proceso no las guarda. | Ir al portal. El filtro estrecha un listado vacío. |

## Estados

| Estado | Dónde | Evidencia |
| --- | --- | --- |
| Carga | Celda «Comprobando la API.» El botón Reintentar queda desactivado. | `evidence/container-loading-390.png`, `container-loading-768.png`, `container-loading-1280.png` |
| Éxito | Tabla con `services:8000` y «En marcha». | `evidence/container-success-*.png` |
| Vacío | «Este proceso no guarda incidencias.» Con texto en el filtro: «Ninguna incidencia coincide con ese texto.» | `evidence/container-empty-*.png` |
| Error | Aviso «No hay conexión con la API.» El filtro escrito se conserva. | `evidence/container-error-*.png` |
| 404 | «No encontramos esa ruta.» | `evidence/container-404-1280.png` |

## Señal

- Tokens y motion importados de `uis/backoffice/tokens/`, sin reescribirlos.
- Arial, Helvetica. Sin fuentes remotas.
- Lockup horizontal 400 px desde 640 px; apilado 280 px por debajo. Hash en `evidence/container-lockup-hashes.txt`.
- `prefers-reduced-motion`: `transition-duration: 0s` en `evidence/container-reduced-motion.txt`.
- Skip link, `lang=es`, un `h1`, etiqueta visible, botón de 44 px, campo de 48 px, `noindex`.
- axe sin serious/critical: `evidence/container-axe.json`.
- Anchos 390, 768 y 1280, sin desbordamiento del documento.
- Vídeo `evidence/container-recorrido.webm`, 6,60 s.

## Lighthouse (build de producción)

| Superficie | LCP mediana / peor | CLS mediana / peor | TBT mediana / peor |
| --- | --- | --- | --- |
| Móvil 390×844, simulate, RTT 150, 1638,4 kbps, CPU ×4 | 1889 / 1890 ms | 0,0024 / 0,0024 | 14 / 14 ms |
| Escritorio, simulate, RTT 40, 10240 kbps, CPU ×1 | 459 / 481 ms | 0,005 / 0,005 | 0 / 0 ms |

`configSettings` comprobado en los seis JSON. INP no sale en laboratorio. Detalle en `/opt/cursor/artifacts/lighthouse/`. Resumen: `evidence/container-lighthouse-summary.json`.

## Motion

Una sola transición de fondo, 180 ms, al llegar el resultado (`data-motion-node`). Propósito: marcar que la comprobación terminó. Se cancela con `prefers-reduced-motion` por el CSS de tokens. No hay puntero ni bucle.
