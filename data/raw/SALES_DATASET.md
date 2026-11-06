# Dataset de ventas — Nexova

Serie mensual oficial usada por el pronóstico. No está generada en este repositorio.

| Campo | Valor |
| --- | --- |
| Archivo | `data/raw/nexova_sales.csv` |
| Filas | 120 meses más cabecera |
| SHA-256 | `e3af15657506fae36a81eec6a9a544a54473bf38f41f2ee1bb066799ff94440a` |
| Origen | `4GeeksAcademy/ai-engineering-syllabus` @ `fd2da034894ba93ba738559280ccde074ab1d953` |
| Ruta de origen | `content/contexts/sales-forecasting/nexova/nexova_sales.csv` |

El monorepo no traía el CSV. Se copió byte a byte desde esa revisión del syllabus, que es la misma que fija el enunciado. Los briefings de columnas y estacionalidad están al lado, también sin reescritura:

- `nexova-BRIEFING.es.md` — SHA-256 `f6aac28d4c27f98c7317aed1d90917dbd62de1d9f020ffba7c912752b76ea83c`
- `nexova-BRIEFING.en.md` — SHA-256 `b5aee74ead883336bc1876a81dfeac60c7f6c2571413df6ca07632d93b9812de`

Columnas, según ese briefing: `month`, `revenue_usd`, `active_contracts`, `avg_contract_value_usd`, `business_line`. El objetivo es `revenue_usd` de `business_line=consolidated`.

No hay copia en `data/process/`. El script recalcula las features al entrenar. El enunciado no pide un segundo dataset.
