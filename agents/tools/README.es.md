# Carpeta `agents/tools`

Esta carpeta agrupa **herramientas reutilizables** que pueden usar los agentes del monorepo (por ejemplo: conectores a APIs internas, wrappers de bases de datos, utilidades de scraping, validadores, clientes de servicios, etc.).

- **Propósito principal**: evitar duplicación de código entre agentes y estandarizar cómo los agentes interactúan con sistemas de la compañía.
- **Recomendación**: documenta cada herramienta que añadas (qué hace, entradas/salidas, permisos/seguridad, límites y ejemplos de uso) y enlázala desde los agentes que la consumen.

## Consulta de tickets

Código: `services/api/app/agent/tools/tickets.py`. El agente de soporte la llama desde el nodo `lookup_ticket`.

- **Qué hace**: lee una incidencia por id, o una lista filtrada por `status`, `origin`, `branch` o `category`.
- **Entrada**: `ticket_id` o esos filtros. Los campos son los públicos de `GET /api/incidents`.
- **Salida**: `outcome` (`found`, `not_found`, `empty`, `timeout`, `error`, `unauthorized`, `invalid`), `tickets` (el registro público: id, title, description, category, status, origin, branch, created_at, updated_at) y `message`.
- **Permiso**: solo lectura. El módulo no llama a `create_incident` ni a `update_status`. El transporte HTTP solo envía `GET`.
- **Transporte**: en proceso, por `incident_store`, salvo que `INCIDENT_API_BASE_URL` tenga valor. La API HTTP de incidentes pide un bearer token. El lector en proceso comprueba ese token. `INCIDENT_API_TOKEN` solo vale para el transporte HTTP y está vacío en `.env.example`.
- **Límite**: `TICKET_TOOL_TIMEOUT_SECONDS` es 4. Ante timeout, error o ticket ausente, el agente dice que no pudo confirmar el estado. No lo inventa.
- **Ejemplo**: `What is the status of ticket <id>?` cuando ese id ya existe en el gestor de incidentes.
