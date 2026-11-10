# Rúbrica — 016 Gestor de incidencias centralizado

Fuente: `content/projects/ai-eng-centralized-incident-manager/README.es.md` del syllabus oficial en `fd2da034894ba93ba738559280ccde074ab1d953`, sección «Qué evaluaremos». Todos los criterios son required. sha256 del texto: `c9d156256b34db52b3f1999907cfd29c063ddf6a278fdf05730fa854b2553c01`.

Contexto: `content/contexts/centralized-incident-manager/nexova-BRIEFING.es.md` (idéntico a `scripts/nexova-incident-manager-BRIEFING.es.md`).

| ID | Required | Criterio |
| --- | --- | --- |
| C01 | sí | Modelo con todos los campos requeridos y restricciones de integridad. |
| C02 | sí | Seed carga histórico con origin='customer'. |
| C03 | sí | Seed aplica transformaciones CSV→modelo del BRIEFING. |
| C04 | sí | Registros inválidos no se insertan y se reportan en consola. |
| C05 | sí | Seed idempotente. |
| C06 | sí | Tras el seed, totales por status/category en /summary = valores del BRIEFING (96 válidos). |
| C07 | sí | Endpoints con códigos HTTP correctos en casos felices y de error. |
| C08 | sí | Errores de validación identifican el campo en el JSON. |
| C09 | sí | Ningún endpoint expone stack trace. |
| C10 | sí | Transiciones inválidas → 400. |
| C11 | sí | /summary correcto sin incidencias. |
| C12 | sí | Formulario valida obligatorios en cliente antes de enviar. |
| C13 | sí | origin=branch resalta branch y desplegable con etiquetas BRIEFING. |
| C14 | sí | Estados de carga visibles; submit deshabilitado durante la petición. |
| C15 | sí | Errores API en lenguaje comprensible. |
| C16 | sí | Listado gestiona cargando/vacío/con datos. |
| C17 | sí | Actualización de estado revierte visualmente si falla. |
| C18 | sí | Panel de resumen no rompe la página si falla. |
| C19 | sí | Validación del proyecto anterior extraída a packages/shared/ y reutilizada por script y API. |
| C20 | sí | Código organizado según scripts/, services/, uis/, packages/shared/. |
