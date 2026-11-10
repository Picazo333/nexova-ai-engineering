# Justificación de la rúbrica — 016

Re-ejecución del 10-nov-2026 (CDMX) sobre `6d0c5789b47fc28c5371970f0ccbed3b677b567a` (punta de PR #17). Logs en `evidence/rerun-2026-11-10/`. `UNVERIFIED` significa que ninguna prueba de esta corrida lo demuestra; no es un PASS. Esto no es la auditoría independiente.

| ID | Estado | Evidencia | Nota |
| --- | --- | --- | --- |
| C01 | PASS | evidence/rerun-2026-11-10/02-pytest.txt (107 passed); test_create_list_detail_and_summary; test_validation_names_the_field_in_spanish |  |
| C02 | PASS | evidence/rerun-2026-11-10/20-seed2x-summary.txt (by_origin.customer=96) |  |
| C03 | PASS | evidence/rerun-2026-11-10/20-seed2x-summary.txt (status/category = BRIEFING); test_official_csv_transforms_to_the_briefing_totals |  |
| C04 | PASS | evidence/rerun-2026-11-10/20-seed2x-summary.txt (Rechazadas: 4, listadas por línea) |  |
| C05 | PASS | evidence/rerun-2026-11-10/20-seed2x-summary.txt (2ª corrida: Insertadas 0, Ya estaban 96; listado=96) |  |
| C06 | PASS | evidence/rerun-2026-11-10/20-seed2x-summary.txt (open27/resolved56/discarded13; technical49/process35/client12; total 96) |  |
| C07 | PASS | evidence/rerun-2026-11-10/02-pytest.txt; test_create_list_detail_and_summary; test_status_lifecycle_and_filters |  |
| C08 | PASS | evidence/rerun-2026-11-10/02-pytest.txt; test_validation_names_the_field_in_spanish |  |
| C09 | PASS | evidence/rerun-2026-11-10/02-pytest.txt; test_internal_error_does_not_return_the_exception |  |
| C10 | PASS | evidence/rerun-2026-11-10/02-pytest.txt; test_status_lifecycle_and_filters (400) |  |
| C11 | PASS | evidence/rerun-2026-11-10/20-seed2x-summary.txt (summary BD vacía: HTTP 200, todo 0; listado []); evidence/rerun-2026-11-10/40-patch-test-summary-empty.txt (parche) |  |
| C12 | PASS | evidence/rerun-2026-11-10/13-playwright.txt incidents-manager.spec (envío vacío → 'El título es obligatorio.'); uis/backoffice/js/incidents-manager.js preventDefault + mensajes |  |
| C13 | PASS | evidence/rerun-2026-11-10/13-playwright.txt (data-highlight=1, etiquetas BRIEFING) |  |
| C14 | UNVERIFIED | — | Ninguna prueba de esta corrida afirma el indicador de carga ni el botón deshabilitado durante la petición. |
| C15 | UNVERIFIED | — | La e2e cubre el fallo de red del resumen, no un error 4xx/5xx de la API mostrado al usuario. |
| C16 | UNVERIFIED | — | No hay aserción de estados 'cargando' y 'vacío' del listado en esta corrida. |
| C17 | UNVERIFIED | — | No hay aserción de la reversión visual del estado tras un PATCH fallido. |
| C18 | PASS | evidence/rerun-2026-11-10/13-playwright.txt (resumen abortado → mensaje + 'Reintentar el resumen'; listado visible) |  |
| C19 | PASS | evidence/rerun-2026-11-10/02-pytest.txt (test_incident_seed importa nexova_incidents); evidence/rerun-2026-11-10/50-static-checks.txt |  |
| C20 | UNVERIFIED | evidence/rerun-2026-11-10/50-static-checks.txt | UI renderizada desde services/api/app/incident_pages.py; decisión del auditor. |
