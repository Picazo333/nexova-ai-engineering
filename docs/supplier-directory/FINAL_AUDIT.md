# Auditoría final — 011 Directorio de proveedores

Estado: **PENDIENTE_REVISION_ORQUESTADOR**.

44 criterios de `RUBRIC.md`: **44 PASS**, 0 FAIL, 0 BLOCKED, 0 omitidos.

El briefing no faltaba. No está dentro del monorepo (se buscó en `BRIEFING.md`, `CONTEXT.md`, el briefing de incidencias y `data/`). Está en el syllabus, en `content/contexts/supplier-directory/nexova-BRIEFING`, que es la ruta que indica el enunciado. Se copió a `scripts/nexova-supplier-BRIEFING.es.md` y `.en.md`. Los datos del seeder son esos 15 contratos.

## Qué queda cerrado

- API FastAPI + TinyDB + Pydantic en el mismo proceso que las incidencias.
- `uv run seed` idempotente, con el recuento en consola, y seeder al arrancar.
- Página `/proveedores` en el backoffice, con filtros, alta, tarifa, estado, carga, vacío y error.
- SIGNAL: tokens, lockup verificado, capturas 390/768/1280, vídeo de 6,48 s, Lighthouse móvil y escritorio.
- Extras E01 y E02 con evidencia.
- 35 tests pytest, incluidos los de incidencias.

## Límites

- No hay clave externa y no hace falta. Nada queda BLOCKED por un servicio de pago.
- No se hizo merge. La base del PR es `feature/incidents-analysis` (PR #9). El orden de merge es ese PR primero y este después.
- `updated_at` de un proveedor ya guardado no vuelve al valor del seeder si alguien lo editó: el seeder no pisa filas existentes.
- Las fechas de renovación del briefing están vencidas a 2026-11-06. La UI lo dice. La regla de 60 días está cubierta por un test con fecha futura.
- INP no lo mide Lighthouse en este laboratorio. La cifra de bloqueo entregada es TBT.
- Esta auditoría no es la revisión del orquestador ni un envío al LMS.
