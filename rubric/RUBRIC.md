# Rúbrica — 015 ai-eng-company-monorepo-container

Fuente: `OFFICIAL_README.md` y `OFFICIAL_README.es.md` del syllabus `ai-eng-container-project` (sha `fd2da034894ba93ba738559280ccde074ab1d953`, registry `ai-eng-company-monorepo-container`). Solución de referencia del mismo árbol, sin copiarla como entrega. No hay cláusula que prohíba herramientas de IA («No utilices herramientas de IA», «write each one yourself», «sin copiar», «no uses ChatGPT»). Se ejecutó la solución.

Orden de autoridad: enunciado 4Geeks > notas de lanzamiento > SIGNAL. El fork real es Nexova: el Next.js de producto está en `uis/portal`, la API en `services/api`, y `uis/backoffice` ya sirve HTML estático desde FastAPI. El ticket pide `/uis/website` y `/uis/backoffice` como dos apps Next en un contenedor. Se integran sin duplicar el portal y sin sustituir el HTML de la API.

`required` = el enunciado, el lanzamiento o el encargo de esta ejecución lo exige. `cuenta` = entra en el 100% implementable. `BLOCKED_HITL`, `HITL_MIGUEL` y `HITL_ENVIO_MIGUEL` no restan de ese 100%. Un mock no convierte en PASS un criterio que pide producción o un envío real.

| ID | Required | Cuenta | Criterio |
| --- | --- | --- | --- |
| R01 | sí | sí | Se trabaja en el fork Nexova, no en un repositorio nuevo. La base es `feature/user-authentication-restore` (`d69a3b9`). |
| R02 | sí | sí | `uis/Dockerfile` usa una imagen oficial de Node Alpine. |
| R03 | sí | sí | Las dependencias de `uis/website` y de `uis/backoffice` se instalan por separado. El portal, que es la app del puerto 3000, también. |
| R04 | sí | sí | El `CMD` invoca `start.sh`. Website en el puerto 3000 y backoffice en el 3001. |
| R05 | sí | sí | `uis/.dockerignore` excluye `node_modules`, `.next`, `.env*` y `*.log`. |
| R06 | sí | sí | `services/Dockerfile` usa una imagen oficial de Python. |
| R07 | sí | sí | Instala `uv` y ejecuta `uv pip install -r requirements.txt`. |
| R08 | sí | sí | Uvicorn arranca con `--reload`. |
| R09 | sí | sí | `services/.dockerignore` excluye `__pycache__`, `*.pyc`, `.env*`, `tests/` y `*.log`. |
| R10 | sí | sí | `docker-compose.yml` en la raíz define el servicio de interfaces y el de la API, con bind mount, `next dev` y `--reload`. Qdrant se conserva porque el monorepo ya lo usaba. |
| R11 | sí | sí | Los puertos 3000, 3001 y 8000 quedan publicados en el host. |
| R12 | sí | sí | Los servicios comparten una red Docker con nombre explícito. |
| R13 | sí | sí | La llamada de un contenedor a otro usa el nombre del servicio (`services`, `qdrant`), no `localhost` ni una IP fija. |
| R14 | sí | sí | Ningún Dockerfile ni el Compose contienen secretos, claves ni contraseñas. |
| R15 | sí | sí | Las variables salen del `.env` de la raíz. El YAML no las hardcodea. |
| R16 | sí | sí | `.env` está en `.gitignore` y no aparece en el historial de commits. |
| R17 | sí | sí | `docker compose up --build` levanta la plataforma. El único preparativo es el `.env` que el propio enunciado pide, generado por `make up` sin imprimir secretos. |
| R18 | sí | sí | Un cambio en el host se ve sin reconstruir la imagen, en la UI y en la API. |
| R19 | sí | sí | Un solo contenedor de interfaces sirve los dos Next.js, en 3000 y 3001. Incluye el portal existente y la API FastAPI. |
| R20 | sí | sí | Build multi-stage, usuario no root y healthchecks. |
| R21 | sí | sí | `.env.example` documenta los nombres con secretos vacíos. |
| P01 | sí | no | Los contenedores están desplegados y accesibles en el VPS de producción. |
| D01 | sí | sí | El PR incluye evidencia local de los contenedores en marcha (`docker compose ps`). |
| D02 | sí | no | El PR incluye evidencia del mismo stack en el VPS (SSH o URL en vivo). |
| D03 | sí | no | Compartir el enlace del PR con el tech lead para el sign-off. |
| D04 | sí | no | Merge del PR a `main` después de la aprobación. |
| H01 | sí | no | Confirmar SSH al VPS y autorizar el despliegue. |
| U01 | sí | sí | El panel nuevo usa tokens SIGNAL, Arial/Helvetica, y estados de carga, vacío, éxito y error. |
| U02 | sí | sí | Capturas reales a 390, 768 y 1280 px. |
| U03 | sí | sí | Vídeo corto real del recorrido, entre 5 y 10 s. |
| U04 | sí | sí | `prefers-reduced-motion` deja el panel en el estado final, sin animación. |
| U05 | sí | sí | Lockup oficial en el pie. Horizontal a 400 px desde 640 px; apilado a 280 px por debajo. Hash verificado. |
| U06 | sí | sí | Lighthouse del build de producción del panel: tres corridas móvil y tres de escritorio, con la configuración pedida. |
| U07 | sí | sí | Skip link, etiquetas visibles, foco, `noindex`, 404 y axe sin hallazgos serious/critical. |
| U08 | sí | sí | Sin desbordamiento horizontal del documento en 390, 768 y 1280. |
| U09 | no | no | SEO completo de landing pública. |
| X01 | no | no | Extra visible: `make up` anuncia las tres URLs y el panel muestra el host interno al que llegó. |
| X02 | no | no | Extra técnico: contrato de Compose en pytest, healthchecks y sonda de hot reload. |

El 100% implementable son las filas con `cuenta = sí`: R01–R21, D01 y U01–U08. Son 30.
