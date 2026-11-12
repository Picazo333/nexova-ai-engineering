# Revisión de excelencia — 012

Los extras no sustituyen la rúbrica. Los dos pedidos por el encargo están implementados y vuelven a pasar la suite (45 tests).

## E01 — Guía ejecutable en Swagger — IMPLEMENT

Qué se nota al abrir `/docs`: la descripción de la API es una guía de cinco pasos (registro, login, perfil, 401, 403). Cada operación lleva el número de paso en el resumen. El botón Authorize envía el correo como `username` al `POST /auth/login`, el mismo endpoint que acepta JSON.

Evidencia: `services/api/app/auth/guide.py`, capturas `docs/user-authentication/evidence/swagger-guide-1280.png` y `swagger-guide-390.png`. El vídeo de recorrido termina en esa pantalla.

## E02 — Tests de caducidad, ownership y regresión — IMPLEMENT

`services/api/tests/test_auth.py` cubre:

- token ausente, mal formado, firmado con otro secreto y ya caducado → 401
- leer, editar o borrar las credenciales de otro usuario → 403, con un token válido
- el perfil de quien llama no pisa el perfil ajeno
- las 10 rutas ya existentes de proveedores e incidencias responden 401 sin token y, con token, el código que ya tenían (200, 400, 404 o 422)

Evidencia: `docs/user-authentication/evidence/pytest.txt` (45 passed) y `http-transcript.txt`.

## Otras decisiones

- IMPLEMENTADO dentro de E02, no como tercer extra: la comparación de contraseña también se ejecuta cuando el correo no existe, contra un hash de relleno, para no adelantar la respuesta solo en el caso de usuario ausente.
- REJECT: permisos distintos por rol en cada ruta de proveedores o de incidencias. El enunciado dice que no hace falta en esta entrega, y cambiaría el contrato que ya cubren los tests de 009 y 011 (cualquier sesión válida opera el directorio y el análisis).
- DEFER: tabla de permisos por rol cuando el enunciado lo pida. Hoy el rol solo condiciona el cambio de `role` e `is_active`, que es lo que AUTH-01 pide.

## Lockup

Hay UI, así que el lockup 4Geeks × Divinivid sigue en el pie, con los SVG que ya estaban. No se redibujaron. El test de hashes de assets sigue en verde.
