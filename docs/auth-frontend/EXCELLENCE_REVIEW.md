# Excellence review — 013

Los dos extras del encargo se implementan. No sustituyen a la rúbrica.

## E01 — IMPLEMENT

Aviso visible de sesión vencida y vuelta a la vista protegida.

Si una llamada con token responde `401`, `leaveForLogin` borra `nexova-access-token` y abre `/login?reason=expired&next=<ruta>`. El login muestra «La sesión ha vencido» y nombra la vista (análisis, directorio o perfil). Tras un login correcto, `safeNext` solo acepta `/`, `/proveedores` y `/account/profile` y el navegador vuelve ahí.

Evidencia: `uis/portal/lib/api.ts` (`leaveForLogin`), `uis/portal/lib/paths.ts`, `uis/portal/components/LoginScreen.tsx`, test `un 401 limpia la sesión…` en `e2e/auth.spec.ts`, capturas `sesion-vencida-390.png` y `sesion-vencida-1280.png`.

## E02 — IMPLEMENT

Pruebas de extremo a extremo contra la API real de 012.

Cubren registro con perfil, `Authorization: Bearer` en `GET /auth/me` y `PUT /profiles/me`, login fallido, errores de campo, correo duplicado, redirección sin token, 401, logout y que el website público y las HTML de la API no saltan al portal. El secreto JWT de esas pruebas se genera en memoria y no se escribe en el repositorio.

Evidencia: `uis/portal/e2e/auth.spec.ts`, `uis/portal/e2e/public.spec.ts`. 9 passed. La suite de 009/011/012 sigue en 45 passed.

## Rechazado

Guardar el JWT también en una cookie para que el middleware de Next.js pudiera leerlo. El enunciado pide `localStorage` y un guard de cliente. Una cookie sería otro almacén y abriría la comprobación en el servidor, que el enunciado aparta.

## Diferido

No se reescribe el backoffice vanilla. Su contrato de 012 es `sessionStorage` en el origen del puerto 8000. Mezclarlo con el `localStorage` del portal rompería esa entrega sin cumplir mejor el enunciado de Next.js.
