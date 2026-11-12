# `uis` folder

This folder contains **all projects with a user interface** for the cross-functional AI Engineering company project — for example: a public website, admin dashboard frontend, ecommerce UI, customer portals, Streamlit/Gradio app or other frontend-only tools.

The two main projects stored here are:

- **`website`** — the company's public-facing web presence.
- **`backoffice`** — the internal admin application. This is the ideal place to develop multiple solutions within a single project: authentication, people management, operations management, internal communication, and other back-office capabilities.

Organize `uis/` by **different concerns** — each subfolder covers a distinct area of the company (for example, public web vs internal operations) and includes its own technical and functional documentation.

- **Main purpose**: to centralize in a single place all frontend applications that support the company's use cases.
- **Recommendation**: document in this file (or in sub-READMEs) the applications you add, their objective, the technology used, and how to run them.

> _Estas instrucciones también están disponibles en [español](./README.es.md)._

## `backoffice/`

Internal screens for incident analysis (`/`) and the supplier directory (`/proveedores`), served by `services/api`. They do not replace the public website at the repository root. See [`backoffice/README.md`](./backoffice/README.md).

The 012 session form on those pages keeps the JWT in `sessionStorage` for that delivery. It is not the Next.js guard of 013.

## `portal/`

Next.js app for login, registration, profile, and the protected internal views. It calls the same API with `Authorization: Bearer` and stores the JWT in `localStorage`. See [`portal/README.md`](./portal/README.md).

The public website stays at the repository root. It is not served by the portal and it does not check a token.
