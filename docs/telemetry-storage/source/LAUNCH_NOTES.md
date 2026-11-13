# 027 — ai-eng-telemetry-storage

## Estado de preparación
- Repositorio destino: NO CREADO / NO NUEVA RAMA en esta preparación (solo fuentes y notas)
- Tipo: tabla Supabase + endpoint real bulk insert telemetría
- Alcance SIGNAL: parcial API/docs; FE no se toca
- Independiente de la cadena serial Nexova 011→012→013/014→021…: **no**
- Fuente oficial: sí
- Documentos: source/OFFICIAL_README.md, source/OFFICIAL_README.es.md, source/PROVENANCE.json, source/ASSETS.md

## Base oficial / template
Monorepo is_template=true; trabajar en Nexova.
Conservar licencias/procedencia del código base, sin inventar colaboradores ni firmas de autoría.
Si la fuente exige monorepo existente, un repo separado no elimina esa obligación.

## Keys o servicios externos necesarios
Supabase/Postgres (DATABASE_URL). Sin LLM.
Nunca buscar/imprimir credenciales; no usar FOURGEEKS_API_TOKEN para proveedores externos.
Si falta key/servicio real: mock explícito solo para pruebas; criterios de integración real → BLOCKED/NO EJECUTADO, no PASS por mock.
No crear cuentas de pago ni acciones externas sin autorización específica de Miguel.

## Extras propuestos (subordinados a rúbrica)
- Visible: Log/admin de filas insertadas y rechazadas por validación parcial.
- Técnico: Bulk insert + validación per-event; test de rechazo parcial sin tumbar el batch.

## Restricciones / bloqueos de lanzamiento
Depende de 026 (mismo endpoint). Tags/dimensiones del plan 025. Criterios DB reales BLOCKED sin Supabase.

## Ruta de entrega
(b) rama + PR sobre Picazo333/nexova-ai-engineering — Nexova — feature/telemetry-storage
Sin merge automático. Sin envío al LMS. Autoría/envío LMS solo Miguel.

## Dependencias
025, 026.

## Handoff y aceptación
Aplicar /workspace/ejecucion/SIGNAL_BRIEF.md y SIGNAL_PACKAGE.zip según alcance.
UI: evidencia capturas 390/768/1280 + video corto real, loading/empty/error, AA y reduced-motion. Sin UI: evidencias CLI/API/docs/notebook, lockup no aplica.
Extraer TODOS los criterios del enunciado; RUBRIC_JUSTIFICATION.md con PASS/FAIL y vínculo de evidencia,
TELEMETRY con tokens reales o null si no disponibles, tiempo real, EVAL→REPAIR, fallos y comparación estimación.
EVIDENCE_MANIFEST.yaml, EXCELLENCE_REVIEW.md y DESIGN-QA.md; límites explícitos y revisión por Orquestador antes de READY_TO_SUBMIT.
No lanzar agentes desde esta preparación; no merge; no LMS; no inventar autoría.

