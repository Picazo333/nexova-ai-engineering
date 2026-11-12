# 026 — ai-eng-telemetry-capture

## Estado de preparación
- Repositorio destino: NO CREADO / NO NUEVA RAMA en esta preparación (solo fuentes y notas)
- Tipo: frontend TelemetryService + stub FastAPI /telemetry/events
- Alcance SIGNAL: completo en UIs instrumentadas; parcial API stub
- Independiente de la cadena serial Nexova 011→012→013/014→021…: **no**
- Fuente oficial: sí
- Documentos: source/OFFICIAL_README.md, source/OFFICIAL_README.es.md, source/PROVENANCE.json, source/ASSETS.md

## Base oficial / template
https://github.com/4GeeksAcademy/ai-engineering-company-project-monorepo — is_template=true. Extender fork Nexova; requiere docs/telemetry de 025.
Conservar licencias/procedencia del código base, sin inventar colaboradores ni firmas de autoría.
Si la fuente exige monorepo existente, un repo separado no elimina esa obligación.

## Keys o servicios externos necesarios
Ninguna LLM. NEXT_PUBLIC_TELEMETRY_ENDPOINT (URL local). Supabase aún no obligatorio (stub).
Nunca buscar/imprimir credenciales; no usar FOURGEEKS_API_TOKEN para proveedores externos.
Si falta key/servicio real: mock explícito solo para pruebas; criterios de integración real → BLOCKED/NO EJECUTADO, no PASS por mock.
No crear cuentas de pago ni acciones externas sin autorización específica de Miguel.

## Extras propuestos (subordinados a rúbrica)
- Visible: Indicador discreto de eventos encolados/enviados en backoffice (dev-only).
- Técnico: Cola/retry del TelemetryService + tests de schema contra event-schemas.json.

## Restricciones / bloqueos de lanzamiento
Depende de 025 (telemetry-plan + event-schemas.json). No instrumentar antes del stub. Vocabulario BRIEFING.

## Ruta de entrega
(b) rama + PR sobre Picazo333/nexova-ai-engineering — Nexova — feature/telemetry-capture
Sin merge automático. Sin envío al LMS. Autoría/envío LMS solo Miguel.

## Dependencias
025; UIs backoffice/sitio existentes.

## Handoff y aceptación
Aplicar /workspace/ejecucion/SIGNAL_BRIEF.md y SIGNAL_PACKAGE.zip según alcance.
UI: evidencia capturas 390/768/1280 + video corto real, loading/empty/error, AA y reduced-motion. Sin UI: evidencias CLI/API/docs/notebook, lockup no aplica.
Extraer TODOS los criterios del enunciado; RUBRIC_JUSTIFICATION.md con PASS/FAIL y vínculo de evidencia,
TELEMETRY con tokens reales o null si no disponibles, tiempo real, EVAL→REPAIR, fallos y comparación estimación.
EVIDENCE_MANIFEST.yaml, EXCELLENCE_REVIEW.md y DESIGN-QA.md; límites explícitos y revisión por Orquestador antes de READY_TO_SUBMIT.
No lanzar agentes desde esta preparación; no merge; no LMS; no inventar autoría.

