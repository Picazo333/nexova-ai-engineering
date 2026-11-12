# Cambios del esquema de telemetría

## 1.1.0 — 2026-11-12

Extensión aditiva de la captura 026. No se modifica ni se elimina ningún evento de 1.0.0.

- Nuevo `event_type`: `web_vital_recorded`.
- `schemaVersion` del sobre admite `1.0.0` y `1.1.0`. Este evento exige `1.1.0`. Los demás siguen en `1.0.0`.
- Allowlist: `app`, `path_template`, `metric_name`, `value`, `rating`.
- `metric_name`: `LCP`, `INP`, `CLS`, `FCP`, `TTFB`.
- `rating`: `good`, `needs-improvement`, `poor`.
- `path_template` reutiliza la lista cerrada de `page_load_recorded`. Sin query y sin PII.
- El catálogo de `x-nexova.schemaVersion` pasa de `1.0.0` a `1.1.0`.

## 1.0.0 — 2026-11-12

Catálogo de 025: 19 eventos. Sin cambios en esta línea.
