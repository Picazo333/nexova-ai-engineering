# Rúbrica — 024 caché

Required = sí cuenta para el cierre. HITL no resta. NO APLICA no es un fallo.

| ID | Required | Criterio |
| --- | --- | --- |
| R01 | sí | Al menos dos componentes o rutas identificados para lazy loading, con el porqué. |
| R02 | sí | Esos componentes usan `next/dynamic` o `React.lazy`. |
| R03 | sí | Al menos un `useMemo` sobre un cálculo no trivial, con dependencias definidas. |
| R04 | sí | Ese `useMemo` está implementado. No cubre una suma trivial. |
| R05 | sí | Todos los endpoints listados con coste, frecuencia y cadencia de cambio. |
| R06 | sí | Al menos dos endpoints cumplen coste + frecuencia + estabilidad. |
| R07 | sí | Esos endpoints tienen caché con TTL. |
| R08 | sí | Una escritura de los datos subyacentes vacía o marca vieja la caché. |
| R09 | sí | Ningún dato privado o de sesión vive en una clave compartida. |
| R10 | sí | `CACHING_REPORT.md` tiene decisiones de frontend, de backend, el intercambio y lo que no se cacheó. |
| R11 | sí | Las decisiones nombran rutas, tiempos y TTL. No basta «está lento». |
| R12 | sí | Hay un intercambio explícito entre frescura y rendimiento. |
| R13 | sí | Hay números de antes y de después, y el volumen de filas antes y después de la carga. |
| R14 | sí | Siguen verdes API con Postgres, raíz, Playwright, Jest del portal y Jest del backoffice. |
| X01 | extra | Indicador visible de lista servida desde caché. |
| X02 | extra | Tests de TTL, de expiración y de clave privada no compartida. |
| N01 | no | Redis. El enunciado lo deja opcional. |
| H01 | HITL | Compartir el PR con el instructor o enviarlo al LMS. |
