# `agents/tools` folder

This folder groups **reusable tools** that agents in the monorepo can use (for example: connectors to internal APIs, database wrappers, scraping utilities, validators, service clients, etc.).

- **Main purpose**: avoid duplicated code across agents and standardize how agents interact with company systems.
- **Recommendation**: document each tool you add (what it does, inputs/outputs, permissions/security, limits, and usage examples) and link to it from the agents that use it.

## Ticket lookup

Code: `services/api/app/agent/tools/tickets.py`. The support agent calls it from the `lookup_ticket` node.

- **What it does**: reads one incident by id, or a list filtered by `status`, `origin`, `branch`, or `category`.
- **Input**: `ticket_id` or those filters. The fields are the public fields of `GET /api/incidents`.
- **Output**: `outcome` (`found`, `not_found`, `empty`, `timeout`, `error`, `unauthorized`, `invalid`), `tickets` (the public record: id, title, description, category, status, origin, branch, created_at, updated_at), and `message`.
- **Permission**: read-only. The module does not call `create_incident` or `update_status`. The HTTP transport sends `GET` only.
- **Transport**: in-process through `incident_store` unless `INCIDENT_API_BASE_URL` is set. The incident HTTP API requires a bearer token. The in-process reader checks that token. `INCIDENT_API_TOKEN` is only for the HTTP transport and is empty in `.env.example`.
- **Limit**: `TICKET_TOOL_TIMEOUT_SECONDS` is 4. On timeout, error, or a missing ticket the agent says it could not confirm the status. It does not invent one.
- **Example**: `What is the status of ticket <id>?` after that id exists in the incident manager.

> _Spanish version: [README.es.md](./README.es.md)._
