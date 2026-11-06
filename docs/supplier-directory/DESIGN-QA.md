# DESIGN-QA — directorio de proveedores

App interna. No es una landing. SIGNAL se aplica a la UI del backoffice. El enunciado fija los campos, los filtros y las acciones; SIGNAL no los sustituye.

| ID | Qué | Cómo | Resultado | Evidencia |
| --- | --- | --- | --- | --- |
| QA-01 | Tokens y tipo | `tokens.css` y `motion.css` sin editar. Arial, Helvetica. Sin fuentes remotas. | PASS | `test_signal_asset_hashes` |
| QA-02 | Lockup | Horizontal ≥ 400 px desde 640. Apilado ≥ 280 px por debajo. Bytes iguales al manifiesto. | PASS | A 390 el `currentSrc` es `signal-stacked.svg`. A 768 y 1280, el horizontal. |
| QA-03 | Copy | Título, filtros, tabla y alta. Sin eslogan intercambiable ni métricas inventadas. | PASS | Capturas del directorio. |
| QA-04 | Carga | Texto «Cargando proveedores…», `aria-busy`, la tabla previa sigue. | PASS | `ui-loading-390.png`, `ui-loading-768.png`, `ui-loading-1280.png` |
| QA-05 | Vacío | Con filtros que no encajan: mensaje y acción «Quitar filtros». Sin datos: invita a registrar o a sembrar. | PASS | `ui-empty-*.png`. Test del directorio vacío. |
| QA-06 | Error | Fallo de red al refrescar el fragmento: alerta, reintentar, filas anteriores visibles. Alta rechazada: el formulario no se borra. | PASS | `ui-error-*.png`, `ui-api-error-1280.png`, `ui-client-error-1280.png` |
| QA-07 | 390 px | Viewport 390. Documento sin scroll horizontal. La tabla sí, dentro de `.table-scroll`. | PASS | `ui-filter-ats-390.png`, `ui-filter-ats-390-scrolled.png`. Medición: scroller 358 px, tabla 2790 px, Nombre 144 px. |
| QA-08 | 768 px | Misma página filtrada por ATS, vacío, carga y error. | PASS | `ui-*-768.png` |
| QA-09 | 1280 px | Filtro ATS con Workable activo y Greenhouse suspendido. | PASS | `ui-filter-ats-1280.png` |
| QA-10 | Foco y tamaño | `:focus-visible` 2 px, offset 3 px. Botones ≥ 44 px. Inputs y selects ≥ 48 px. | PASS | `uis/backoffice/css/app.css` |
| QA-11 | Contraste | Tinta, muted, éxito, peligro, aviso y acción sobre superficie, todos ≥ 4,5. El borde `#788598` sobre blanco da 3,75 (componente, umbral 3). | PASS | Cálculo en la sesión de evidencia. |
| QA-12 | No solo color | El estado y la renovación llevan texto. | PASS | Badges «Activo (active)», «Suspendido (suspended)», «Renovación vencida». |
| QA-13 | Teclado | Selects, checks, botones y el scroller con `tabindex="0"`. Sin gesto exclusivo. | PASS | Controles nativos. |
| QA-14 | axe | axe-core 4.10.3 en la página filtrada a 1280. | PASS | `axe-proveedores.json` es `[]`. |
| QA-15 | Motion | Fondo de fila 180 ms solo si no hay reduced-motion. El dato nuevo está en el HTML desde el primer pintado tras la respuesta. | PASS | `ui-reduced-motion-1280.png` (`data-motion=reduced`). |
| QA-16 | Vídeo | Recorrido real de filtros, 6,48 s, sin botón de repetir. | PASS | `supplier-walkthrough.mp4` |
| QA-17 | Lighthouse | Producción = uvicorn sin reload. Simulate, RTT 150, 1638,4 kbps, CPU ×4. Tres corridas. | PASS | Mediana móvil LCP 1657,3 ms, CLS 0, TBT 0. Mediana escritorio LCP 1660,4 ms, CLS 0, TBT 0. |
| QA-18 | Presupuesto | CSS gzip ≤ 40 KiB y JS gzip ≤ 170 KiB, incluidos tokens y `suppliers.js`. | PASS | `test_front_end_transfer_budgets` |
| QA-19 | SEO | `noindex`. Sin canonical, sitemap ni schema. | NO APLICA el SEO de landing. PASS lo que aplica. | `layout.html` |
| QA-20 | Incidencias | La portada de 009 sigue en `/` con su formulario. | PASS | `ui-incidents-1280.png` y `test_api.py` |

No se certifica WCAG por la puntuación de una herramienta. axe no reportó violations en la página medida; el contraste y los nombres se revisaron aparte.
