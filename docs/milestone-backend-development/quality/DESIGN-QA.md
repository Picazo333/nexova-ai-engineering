# DESIGN-QA — 021

No hay UI nueva. El lockup 4Geeks × Divinivid no se copia y no hay capturas ni vídeo de pantalla. SIGNAL, en este hito, se aplica al README y a las respuestas de la API.

| ID | Comprobación | Resultado | Motivo |
| --- | --- | --- | --- |
| QA-01 | UI a 390, 768 y 1280 px | NO APLICA | No hay página nueva. |
| QA-02 | Lockup en el footer | NO APLICA | SIGNAL: sin UI, el lockup no aplica. El enunciado tampoco pide marca en la API. |
| QA-03 | Lighthouse | NO APLICA | No hay HTML nuevo que medir. |
| QA-04 | Estados de carga, vacío y error en pantalla | NO APLICA | El vacío y el error están en HTTP: lista `[]` no se usa porque la semilla llena las tablas; sin `DATABASE_URL` el GET responde 503 sin URI en el cuerpo; el 400 de stock trae el texto del briefing. |
| QA-05 | Contraste, tipo Arial y tokens CSS | NO APLICA | No hay CSS nuevo. |
| QA-06 | Claridad del README | PASS | Tabla de rutas, tabla de stock, curl con token y variables vacías en el ejemplo. |
| QA-07 | Errores sin secretos | PASS | El 503 público no incluye la URI. La transcripción no incluye el token ni la contraseña de la base. |
| QA-08 | Hash del lockup `85459232…` | NO APLICA | El archivo no se usa. No se regeneró ningún SVG. |

No se certifica WCAG. No hay puntuación de Lighthouse que reportar.
