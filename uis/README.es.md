# Carpeta `uis`

Esta carpeta contiene **todos los proyectos con interfaz de usuario** para el proyecto transversal de AI Engineering de la compañía — por ejemplo: un sitio web público, un frontend de panel de administración, una interfaz de ecommerce, portales para clientes, aplicaciones Streamlit/Gradio u otras herramientas sólo-frontend.

Los dos proyectos principales que se almacenan aquí son:

- **`website`** — la presencia web pública de la compañía.
- **`backoffice`** — la aplicación interna de administración. Es el lugar ideal para desarrollar múltiples soluciones dentro de un mismo proyecto: autenticación, gestión de personas, gestión de operaciones, comunicación interna y otras capacidades de back-office.

Organiza `uis/` por **distintas áreas de la compañía** — cada subcarpeta agrupa un ámbito diferente (por ejemplo, web pública frente a operaciones internas) e incluye su propia documentación técnica y funcional.

- **Propósito principal**: centralizar en un único lugar todas las aplicaciones frontend que dan soporte a los casos de uso de la compañía.
- **Recomendación**: documenta en este archivo (o en sub-READMEs) las aplicaciones que vayas añadiendo, su objetivo, tecnología usada y cómo ejecutarlas.

> _These instructions are also available in [English](./README.md)._

## `backoffice/`

Pantallas internas de análisis de incidencias (`/`) y del directorio de proveedores (`/proveedores`). Las sirve `services/api`. No sustituyen al sitio público de la raíz del repositorio. Ver [`backoffice/README.md`](./backoffice/README.md).

El formulario de sesión de 012 guarda el JWT en `sessionStorage`. No es el guard de Next.js de 013.

## `portal/`

Aplicación Next.js con login, registro, restablecimiento de contraseña, perfil y las vistas internas protegidas. Llama a la misma API con `Authorization: Bearer` y guarda el JWT en `localStorage`. Ver [`portal/README.md`](./portal/README.md).

El sitio público sigue en la raíz del repositorio. No lo sirve el portal y no comprueba token.
