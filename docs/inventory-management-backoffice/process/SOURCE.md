# SOURCE — 022 inventario en el backoffice

Syllabus `ai-eng-inventory-management-backoffice` @ `fd2da034894ba93ba738559280ccde074ab1d953`.

Enunciado leído: `OFFICIAL_README.md` y `OFFICIAL_README.es.md`. No hay cláusula que prohíba herramientas de IA ni que exija escribir el trabajo a mano. Se implementa.

Autoridad: enunciado 4Geeks > briefing de Nexova > SIGNAL. Las rutas HTTP siguen siendo las de la API (`/inventory/products`, `/inventory/orders/inbound`, `/inventory/orders/outbound`, `/inventory/orders`). Las etiquetas de la interfaz usan Asset, AssetEntry, AssetExit, `current_stock`, `user_uuid`, `supplier`, `exit_type`, `assigned_to` y `office`.

Base git: `feature/milestone-backend-development` @ `106083a`. Rama de trabajo: `feature/inventory-management-backoffice`. Sin merge. Sin LMS.

La API de 021 ya está en `services/api`. El stock no es una columna. El backoffice Next.js es `uis/backoffice` (puerto 3001). La sesión es la de 012/013/014: `POST /auth/login` y la clave `nexova-access-token`. Cada origen guarda su propio `localStorage`.
