# Rúbrica — 013 Flujos de autenticación en el frontend (Nexova)

Fuente: `content/projects/ai-eng-user-authentication-flows` (README en inglés y español, syllabus `fd2da034894ba93ba738559280ccde074ab1d953`). El enunciado manda sobre el encargo y sobre SIGNAL.

Chequeo anti-IA en SOURCE: los dos README oficiales no contienen cláusulas del tipo «No utilices herramientas de IA», «Do not use AI tools», «write each one yourself», «escrito por ti», «sin copiar» ni «no uses ChatGPT». La ejecución sigue.

Leyenda: **required** = exigido por el enunciado o por la forma de entrega de este encargo. **extra** = pedido por el encargo y subordinado a la rúbrica.

| ID | Required | Criterio |
| --- | --- | --- |
| R01 | sí | El trabajo vive en el monorepo de Nexova. No se crea otro repositorio. La rama es `feature/auth-frontend`, el nombre que pide el enunciado. |
| R02 | sí | No hay una aplicación de autenticación separada. Los flujos se integran en una aplicación Next.js dentro del monorepo y consumen la API real de 012. El choque con el backoffice vanilla (token en `sessionStorage`, contrato de 012) queda documentado. No se rompen sus pruebas ni sus rutas. |
| R03 | sí | Existe `/login`: formulario de correo y contraseña. |
| R04 | sí | Si el login tiene éxito, el token se guarda en `localStorage` y el navegador va a la vista autenticada principal. |
| R05 | sí | Si el login falla, se muestra un mensaje de error claro y se conservan los datos escritos. |
| R06 | sí | Existe `/register`: formulario de registro. |
| R07 | sí | Si el registro tiene éxito, se llama a `POST /users` (con los campos opcionales de perfil), después a `POST /auth/login` con las mismas credenciales, se guarda el token y se redirige. |
| R08 | sí | Si el registro falla, se muestran errores de validación a nivel de campo. |
| R09 | sí | `/account/profile` muestra el correo del `User` y `name`, `phone` y `address` del `Profile` obtenido con `GET /auth/me`. |
| R10 | sí | El perfil se edita con `PUT /profiles/me` y el token va en `Authorization: Bearer`. |
| R11 | sí | Están identificadas las vistas Next.js que exigen sesión. El website público (Hito 1) queda fuera. |
| R12 | sí | La protección es un guard o hook de cliente que lee `localStorage` y redirige a `/login` si el token falta o no es válido. No se usa el middleware de Next.js para esa comprobación. |
| R13 | sí | El website público sigue sin comprobación de token y sin redirección a login. |
| R14 | sí | En login y en registro el token se almacena en `localStorage`. |
| R15 | sí | Cada llamada protegida a la API lee el token y lo envía como `Authorization: Bearer`. |
| R16 | sí | El logout quita el token de `localStorage` y redirige a `/login`. |
| R17 | sí | Una respuesta `401` de una llamada protegida borra el token y redirige a `/login`. |
| R18 | sí | El pull request tiene base `feature/auth-api` (el diff es solo 013). La descripción lista las vistas protegidas, confirma que el website público no cambia y documenta el orden de merge #9 → #10 → #11 → este. No se hace merge. |
| R19 | sí | No hay claves externas ni secretos en el repositorio. Solo se versiona un `.env.example` con el placeholder vacío. |
| R20 | sí | Las pruebas de 009, 011 y 012 siguen en verde. Las rutas públicas de la API y del website no quedan detrás del guard. |
| R21 | sí | `uis/portal/README.md` explica qué es el portal, cómo arrancarlo contra la API y la decisión de no convertir el backoffice vanilla. |
| U01 | sí (SIGNAL, hay UI) | Tokens, tipografía Arial/Helvetica, estados de carga, vacío y error, contraste AA, `prefers-reduced-motion` y lockup en el pie con los bytes del paquete. Los hashes coinciden con `MANIFEST.json`. |
| U02 | sí (SIGNAL, hay UI) | Capturas reales a 390, 768 y 1280 px, y un video de recorrido de 5 a 10 segundos. |
| U03 | sí (SIGNAL, hay UI) | Lighthouse headless sobre el build de producción: 3 corridas por superficie, mediana y peor caso. Móvil 390×844, RTT 150 ms, 1638.4 kbps, CPU ×4. Escritorio RTT 40 ms, 10240 kbps, CPU ×1. `configSettings` verificado en cada JSON. En el repo solo `lighthouse-summary.json`. |
| E01 | extra | Aviso visible de sesión vencida y vuelta a la vista protegida que el usuario estaba viendo. |
| E02 | extra | Pruebas E2E de registro, login, 401, logout y de que las rutas públicas no se ven afectadas. |
