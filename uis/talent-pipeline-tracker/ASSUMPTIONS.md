# Supuestos

Hechos que el repositorio no fija y que esta implementación necesita para funcionar.

## Empresa

- La empresa del monorepo es Nexova Solutions, según `CONTEXT.md`, `BRIEFING.md` y `company-choice.md`.
- El hito habla de “People & Talent”. Nexova no usa ese nombre. El departamento que sigue candidaturas es **Operaciones de Selección** (Javier Almeida, 40 consultores). La interfaz usa ese nombre.
- Recursos Humanos interno (Patricia Solís) gestiona a la plantilla de Nexova, no el pipeline de candidaturas de clientes. No se presenta esta herramienta como el portal de RRHH interno.
- No hay en el repo un encargo literal de Javier Almeida para esta pantalla. El texto solo dice para quién es el trabajo.

## Datos

- `BRIEFING.md` no define estados, etapas ni campos de una candidatura. Esos valores salen del OpenAPI público del tracker: estados `received`, `in_progress`, `selected`, `discarded` y etapas `pending`, `review`, `personal_interview`, `technical_interview`, `offer_presented`.
- Las etiquetas en español (“Recibida”, “Entrevista técnica”, etc.) son traducción de esos valores. Si la API devuelve uno distinto, se muestra el valor crudo.
- Los registros de `https://playground.4geeks.com/tracker/api/v1` son datos del curso, no un extracto del ATS de Nexova. El pie lo dice. No se tratan como clientes ni empleados reales.
- La zona horaria de las fechas es `Europe/Madrid`, por la sede de Valencia. La API entrega ISO-8601.

## Diseño

- El sitio público de Nexova tiene tokens propios (`marfil`, `tinta`, `miel`) en `index.html`. El enunciado no pide reutilizarlos y limita el stack a Next.js, React y TypeScript. Mezclar ese tema con SIGNAL rompería la regla de un solo tema. Esta app usa los tokens SIGNAL y el nombre de Nexova en texto, sin redibujar el símbolo del sitio.
- El lockup 4Geeks × Divinivid va en el pie, como pide el encargo académico. No afirma una colaboración oficial.

## API

- No hace falta token. `NEXT_PUBLIC_API_URL` tiene como respaldo la URL pública del enunciado para que el build no quede vacío si falta el archivo de entorno.
- `GET /records` pagina (por defecto 20). La lista pide páginas de 100 hasta cubrir `total`, porque el enunciado pide ver todas las candidaturas.
- `PUT` no envía estado ni etapa. Una sonda del 2026-11-06 mostró que el tracker los conserva. El formulario de edición no los pide; se cambian con `PATCH` en el detalle.
- `POST /records/:id/notes` devuelve la nota. `GET /records/:id/notes` devuelve `{ data, meta }`.
- La búsqueda y los filtros de la pantalla se aplican en el cliente sobre el listado completo y se reflejan en la query (`status`, `stage`, `q`) con `useSearchParams`. Así una búsqueda no deja fuera las páginas que el servidor no ha devuelto.

## Idioma y entrega

- La interfaz está en español porque el briefing de Nexova y la operación descrita están en español.
- No hay despliegue: el enunciado pide subir el monorepo, no una URL pública. El build local es la verificación.
