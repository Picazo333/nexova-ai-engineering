# Rúbrica — 011 Directorio de proveedores (Nexova)

Fuente: `OFFICIAL_README.md` / `OFFICIAL_README.es.md` del proyecto `ai-eng-supplier-directory`, más el briefing de Nexova en `content/contexts/supplier-directory` y las reglas de fase 2 (SIGNAL, extras, Lighthouse). El enunciado manda sobre SIGNAL.

La página vive en `uis/backoffice` (`/proveedores`) y no en `uis/application/app/suppliers/`. El mismo enunciado pide trabajar en `/uis/backoffice` y evaluar esa carpeta; `/suppliers` queda reservado a la API. El proyecto 009 ya sirve el backoffice desde `services/api`.

| ID | Required | Criterio |
| --- | --- | --- |
| R01 | sí | El modelo Pydantic tiene los campos del briefing: `name`, `country`, `categories`, `monthly_rate`, `currency`, `updated_at`, `status`, `contract_renewal_date`, `contact_email`, `notes`. |
| R02 | sí | `status` solo acepta `active` y `suspended`. |
| R03 | sí | `monthly_rate` es un número mayor que cero. Cero o negativo responden `422` antes de escribir en TinyDB. |
| R04 | sí | Hay modelo de entrada y de respuesta. `updated_at` lo genera el servidor. |
| R05 | sí | Spain usa EUR y USA usa USD. Otra combinación se rechaza. |
| R06 | sí | `categories` es una lista de al menos una categoría de la lista cerrada del briefing. |
| R07 | sí | Renovación, correo y notas son opcionales. |
| R08 | sí | El seeder carga los 15 proveedores del briefing, sin sustituirlos por un dataset genérico. |
| R09 | sí | `uv run seed` funciona desde `services/api` sin tocar el código. |
| R10 | sí | Una segunda ejecución no duplica registros. |
| R11 | sí | La consola dice cuántos registros se insertaron. |
| R12 | sí | Al arrancar la API el directorio no queda vacío: el seeder corre solo y es idempotente. |
| R13 | sí | `POST /suppliers` crea y devuelve el objeto con id (`201`). La entrada inválida es `422`. |
| R14 | sí | `GET /suppliers` sin parámetros devuelve todos. |
| R15 | sí | `GET /suppliers?country=X` devuelve solo ese país. |
| R16 | sí | `GET /suppliers?category=Y` devuelve solo quienes tienen esa categoría. |
| R17 | sí | `GET /suppliers/{id}` responde `404` si el id no existe. |
| R18 | sí | `PATCH /suppliers/{id}/rate` actualiza la tarifa, graba `updated_at` y rechaza tarifas ≤ 0. |
| R19 | sí | `PATCH /suppliers/{id}/status` rechaza un estado que no sea `active` o `suspended` con `422`. |
| R20 | sí | `DELETE /suppliers/{id}` borra (`200`) y responde `404` si no existe. |
| R21 | sí | Los códigos son coherentes: `404`, `422`, `200` y `201`. |
| R22 | sí | El directorio está en el menú del backoffice. |
| R23 | sí | La tabla muestra nombre, país, categorías, tarifa mensual y estado. |
| R24 | sí | Los filtros de país y categoría actualizan el listado sin recargar la página. |
| R25 | sí | El alta valida en el cliente los campos obligatorios y muestra el error de la API si el servidor rechaza el cuerpo. |
| R26 | sí | El cambio de tarifa se ve en el listado cuando la API responde. |
| R27 | sí | Cada fila puede activar o suspender. |
| R28 | sí | Activo y suspendido se distinguen con texto y con color. |
| R29 | sí | Una renovación dentro de 60 días se marca. Una fecha ya pasada se marca como vencida. |
| R30 | sí | El análisis de incidencias del proyecto 009 sigue respondiendo. |
| R31 | sí | El código está en `services/api` y `uis/backoffice`. |
| R32 | sí | TinyDB sigue teniendo los datos después de cerrar y volver a abrir el proceso. |
| R33 | sí | Tokens, Arial/Helvetica y lockup del footer con los hashes del manifiesto SIGNAL. |
| R34 | sí | Hay estados de carga, vacío y error. |
| R35 | sí | Controles con nombre, contraste de texto ≥ 4,5:1, foco visible, objetivos de 44 px y estado no solo por color. |
| R36 | sí | Capturas reales a 390, 768 y 1280 px. |
| R37 | sí | Vídeo de recorrido de 5 a 10 segundos. |
| R38 | sí | Lighthouse headless, throttling simulado, LCP, CLS y TBT en móvil y escritorio. |
| R39 | sí | `prefers-reduced-motion` deja el dato visible sin la animación. |
| R40 | sí | La app interna lleva `noindex`. No se inventa sitemap, dominio ni schema. |
| E01 | extra | El filtro de estado y los filtros de país y categoría se conservan al salir y volver. |
| E02 | extra | Tests del seeder idempotente y de la validación de tarifa y estado antes de persistir. |
| R41 | sí | Evidencia de `uv run seed`, de un filtro de la API y del listado con un filtro aplicado. |
| R42 | sí | El README dice cómo arrancar la API y el seeder. |
