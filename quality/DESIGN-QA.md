# DESIGN-QA — pantalla `/agente`

Alcance: solo esta pantalla. El resto del backoffice no se redibujó. Autoridad: enunciado, luego SIGNAL. App interna: `noindex`, sin sitemap ni schema.

| ID | Qué | Resultado |
| --- | --- | --- |
| QA-01 | Tokens | PASS. `/tokens/tokens.css` y `/tokens/motion.css`. Sin una paleta paralela. |
| QA-02 | Tipo | PASS. `--font-body` y `--font-display` son Arial, Helvetica, sans-serif. El nombre del nodo usa `--font-mono`. |
| QA-03 | Composición | PASS. Título, sesión, dos columnas de trabajo. No hay hero ni tres tarjetas iguales. |
| QA-04 | Idle | PASS. `evidence/agente-idle-390.png`, `agente-idle-768.png`, `agente-idle-1280.png`. |
| QA-05 | Error de sesión | PASS. Contraseña incorrecta. `evidence/agente-login-error-*.png`. El texto del correo se conserva. |
| QA-06 | Empty de ticket | PASS. Ticket 482. Frase honesta y traza `ticket_tool`. `evidence/agente-ticket-vacio-*.png`. |
| QA-07 | Success de tool y error de RAG | PASS. El id real vuelve `in_progress`. La tarifa, sin `EMBEDDING_*`, muestra el error de configuración y la traza hasta el nodo de error. `evidence/agente-lado-a-lado-*.png`. |
| QA-08 | Loading | PASS en código. El botón se desactiva, `aria-busy` pasa a true y el texto es «Consultando esta ruta.» La API local responde antes de poder fotografiar el frame. |
| QA-09 | 390 / 768 / 1280 | PASS. Overflow 0 en las doce capturas de estado. A 390 las columnas se apilan. Desde 768 van en dos columnas. |
| QA-10 | Reduced motion | PASS. `animation: none`. `evidence/agente-reduced-1280.png`. |
| QA-11 | Lockup | PASS. Horizontal 400 px; por debajo de 640 px, apilado 280 px. Hashes en `evidence/lockup-hashes.txt`. |
| QA-12 | Teclado y nombres | PASS. Labels visibles, skip link, foco 2 px, botones ≥ 44 px, campos ≥ 48 px. |
| QA-13 | axe | PASS. axe-core 4.10.3, 0 violaciones. `evidence/axe.json`. No es una certificación WCAG. |
| QA-14 | Vídeo | PASS. `evidence/agente-recorrido.webm`, 5,80 s. |
| QA-15 | Lighthouse | PASS. Mediana móvil LCP 1359,0 ms, CLS 0, TBT 0. Mediana escritorio LCP 328,2 ms, CLS 0, TBT 0. INP de laboratorio: null. `evidence/lighthouse-summary.json`. |
| QA-16 | SEO de landing | NO_APLICA. No es una landing pública. Hay `title`, `description` y `noindex`. |
