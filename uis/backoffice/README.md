# Backoffice — análisis de incidencias

Pantalla interna para subir el CSV de tickets de soporte de Nexova, ver el resumen y descargar `results.csv`. La sirve la API (`services/api`) en `/`. No es el sitio público de la raíz del repositorio: aquel tiene su propio sistema visual y este entregable no pide reutilizarlo.

## Qué hay en pantalla

- Carga con selector de fichero y, además, soltar el CSV en la zona. El teclado usa el selector.
- Totales, reglas de invalidez, categoría, estado y satisfacción.
- Detalle de filas inválidas (línea, ticket y regla), sin correo ni descripción.
- Vista previa del CSV de exportación y botón de descarga.
- Estados de espera, vacío, error y resultado. Si un segundo fichero falla, el análisis anterior sigue visible y el aviso lo dice.
- Página de privacidad en `/privacidad`. Una ruta desconocida responde `404`.

Sin JavaScript el formulario hace `POST` y la API devuelve la página ya rellena.

## Señal visual

Tokens, motion y lockups se copiaron byte a byte desde el paquete SIGNAL v1.1.0:

- `tokens/tokens.css`, `tokens/tokens.json`, `tokens/motion.css`, `tokens/motion.json`
- `brand/lockups/signal-horizontal.svg` (pie, ancho 400px desde 640px)
- `brand/lockups/signal-stacked.svg` (pie, ancho 280px por debajo de 640px)
- `brand/README.md` (procedencia, sin modificar)

La prueba `services/api/tests/test_assets.py` compara esos SHA-256 con el manifiesto. Tipografía Arial/Helvetica. No hay fuentes remotas. El lockup del pie es el crédito visual del encargo; el texto dice que no es una asociación oficial.

La única animación es un fondo de 180 ms al aparecer el resultado (`--motion-state`). No corre con `prefers-reduced-motion` ni cuando `html[data-motion=reduced]`.
