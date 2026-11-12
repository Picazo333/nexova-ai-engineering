# Justificación — 013

Chequeo anti-IA: los README oficiales no prohíben herramientas de IA ni piden redacción manual. Se ejecuta la solución.

| ID | Estado | Cómo se cumple | Evidencia |
| --- | --- | --- | --- |
| R01 | PASS | El portal vive en este monorepo, rama `feature/auth-frontend`. No hay otro repositorio. | `uis/portal/`. Rama creada desde `feature/auth-api`. |
| R02 | PASS | No es una app solo de login. Tras entrar están el análisis de tickets, el directorio y el perfil, llamando a la API de 012. Nota: el portal (`uis/portal`, puerto 3000) guarda el token en `localStorage`; el backoffice del puerto 8000 sigue con el `sessionStorage` de 012 porque aquel contrato pedía el almacén de la pestaña y cambiarlo rompería esa entrega. Son orígenes distintos. | `uis/portal/README.md`. `uis/README.md`. Pytest 45 passed. |
| R03 | PASS | `/login` pide correo y contraseña. | `uis/portal/app/login/page.tsx`. `components/LoginScreen.tsx`. |
| R04 | PASS | El login correcto escribe el token y abre la vista principal `/`. | `LoginScreen.tsx` líneas 41-57 (`writeToken`, `router.push`). Test de registro, que termina en `/`. |
| R05 | PASS | Un login rechazado muestra el mensaje de la API y no borra los campos. | `LoginScreen.tsx` líneas 58-63. Test «el login fallido conserva la contraseña». Captura `login-error-768.png`. |
| R06 | PASS | Existe `/register`. | `app/register/page.tsx`. `components/RegisterScreen.tsx`. |
| R07 | PASS | El alta hace `POST /users` con nombre, teléfono y dirección, luego `POST /auth/login` con las mismas credenciales, guarda el token y redirige. | `RegisterScreen.tsx` líneas 70-98. Test «el registro guarda el token…». |
| R08 | PASS | Correo o contraseña inválidos marcan el campo. Un 409 de correo repetido también. | `lib/forms.ts`. `lib/api.ts` líneas 89-92. Test de errores de campo y de correo repetido. Capturas `register-error-390.png` y `register-error-1280.png`. |
| R09 | PASS | El perfil muestra el correo y el rol del usuario y nombre, teléfono y dirección del perfil que devuelve `GET /auth/me`. | `components/ProfileScreen.tsx`. Test que compara esos tres campos. Capturas `perfil-390.png` y `perfil-1280.png`. |
| R10 | PASS | Guardar envía `PUT /profiles/me` con `Authorization: Bearer`. | `ProfileScreen.tsx` línea 56. El test espera esa cabecera en el PUT. |
| R11 | PASS | Protegidas: `/`, `/proveedores`, `/account/profile`. Públicas en el portal: `/login`, `/register`. El website de la raíz queda fuera. | Tabla en `uis/portal/README.md`. |
| R12 | PASS | `SessionGate` lee `localStorage` y, si no hay token, va a `/login`. Si `GET /auth/me` responde 401, limpia y redirige. No existe `middleware.ts`. | `components/SessionGate.tsx` líneas 40-48. `e2e/auth.spec.ts` afirma que no hay middleware. |
| R13 | PASS | `index.html`, `application.html` y `404.html` no mencionan login ni `localStorage`. Servidos en el puerto 4173 responden 200 y no redirigen. | `e2e/public.spec.ts`. |
| R14 | PASS | El enunciado lo exige. `README.md` de `ai-eng-user-authentication-flows`, línea 34: «The token must be stored in `localStorage` and attached to every protected API call via the `Authorization: Bearer` header.» Línea 80: «On login and registration: store the token in `localStorage`.» Login y registro llaman a `writeToken`. | `lib/session.ts` líneas 12-16. Cita también en `uis/portal/README.md`. |
| R15 | PASS | `apiFetch` y `apiDownload` leen el token y ponen `Authorization: Bearer` en las llamadas protegidas. Login y registro van con `auth: false` para no tratar un 401 de credenciales como sesión vencida. | `lib/api.ts` líneas 62-68 y 85-87. Test del header en `GET /auth/me` y en el PUT. |
| R16 | PASS | «Cerrar sesión» borra la clave y abre `/login`. | `components/AppHeader.tsx` líneas 17-19. Test de logout. |
| R17 | PASS | Un 401 de una llamada autenticada ejecuta `leaveForLogin`: borra el token y abre `/login?reason=expired`. | `lib/api.ts` líneas 23-30 y 85-87. Test del token caducado. |
| R18 | PASS | El PR tiene base `feature/auth-api`. La descripción lista las vistas protegidas, dice que el website público no cambia y fija el orden #9 → #10 → #11 → este. No se hace merge. | Cuerpo del pull request. |
| R19 | PASS | No hay claves de terceros. `uis/portal/.env.example` solo tiene `NEXT_PUBLIC_API_URL=` vacío. El secreto de las pruebas E2E se genera con `randomBytes` y no se versiona. `services/api/.env` sigue ignorado. | `.env.example`. `playwright.config.ts`. `.gitignore` de la raíz. |
| R20 | PASS | `pytest` del monorepo: 45 passed (009, 011 y 012). `GET /`, `/privacidad` y `/proveedores` de la API siguen en 200 y no apuntan al portal. | Salida de pytest. `e2e/public.spec.ts`. |
| R21 | PASS | El README del portal dice qué es, cómo arrancarlo contra la API y por qué el backoffice vanilla no se convierte a Next.js. | `uis/portal/README.md`. |
| U01 | PASS | Tokens, motion y lockups copiados byte a byte. Hashes iguales al `MANIFEST.json` del paquete. Carga, vacío y error visibles. AA de los tokens. Reduced motion comprobado. Lockup en el pie. | Salida PASS de SHA-256 en la evidencia. Capturas de carga, vacío, error y `incidencias-reduced-1280.png`. |
| U02 | PASS | Capturas a 390, 768 y 1280 de login, registro e incidencias vacías, más perfil, proveedores, error y sesión vencida. Video `recorrido.webm` de 6,44 s: login, entrada y perfil. | `docs/auth-frontend/evidence/`. |
| U03 | PASS | 3 corridas por superficie (login, register, incidencias, perfil, proveedores), móvil y escritorio. 30 JSON en `/opt/cursor/artifacts/lighthouse/`. Ninguno en el repo. Cada `configSettings` cumple móvil RTT 150, CPU ×4, 1638,4 kbps, 390×844, y escritorio RTT 40, CPU ×1, 10240 kbps. Mediana móvil de proveedores: LCP 2187 ms, CLS 0,017, TBT 37 ms. Peor LCP de esa superficie: 2334 ms. INP de laboratorio: null. | `docs/auth-frontend/lighthouse-summary.json`. Comprobación Python de los 30 JSON: `bad []`. |
| E01 | PASS | El aviso «La sesión ha vencido» nombra la vista y, al entrar, se vuelve a ella. | Test del 401. Capturas `sesion-vencida-390.png` y `sesion-vencida-1280.png`. |
| E02 | PASS | 9 pruebas Playwright passed: registro, login, 401, logout y rutas públicas. | `uis/portal/e2e/`. |

Mediana y peor caso completos, con el `configSettings` de cada forma, están en `lighthouse-summary.json`. El peor LCP de toda la matriz es proveedores en móvil, corrida 2, 2334 ms. El peor CLS es 0,0169.
