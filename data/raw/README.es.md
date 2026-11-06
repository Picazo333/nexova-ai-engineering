# Carpeta `data/raw`

Esta carpeta está pensada para almacenar **datos en bruto** (raw) relacionados con la compañía: dumps, exports, archivos de ejemplo, muestras de eventos, o datasets sin transformar.

- **Propósito principal**: servir como zona de aterrizaje o referencia de datos originales antes de ser procesados por pipelines.
- **Recomendación**: documenta el origen de cada dataset, formato, tamaño esperado, consideraciones de privacidad/PII y cómo se versiona (idealmente evitando subir datos sensibles al repositorio).

## Datasets

| Archivo | Qué es |
| --- | --- |
| `nexova_sales.csv` | Ingreso mensual consolidado oficial, de 2016-01 a 2025-12. No se regenera. Procedencia y SHA-256: [`SALES_DATASET.md`](./SALES_DATASET.md). |
| `nexova-BRIEFING.en.md` / `nexova-BRIEFING.es.md` | Significado de columnas y estacionalidad, copiados de la revisión del syllabus que cita la nota de procedencia. |
