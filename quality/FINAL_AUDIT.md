# Auditoría final — 015 ai-eng-company-monorepo-container

Estado: **PENDIENTE_REVISION_ORQUESTADOR**. No es READY_TO_SUBMIT. No hubo merge.

PR: https://github.com/Picazo333/nexova-ai-engineering/pull/22 contra `feature/user-authentication-restore`.

## Resultado

30/30 criterios que cuentan: PASS.

No cuentan y quedan pendientes:

| ID | Estado | Qué falta |
| --- | --- | --- |
| P01 | BLOCKED_HITL | Contenedores en marcha en el VPS. No hay SSH ni autorización. |
| D02 | BLOCKED_HITL | Evidencia de ese VPS (SSH o URL). No se inventa la URL. |
| D03 | HITL_ENVIO_MIGUEL | Compartir el PR con el tech lead o el instructor. |
| D04 | HITL_MIGUEL | Merge a `main` cuando el PR esté aprobado. |
| H01 | HITL_MIGUEL | Confirmar el acceso SSH y autorizar el despliegue. |
| U09 | NO_APLICA | SEO de landing pública. El panel es interno. |

Extras X01 y X02: PASS. Están en `quality/EXCELLENCE_REVIEW.md`.

## Checklist de Miguel

1. Revisar el PR contra `feature/user-authentication-restore`. No hay merge automático.
2. Si el VPS debe demostrarse: seguir `docs/container/RUNBOOK.md` en el servidor, con un `.env` que no sale del servidor. Hasta entonces P01 y D02 siguen BLOCKED_HITL.
3. Entregar al instructor o al LMS, si toca. D03.
4. Merge a `main` solo después de aprobar. D04.

## Qué se volvió a ejecutar

- `services/api`: `uv run pytest` → 157 passed. La línea de partida era 156. La prueba nueva es `tests/test_health.py`.
- La misma suite dentro del contenedor `services` → 157 passed en 7,03 s.
- Raíz: `uv run python -m pytest tests packages/incident_analysis/tests` → 64 passed, 1 skipped. El skip ya existía (generación en vivo). Las 7 nuevas son el contrato de Compose.
- Portal: `tsc --noEmit`, Jest 20 passed, Playwright 14 passed.
- `docker compose up -d --wait` con los tres servicios. UI y API `healthy`. `wget http://services:8000/health` desde el contenedor de interfaces respondió `{"status":"ok"}`.
- Recarga en caliente de la UI y de la API sin reconstruir.
- Capturas y axe contra el `next start` de producción del panel.
- Lighthouse 6 corridas. `configSettings` comprobado.

## Límites

- No se abrió SSH. No hay URL de producción.
- El `.env` local se generó en la máquina y no se versiona. El secreto no está en el informe.
- En esta VM el reenvío entre contenedores no pasaba por las reglas legacy de iptables. Se dejó `net.bridge.bridge-nf-call-iptables=0` en el host de la verificación. Un Docker de escritorio con un solo backend de iptables no necesita ese ajuste. No forma parte del repositorio.
- El primer `typescript.js` del backoffice dentro de la imagen salió truncado. El Dockerfile ahora corta el build si el fichero pesa menos de 8 MB, y `start.sh` copia los módulos de la imagen cuando el montaje está corto.
