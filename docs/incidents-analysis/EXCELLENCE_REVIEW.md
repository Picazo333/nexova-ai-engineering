# Excellence review

Línea base: los criterios required del enunciado están en PASS, salvo R25 (merge), bloqueado por la orden de no merge. Esta revisión no sustituye ningún requisito.

## Visible — IMPLEMENT

Detalle de cada registro inválido (línea del CSV, fila, ticket y regla) y vista previa del `results.csv` antes de descargarlo.

Por qué: el briefing pide no ignorar los inválidos y Roberto pega una métrica por fila. Ver la fila y el fichero en la misma pantalla evita descargar a ciegas.

Evidencia: tablas en `services/api/app/pages.py` (`_details`, `_preview`). Capturas `ui-success-1280.png` y `ui-desktop-results.png`. El vídeo muestra NXV-000017 con «Falta client_company» y ningún correo.

No contradice el enunciado: no añade campos ni cambia las cifras.

## Técnico — IMPLEMENT

Motor único con tests del CSV oficial, de cada regla, de que el correo no sale, de la API y de los hashes SIGNAL. Workflow `.github/workflows/incidents-analysis.yml`.

Evidencia: `python -m pytest -q` → 24 passed sobre el commit `d7952db5a37fffeec3f98dedf9a8ec20da5cb95b`.

## Otras candidatas

| Candidata | Decisión | Motivo |
| --- | --- | --- |
| Gráfico de barras de categorías | REJECT | Librería o dibujo extra para unos conteos que la tabla ya da. El enunciado no lo pide. |
| Base de datos del histórico | DEFER | El enunciado pide el último análisis. Un fichero local de resumen basta y no guarda el CSV. |
| Autenticación de empleados | DEFER | No está en el enunciado. La propuesta de arquitectura sin merge habla de `require_empleado`; imponerla aquí cerraría el flujo académico. |
| Reutilizar el tema Tailwind del sitio público | REJECT | El enunciado no lo exige. SIGNAL pide no mezclar otro tema. El sitio público sigue intacto. |

## Lockup

El backoffice tiene UI, así que el lockup va en el pie. El sitio público no se toca. El crédito dice que no es una asociación oficial, como pide `brand/README.md`.
