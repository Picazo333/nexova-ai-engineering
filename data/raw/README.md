# `data/raw` folder

This folder is intended for **raw data** related to the company: dumps, exports, sample files, event samples, or untransformed datasets.

- **Main purpose**: serve as a landing zone or reference for original data before pipelines process it.
- **Recommendation**: document each dataset’s origin, format, expected size, privacy/PII considerations, and how it is versioned (ideally avoiding sensitive data in the repository).

## Datasets

| File | What it is |
| --- | --- |
| `nexova_sales.csv` | Official monthly consolidated revenue, 2016-01 through 2025-12. Do not regenerate it. Provenance and SHA-256: [`SALES_DATASET.md`](./SALES_DATASET.md). |
| `nexova-BRIEFING.en.md` / `nexova-BRIEFING.es.md` | Column meanings and the seasonality pattern, copied from the syllabus revision named in the provenance note. |

> _Spanish version: [README.es.md](./README.es.md)._
