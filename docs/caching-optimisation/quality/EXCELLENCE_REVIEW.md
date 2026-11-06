# Revisión de excelencia — 024

Estado de esta revisión: no sustituye la del orquestador.

## Qué queda sólido

El historial era la lectura cara de verdad: 1,33 ms con la semilla de 9 órdenes y 110,50 ms con 7680 movimientos. El HIT HTTP baja a 2,06 ms y una entrada correcta lo invalida. El directorio, a 1500 contratos, baja de 22,66 ms a 2,43 ms, y una tarifa, un estado o un borrado lo vacían. Los tests cubren el TTL con reloj falso, el 400 que no invalida y dos usuarios que no comparten una clave privada.

Los formularios de entrada y de salida bajan la ruta de 4,41 kB y 5,3 kB a 1,64 kB. El `useMemo` se apoya en una medida: 361 ms si cada fila construye su `Intl`, no en el resumen de 0,086 ms, que se descartó.

## Límites

- El HIT de 2,06 ms es TestClient en el mismo proceso. No es un cliente en otra máquina. El cuerpo deja de reconstruirse; el tiempo de red no está en esa cifra.
- La caché es de un solo proceso. Otro worker no vería la invalidación. El TTL de 30 s y 60 s es el tope en ese caso. Este repo arranca uvicorn sin `--workers`.
- `GET /inventory/products` se deja fuera a propósito (5,94 ms). La pantalla de activos no muestra la nota de caché.
- En el portal, `next build` sube la ruta `/` de 3,65 kB a 4,2 kB. El panel diferido son 707 B gzip y no viaja hasta que hay un análisis. El cargador cuesta más que ese panel en la línea de la ruta.
- Con las 9 órdenes de la semilla, `prepareHistory` es barato. El `useMemo` está justificado por el mismo historial cuando crece a miles de filas, que es el caso medido.
- El vacío y el error de las capturas son respuestas forzadas en el navegador. El HIT, la tabla y la nota son la API con Postgres y la semilla.
- Redis no se usó. No hay un PASS de Redis.

## Extra visible y extra técnico

Visible: la frase de caché en el historial, solo cuando la cabecera es HIT.

Técnico: expiración por reloj y clave privada que no se comparte, con la invalidación en las escrituras.
