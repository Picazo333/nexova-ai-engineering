# Revisión de excelencia — 014

Los extras no sustituyen la rúbrica. El correo real sigue en BLOCKED_HITL.

## Extra visible — IMPLEMENTADO

Tres estados distintos cuando el enlace no se puede usar:

- Sin `token`: «Falta el enlace de recuperación» y «Pedir un enlace».
- Caducado: «El enlace ha caducado» y «Pedir otro enlace».
- Ya usado: «Este enlace ya se usó» y el mismo camino de vuelta.

El enunciado pide un error claro y un enlace. Separar el motivo es lo que se ve al abrir la página. No cambia el contrato de la API: el `400` y el `code` ya existían.

Evidencia: `evidence/restore-reset-empty-390.png`, `evidence/restore-reset-expired-768.png`, `evidence/restore-reset-used-1280.png`. El vídeo `evidence/restore-recorrido.webm` pasa por el estado vacío y termina en el aviso de contraseña actualizada.

## Extra técnico — IMPLEMENTADO

1. **Un solo ganador.** `reset_password` comprueba la fila y escribe el hash dentro de `auth_lock`. `test_concurrent_reset_commits_only_one_password` lanza dos hilos con contraseñas distintas: uno responde bien, el otro recibe `used`, y solo la contraseña ganadora entra.
2. **Tope por hora.** `PASSWORD_RESET_MAX_PER_HOUR` (defecto 5) cuenta intentos por correo, también si la cuenta no existe, y sigue respondiendo el mismo `200`. Por encima del tope no se crea otro enlace. Test `test_rate_limit_keeps_the_same_body_and_stops_sending`.
3. **Auditoría mínima del enlace.** La fila guarda `created_at` y `remote_addr` (el par del socket, no una cabecera que el cliente pueda inventar). Esos campos no van en la respuesta HTTP.

El HTML del correo (una columna, 16 px, enlace en botón y en texto) cubre la frase del enunciado «legible en móvil». No se cuenta como un tercer extra.

## Rechazado

No se añadió un segundo producto visual (hero, métricas, testimonios). El portal ya es una herramienta interna.

No se invalidan los JWT de sesión al cambiar la contraseña. El enunciado no lo pide y el token de acceso sigue siendo de corta duración. Hacerlo ahora cambiaría el contrato de 012.

## Diferido

Medir el tiempo de respuesta de `forgot-password` para cerrar el canal de enumeración cuando Resend responde de verdad. Con el proveedor apagado la respuesta es la misma y no hay ida de red. Cuando haya clave, la llamada solo ocurre si la cuenta está activa: el cuerpo sigue siendo idéntico, el tiempo no. Dejarlo escrito evita fingir que el canal de tiempo está cerrado.
