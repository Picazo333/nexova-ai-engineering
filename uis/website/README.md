# `website`

El ticket nombra `/uis/website` como el sitio Next.js del puerto 3000. En este fork esa aplicación ya existe: es `uis/portal` (login, registro, restablecimiento y vistas internas). No se duplica el portal.

`npm run dev` en esta carpeta arranca el portal en `0.0.0.0:3000`. El Dockerfile instala las dependencias de esta carpeta y las de `uis/portal` por separado, y las de `uis/backoffice` en otro `npm ci`. `uis/start.sh` lanza este script y el backoffice en el puerto 3001 dentro del mismo contenedor.
