# Rúbrica — 025 plan de telemetría

Required = sí cuenta para el cierre. HITL no resta. NO APLICA no es un fallo. Un mock no es PASS.

Cada fila sale de un criterio del enunciado (fases, evaluación o entrega) o de una restricción explícita de esta ejecución. El texto oficial está en `source/OFFICIAL_README.md`.

| ID | Required | Criterio |
| --- | --- | --- |
| R01 | sí | Las cinco métricas del briefing de telemetría de Nexova están en el plan y marcadas como obligatorias. |
| R02 | sí | Entidades, `office`, `product_category`, `currency` y la prohibición de nombres coinciden con ese briefing. |
| R03 | sí | El flujo va del acceso autenticado a la orden de entrada o de salida completada. |
| R04 | sí | Ese flujo tiene al menos 5 puntos de instrumentación. |
| R05 | sí | Esos puntos incluyen el rechazo de editar stock a mano, las validaciones fallidas y el umbral mínimo. |
| R06 | sí | Autenticación: intentos de login, sesiones caducadas y fallos de credenciales. |
| R07 | sí | Rendimiento: tiempo de respuesta de la API y tiempo de carga de pantalla. |
| R08 | sí | Errores de frontend no capturados. |
| R09 | sí | Navegación: secciones que se visitan y flujos que se abandonan. |
| R10 | sí | El catálogo pasa del piso obligatorio. Cubre negocio y técnica con amplitud. |
| R11 | sí | Cada evento tiene hipótesis y decisión. No hay eventos por si acaso. |
| R12 | sí | Cada evento está clasificado como obligatorio o como oportunidad identificada. |
| R13 | sí | El envelope es el mismo en todos: `eventId`, `timestamp` ISO 8601, `sessionId`, `userId`, `event_type`, `schemaVersion`, `requestId`, `properties`. |
| R14 | sí | Cada `event_type` usa la forma `entidad_accion` con verbos estables. |
| R15 | sí | Las cinco métricas obligatorias tienen esquema completo. |
| R16 | sí | Hay al menos 8 eventos además de los obligatorios. |
| R17 | sí | Esos eventos adicionales cubren al menos 3 categorías. |
| R18 | sí | Cada evento tiene allowlist: solo claves permitidas. |
| R19 | sí | Cada propiedad tiene nombre, tipo, si es obligatoria y descripción. |
| R20 | sí | PII y datos sensibles están identificados, con el saneado antes de emitir. |
| R21 | sí | `event-schemas.json` es JSON Schema draft-07 y valida. |
| R22 | sí | El esquema y el Markdown coinciden, evento por evento. |
| R23 | sí | Cada evento es stream o batch. |
| R24 | sí | Esa elección se apoya en la urgencia de la decisión, no en el gusto técnico. |
| R25 | sí | Hay throttle o debounce para los eventos de alta frecuencia. |
| R26 | sí | La sección de exclusiones descarta eventos con una razón. |
| R27 | sí | Lo que no se captura por privacidad o por costo tiene una razón. |
| R28 | sí | El plan nombra módulo, función y condición para que otro lo instrumente sin preguntar. |
| R29 | sí | Esta entrega no añade código de instrumentación. |
| R30 | sí | Los dos ficheros viven en `docs/telemetry/`. |
| R31 | sí | El PR se titula `docs: telemetry design plan` y el cuerpo trae conteos, categorías y la decisión más dura. |
| R32 | sí | Siguen verdes pytest de `services/api`, Jest del portal, Jest del backoffice y Playwright del portal. |
| X01 | extra | Diagrama de stream frente a batch legible para negocio. |
| X02 | extra | Script que valida `event-schemas.json` contra ejemplos y contra el plan. |
| N01 | no | Capturas 390/768/1280. No hay UI nueva. |
| N02 | no | Lockup. No hay UI nueva. |
| N03 | no | Vídeo de recorrido. No hay UI nueva. |
| N04 | no | axe o certificación WCAG. No hay UI nueva. |
| N05 | no | Pipeline o proveedor de telemetría en marcha. Esta entrega es el diseño. Un mock no contaría. |
| H01 | HITL | Compartir el PR con el instructor o enviarlo al LMS. |
