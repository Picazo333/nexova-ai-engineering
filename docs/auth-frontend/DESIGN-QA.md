# DESIGN-QA — portal de autenticación (013)

Superficie: `uis/portal`, build de producción de Next.js 15.5.29. Enunciado por encima de SIGNAL. El sitio público no se redibuja.

## Bloques

| Ruta | Pregunta | Hecho | Acción |
| --- | --- | --- | --- |
| `/login` | ¿Hay sesión? | El formulario llama a `POST /auth/login`. | Entrar, o crear cuenta. |
| `/register` | ¿La API acepta la cuenta? | `POST /users` y después `POST /auth/login`. | Crear cuenta. Los errores quedan en el campo. |
| `/` | ¿Qué dice el CSV de tickets? | Sin análisis todavía, el texto lo dice. | Elegir el fichero y analizar. |
| `/proveedores` | ¿Qué contratos hay? | `GET /suppliers` con el token. | Filtrar por país o quitar el filtro. |
| `/account/profile` | ¿Qué contacto tiene la cuenta? | Correo de `User` y perfil de `GET /auth/me`. | Guardar nombre, teléfono y dirección. |

## Tokens y tipo

Copia byte a byte de `tokens/tokens.css`, `tokens/tokens.json`, `tokens/motion.css`, `tokens/motion.json` y de los lockups. Tipografía Arial/Helvetica. Sin fuentes remotas. El `h1` de una herramienta interna usa la escala de `--text-h2`: la escala display del token es de landing y aquí taparía el formulario.

## Estados

Cada petición tiene espera, resultado, vacío o error. El botón se desactiva mientras la petición está en curso. Si falla, los campos no se vacían. El directorio conserva el listado anterior si una recarga falla y muestra el error con reintento.

## Accesibilidad

Un `h1` por ruta. Enlace de salto. Labels visibles. Campos de 48px y botones de al menos 44px. Foco 2px con offset 3px. Errores en `role="alert"` y estados en `role="status"`. Contraste de tinta, acción y peligro sobre los tokens SIGNAL (texto blanco sobre `--color-action`). `lang="es"`. `robots` noindex: es una herramienta interna, no una landing.

## Motion

El panel de resultado usa `--motion-state` (180ms) en el fondo. `prefers-reduced-motion` y `html[data-motion=reduced]` lo anulan desde el CSS del paquete y desde `MotionPref`, que también reacciona si la preferencia cambia. Captura `incidencias-reduced-1280.png`: el atributo quedó en `reduced`.

## Anchos

Capturas reales a 390, 768 y 1280. El script de captura aborta si `scrollWidth` del documento supera al viewport. La tabla de contratos se desplaza dentro de una región con nombre accesible.

## Lockup

Pie de todas las rutas. Por debajo de 640px, `signal-stacked.svg` a 280px. Desde 640px, `signal-horizontal.svg` a 400px. `alt="4Geeks por Divinivid"`. El texto del pie dice que no es una asociación oficial. Hashes comprobados contra `MANIFEST.json` del paquete.

## Presupuesto

El runtime de Next deja la primera carga compartida en 103 kB sin comprimir (salida de `next build`), por debajo de 170 kB gzip. El CSS propio más los tokens cabe en el presupuesto de 40 kB. LCP de laboratorio por debajo de 2,5 s y CLS por debajo de 0,1 en la matriz de `lighthouse-summary.json`. INP no sale en laboratorio (`null`); el proxy medido es TBT.

El `main` de las rutas protegidas reserva `100dvh` para que el pie no salte mientras se comprueba el token. En la captura a página completa se ve ese aire entre el formulario y el pie.
