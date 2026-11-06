# Seguimiento de candidaturas — Nexova Solutions

Frontend interno de Operaciones de Selección. Lista las candidaturas del tracker, filtra por estado y etapa, busca por nombre o correo y permite actualizar estado, etapa, notas y datos.

La app vive en el monorepo de Nexova, en `uis/talent-pipeline-tracker`. No sustituye el sitio público de la raíz.

## Cómo ejecutarlo

Requisitos: Node.js 22 y npm.

```bash
cd uis/talent-pipeline-tracker
cp .env.example .env.local
npm install
npm run dev
```

Abre `http://localhost:3000`.

Variable:

```text
NEXT_PUBLIC_API_URL=https://playground.4geeks.com/tracker/api/v1
```

`.env.local` no se versiona. Si la variable no está, el build usa esa misma URL pública. No es un secreto y no hace falta token.

## Comandos

```bash
npm run lint
npm run typecheck
npm test
npm run test:contract
npm run verify:assets
npm run build
```

`test:contract` llama a la API pública: crea una candidatura de prueba, la actualiza, añade y borra una nota, y después elimina el registro.

## Estructura

| Ruta | Uso |
| --- | --- |
| `app/page.tsx` | Listado `/` |
| `app/candidates/[id]/page.tsx` | Detalle |
| `app/candidates/[id]/edit/page.tsx` | Edición (`PUT`) |
| `app/candidates/new/page.tsx` | Alta (`POST`) |
| `components/` | Pantallas y controles |
| `hooks/` | Cliente del tracker y carga con estados |
| `lib/` | Acceso HTTP, validación, filtros |
| `types/` | Tipos de la API |
| `styles/` | Tokens SIGNAL, sin modificar |
| `public/brand/lockups/` | Lockup 4Geeks × Divinivid |

## Decisiones

- Next.js App Router, React y TypeScript. El estado vive en los componentes que lo usan. No hay Redux, Zustand ni Jotai.
- Las llamadas pasan por `lib/api.ts` con `async/await`. Cada carga muestra cargando, éxito o error.
- Los filtros usan `useSearchParams` (`status`, `stage`, `q`) y `router.replace`, sin recarga completa. El enlace de vuelta al listado conserva esa query.
- El contexto de empresa está en `ASSUMPTIONS.md`: Nexova no define los enumerados del tracker, y los registros de la API del curso no se presentan como datos de producción.
- La interfaz usa los tokens académicos SIGNAL (Arial, Helvetica, tema claro). El sitio público tiene otra paleta y el enunciado no pide reutilizarla.

## Rutas

- `/`
- `/candidates/new`
- `/candidates/[id]`
- `/candidates/[id]/edit`
