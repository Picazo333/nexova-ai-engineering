# QA REPORT — nexova-public-website @ 238a96c

- **Revisor:** sesión de QA independiente. No construí el sitio (builder ≠ revisor).
- **Artefacto probado:** `/home/claude/site`, copia byte-idéntica declarada de `milestone/nexova-public-website` @ `238a96c`. No se modificó: tomé sha256 de sus 148 archivos antes y después de la sesión y coinciden (`scripts_238a96c/site_hash_before.txt`).
- **Fecha:** 2026-09-29.
- **Runtime:** el comando documentado `npx --yes serve -l <p>` (serve 14.2.6 + `serve.json` `{"cleanUrls": false}`), con gzip. Navegador: Playwright Chromium 1194 headless. Lighthouse 13.5.0 con la misma build de Chromium.
- **CDN:** jsdelivr está bloqueado en el sandbox (403). En todas las ejecuciones, `@tailwindcss/browser@4` se redirigió al archivo vendorizado `tailwindcss-browser-4.3.3.js`. Para Lighthouse se usó una copia con el `src` reescrito a `vendor/tw.js` (`$SCRATCH/qa238/lhsite`). **Ninguna ejecución usó el CDN real.**
- **Evidencia:** `/home/claude/qa/evidence_238a96c/` (JSON y capturas). Scripts propios y logs: `/home/claude/qa/scripts_238a96c/`.
- **Autoridad:** C12_QA_GATE, C14, perfil `4geeks-public-website` (R01–R23), COPY_DECK_v2 (Project) = `wo/copy/copy_deck_v2.json` (sha `cc0438ed…`), `CONTEXT.md` (`wo/nexova-main`) para la procedencia.

## Resumen

| Clase | N | Ítems |
|---|---|---|
| **BLOCKING** | **2** | B1 contraste axe *serious* en las tarjetas C10 (≥1024 px, modo scrolly) · B2 H1 y CTA del hero ocultos en pantalla cuando falla un still del hero |
| NON_BLOCKING | 6 | N1 textos C11 fuera del deck · N2 titles ≠ slots del deck (desviación conocida) · N3 `<style>` fuera del bloque permitido · N4 móvil scrolly con ~40 % del escenario vacío · N5 video sigue reproduciéndose fuera del hero · N6 CTA fija visible sobre los beats apilados en reduced-motion |
| PARTIAL | 3 | scroll_feel (el modelo scrub no aplica al modo *triggered*) · Q02 axe moderate `page-has-heading-one` en scrolly · sin JS no hay estilos (estructural, ya conocido) |
| NOT_VERIFIED 👤 | 5 | PSI sobre URL pública (R15 oficial), push/rama remota (R19), URL de Codespaces (R20), R16 PR, R21 entrega; H.264/iOS Safari en dispositivo real; sensación de scroll |

**Veredicto: FAIL.** Hay 2 bloqueantes según C12 §4.5 (a11y *serious*; contenido oculto). Los dos se arreglan con cambios de una línea. Lighthouse, SEO, formulario, deep links, overflow y consola están en verde.

## 1. BLOQUEANTES

### B1 — Contraste insuficiente en "/ 04" de las tarjetas del hero (axe `color-contrast` serious) · R12 / C12 §4.5
- **Repro:** 1440×900 (también 1280×800 y 1024×768), movimiento por defecto. Cargar `index.html`, hacer un gesto de rueda y desplazarse al 35 %, 63 % o 90 % del hero (tarjetas P2, P3 y P4). Correr axe.
- **Observado:** en cada una de las 3 tarjetas, `<span class="text-lg text-marfil/50">/ 04</span>` da **4.09:1** (#818992 sobre #0E2A4A, 18 px normal) contra un mínimo de 4.5:1. axe lo marca *serious* aunque el `<p>` padre sea `aria-hidden`: el texto sigue siendo visible.
- **Evidencia:** `evidence_238a96c/bar_axe_238a96c.json` (`axe_1440_scrolly_*`), `scripts_238a96c/t_cc.mjs` (salida en el log de sesión), captura `hero_card_1440_0.9.png`.
- **Por qué no lo vio qa_smoke:** su axe solo corre en la carga inicial, cuando las tarjetas aún son `invisible`.
- **Causa:** `index.html` L287, L296 y L305 (`text-marfil/50`).
- **Fix mínimo:** `text-marfil/70` o más (y re-medir), o `text-miel`. Re-test: axe en las tarjetas P2–P4 a 1024, 1280 y 1440.

### B2 — Si falla la carga de un still del hero, el H1, la entradilla y la CTA "Solicitar servicio" pasan a `visibility:hidden` mientras siguen en pantalla · C12 §4.5 "contenido oculto" (misma clase que B4 de d8b60f4)
- **Repro:** abortar una de `assets/img/hero-p{1..4}-1440.webp` (p. ej. `route('**/hero-p3-1440.webp', abort)`). 1440×900. Cargar `index.html`, hacer un gesto de rueda y bajar a `scrollY=300`.
- **Observado:** `experience.js` quita `data-mode` y el hero vuelve al layout apilado, pero el bucle sigue llamando a `render()`, que vuelve a escribir `data-active=p2/p3/p4`. `[data-copy="p1"]` lleva `group-data-[active=p2..4]/hero:invisible`, así que:
  - a 1440, y=300: el H1 (254 px visibles) y la CTA (top 471) quedan ocultos. A y=450 la CTA (top 321) también queda oculta;
  - a 390×844, y=600: la CTA (top 170) queda oculta y queda un hueco marfil vacío.
  - Al subir otra vez se recupera.
- **Evidencia:** `stillfail_1440_y450.png` (hueco donde estaba el H1), `stillfail_390_y600.png` (hueco donde estaba la CTA), `hero_stillfail_1440x900_238a96c.json`, `scripts_238a96c/t_stillfail.mjs`.
- **Por qué pasa `QS-media-abort`:** depende de la temporización (el texto cambia a mitad de un volteo de 1.15 s). qa_smoke mide antes de que avance.
- **Causa:** `assets/js/experience.js` L187 (`render()` asigna `data-active` sin comprobar el modo), junto con L225 (la rama de fallo borra `mode`/`active` pero la escena sigue en `SC`).
- **Fix mínimo:** en `render()`, `if (!root.dataset.mode) { delete root.dataset.active; return; }` antes de L187, o sacar la escena de `SC` en L225.
- **Re-test:** `t_stillfail.mjs` a 1440 y 390 con esperas ≥1.6 s. H1 y CTA deben quedar `visible` en todo el recorrido.
- **Alcance:** solo en caso de fallo de red de un still (~30–80 KB) tras el primer gesto. En condiciones normales no ocurre. Solo se puede rebajar con una entrada en DECISION_LOG (C12 §4.9).

## 2. NO BLOQUEANTES

| # | Hallazgo | Evidencia | Sugerencia |
|---|---|---|---|
| N1 | **C11 añadió ~22 textos visibles que no están en COPY_DECK_v2** y que no aparecen registrados como desviación (solo se registraron los titles): bloque "En resumen" (h2 + 3 dt/dd + enlace), tabla comparativa (caption, th "Qué incluye"/"Equipo", 6 td), pista "Desliza la tabla…", numerales decorativos "02/03/04 / 04" (C10), aria-label "Acceso rápido a la solicitud" y el copy de 404.html (4 textos + title + description). **Ninguno inventa hechos:** todos salen de CONTEXT.md L7/L17/L19/L21 ("headhunting", 40/30/12 personas, canales, formatos) o de slots aprobados (PI-05 para "Para quién"). | `text_vs_deck_238a96c.json` | Registrar en el deck (decisión del operador) o alinear |
| N2 | Titles `index` "Consultora de recursos humanos en Valencia y Miami \| Nexova" y `application` "Solicitar selección, soporte o formación \| Nexova Solutions" ≠ IDX-META-TITLE / APP-META-TITLE (og:title y twitter:title igual). Es una desviación conocida y reversible: solo se reporta. | `text_vs_deck_238a96c.json` | Decisión del operador |
| N3 | `index.html` L52–57: segundo `<style>` fuera del bloque `text/tailwindcss` (safe-area del body y `body:has(#cta-movil) > footer`). El perfil §4 y el README dicen "CSS propio solo dentro del bloque". Los TOKENS siguen byte-idénticos entre páginas (diff = 0). | grep | Pasarlo a utilidades (`pb-[calc(...)]` en el footer, `px-[env(...)]`) o documentarlo como excepción |
| N4 | Móvil 390, hero anclado: ~40 % del escenario queda vacío bajo los beats (media 38svh + texto). No afecta a la legibilidad. | `hero_normal_390_down_p4.png` | Revisión visual humana |
| N5 | Al salir del hero por abajo, el video de P4 vuelve a empezar y se reproduce fuera de pantalla (una vez, ~2 s). Coste de CPU menor. | `hero_normal_1440x900_238a96c.json` estado `past-hero` | Pausar cuando `progress()` sale de [0,1] |
| N6 | Reduced-motion 390: la CTA fija aparece mientras se ven los beats apilados del hero (y 900–1800). En modo normal nunca aparece sobre el hero (0 muestras). | `bar_axe_238a96c.json` `bar_390_reduced.shownWhileHero` | Aceptable (patrón estándar de CTA fija); opcional: ocultarla mientras el hero intersecte |

## 3. Tabla por ítem

| # | Ítem | Resultado | Evidencia (medido) |
|---|---|---|---|
| 1a | qa_smoke `--strict` index + application, 390/768/1440, runtime documentado | **PASS** (exit 0) | console 0 · overflow 0 · axe 0 serious / 0 totales · links 55/0 rotos · seq antes de scroll 0 / con reduced 0 · nojs 34/34 headings index · firstviewport 2/2 (default, reduced, savedata) · reduced 0/45 y 0/25 con movimiento · savedata scrolly 0 · media_abort 0 textos perdidos · deeplinks ×3 200 sin redirección. `qa_smoke_238a96c.json`, `qa_smoke.log` |
| 1b | axe en estados que qa_smoke no cubre | **FAIL (B1)** | 1440/1280/1024 scrolly P2–P4: `color-contrast` serious ×1. 768/390 scrolly: solo `page-has-heading-one` moderate (Q02, PARTIAL). Formulario en estado de error: 0 serious. Con la CTA fija visible: 0 serious |
| 1c | Consola / scroll horizontal | **PASS** | 0 errores en recorridos normales a 390/768/1440 (solo un aviso `willReadFrequently`, provocado por mi propio `getImageData`). Overflow 0 también en estados scrolly |
| 2 | Lighthouse móvil ×3 (LAB-LOCAL, gzip, Tailwind local) | **PASS** (≥80 en las 4 categorías) | **index:** r1 98/100/100/100 · r2 98/100/100/100 · r3 96/100/100/100 → **mediana 98/100/100/100** (LCP 2.1–2.3 s, CLS 0.001, TBT 70–150 ms, 229 KB). **application:** r1 95/100/100/100 · r2 96/100/100/100 · r3 96/100/100/100 → **mediana 96/100/100/100** (LCP 2.3 s, CLS 0–0.001, TBT 110–150 ms, 211 KB). Desktop ×1: 100/100/100/100 ambas. SEO = 100 (SEO-22 ✓). `lh_*_238a96c.report.{json,html}` |
| 3 | seo_check `--phase now --strict` (estático y `--render`) | **PASS** | 17 PASS · 0 FAIL · 0 WARN · 4 N/A (DEP) · 9 MANUAL, exit 0 en los dos modos. `seo_check_238a96c.json`, `seo_check_render_238a96c.json` |
| 4a | Video solo tras el gesto | **PASS** | 0 requests de video y 4× `src=null` tras 3 s de reposo, a 1440 y 390. Tras el gesto: g1+g2, y luego g3 y g4 al llegar (precarga de la siguiente persona). Desktop `-720.webm`, móvil `-m.webm` (VP9 elegido por canPlayType) |
| 4b | Ida y vuelta | **PASS** | Bajada P1→P4 y subida P4→P1 a 1440 y 390: `data-active` correcto, el video de la persona activa pasa a opacity 1 y avanza a 1× (≈1.6 s a los 2.5 s de llegar = volteo de 1.15 s + reproducción), los demás en pausa. Flick 95 %→5 %→60 % acaba en P3 reproduciendo. Canvas nunca en blanco. `hero_normal_*` |
| 4c | Fallback si falla el video | **PASS** | `assets/video/**` abortado: los stills del canvas se mantienen, el texto de las tarjetas se ve y el ciclo sigue. Los errores de consola que aparecen los provoca el abort (esperado). `hero_videofail_*` |
| 4d | Fallback si falla un still | **FAIL (B2)** | Ver B2 |
| 4e | Reduced-motion / Save-Data | **PASS** | 1440 reduced: sin `data-mode`, 0 `<video>`, 0 requests a video/seq, 4 beats visibles apilados. Save-Data: scrolly 0 (qa_smoke) |
| 4f | Tarjetas legibles y nunca tapadas | **PASS salvo B1** | 1440: panel tinta 576 px, texto marfil 46 px. elementFromPoint en 3 puntos por línea = la propia tarjeta en todos los estados. Móvil: texto sobre marfil, bajo la media, sin solape. `hero_card_1440_0.9.png`, `hero_normal_390_down_p4.png` |
| 4g | CTA fija móvil ≤767 | **PASS** | 390 default: nunca visible con el hero en pantalla; aparece solo cuando no hay otra CTA visible; al final de la página queda oculta (el footer tiene padding-bottom 76 px, último texto en 744 < 844). 768: nunca visible. Sin JS: `hidden`. Con reduced-motion: N6. `cta_bar_390_default.png`, `page_end_390_*.png` |
| 4h | scroll_feel `--strict` 1440/390 | **PARTIAL (N/A por diseño)** | exit 1 en los dos viewports: S2 FAIL y S3–S5/S7/S8/M2/M4/M5 N/A. El hook publica `mode:'triggered'` sin `visual` ni `segments`: el modelo scrub de C05 no aplica al tempo propio de C8 (el builder lo anotó en C8; **no hay entrada en DECISION_LOG** en lo revisado). Lo que sí aplica pasa: S1 0 hallazgos · S6/M3 0.59 % >33 ms, máx. 33.4 ms (1440) / 0 % (390) · S9 159/152 ms · S10 a/b OK (anclado 55.5 % / 38.7 %). Sustitutos medidos en 4a–4c. `scroll_feel_*_238a96c.json` |
| 5 | Formulario + validation.js | **PASS** | 38/38 aserciones a 390 y 1440: `?tipo=seleccion/soporte/formacion` preselecciona y abre su sub-bloque (con serve, 200 y query conservada), `candidatura` se ignora, envío vacío bloqueado (≥9 aria-invalid, foco en nombre, resumen "Revisa N campos"), 6 mensajes exactos del deck con prefijo "Error:" y aria-describedby, revalidación en input, límites (numPosiciones 100), desmarcar limpia el sub-bloque, reset restaura, éxito "Gracias, Marta." con foco en el panel y **0 requests de red**, "Nueva solicitud", consola 0. `form_238a96c.json`, `form_errors_390.png`, `form_success_390.png` |
| 6a | Textos ⊆ deck | **PARTIAL (N1, N2)** | index: 33 textos fuera del deck. 7 ya estaban registrados en d8b60f4 (alts de la oficina, aria-label de nav, opciones placeholder, sr-only); el resto son nuevos de C10/C11. application: 12 (todos ya registrados + titles). 404: 8. `text_vs_deck_238a96c.json` |
| 6b | 0 afirmaciones inventadas | **PASS** | Todas las cifras y servicios nuevos trazan a CONTEXT.md L7/17/19/21. Sin testimonios, garantías ni ratings |
| 6c | JSON-LD coherente con lo visible | **PASS** | Organization (2011, 120, Valencia/Miami, CEO Laura Mendoza, 3 servicios con descripción = deck, `knowsAbout` "Headhunting" visible en la tabla), WebSite, FAQPage 6/6 literal (SEO-12). application: WebPage "Solicitud de servicio" + isPartOf/about. Sin teléfono, email ni LocalBusiness |
| 7 | Restricciones del perfil verificables en local | **PASS** | R01 los 3 archivos en raíz; `validation.js` cargado ×1 · R03 sin framework ni build · 0 `package.json` · R04 `npx --yes serve -l 3000` documentado en README_APPEND y probado (200, query conservada, 404 → 404.html) · R10 `@tailwindcss/browser@4` ×1 por página, 0 `cdn.tailwindcss.com` (N3) · R13/R17 ✓ · R14 ✓ · R18 ✓ · R22 ✓ · R23 reduced/Save-Data ✓. R02 CONTEXT.md: no aplica aquí (no forma parte de la copia) |
| 8 | Capturas revisadas a mano | **Hecho** | `hero_normal_1440_down_p1.png` (H1, entradilla y CTA legibles sobre el degradado) · `hero_card_1440_0.9.png` (tarjeta C10 correcta; "/ 04" tenue = B1) · `index_html_390x844_fv_default.png` (CTA entera en el primer viewport) · `hero_normal_390_down_p4.png` (N4) · `cta_bar_390_default.png` (barra correcta) · `stillfail_*` (B2) |

## 4. Limitaciones

- Tailwind vendorizado 4.3.3 en lugar de jsdelivr `@4` flotante. Lighthouse es LAB-LOCAL; el valor oficial es PSI sobre la URL pública de Codespaces (👤).
- Chromium open-source: solo se probó VP9/WebM. H.264/MP4 (Safari/iOS) y la reproducción muted+playsinline en iPhone no se verificaron (👤, dispositivo real).
- Móvil emulado ≠ dispositivo real. **Sensación de scroll: `PENDIENTE_HUMANO`** (C12 §4.6; checklist C13 §D).
- No se verificaron el árbol remoto, el PR, el hash de CONTEXT.md ni la fidelidad a Figma.
- Evidencia atada a `238a96c`: cualquier commit posterior la deja `STALE`.

---

## Re-verificación (working tree sobre 238a96c, fix de B1 + B2)

- **Revisión probada:** `/home/claude/site` con los cambios del builder, que no tienen commit. Diff de hashes contra la línea base de 238a96c: **solo cambian 2 archivos**.
  - `index.html`: sha `e9d72e5a…`. Las 3 spans "/ 04" pasan de `text-marfil/50` a `text-marfil/70` (L287/296/305).
  - `assets/js/experience.js`: sha `cb606937…`. Se añade L186 `if (!root.dataset.mode) { delete root.dataset.active; return; }` al principio de `render()`.
  - No cambia nada más. No modifiqué el sitio: los hashes son iguales antes y después de la re-verificación.
- **Evidencia:** `/home/claude/qa/evidence_238a96c_rv/`. Mismo runtime y mismas limitaciones que arriba (Tailwind 4.3.3 vendorizado, LAB-LOCAL).

| Ítem | Resultado | Evidencia (medido) |
|---|---|---|
| B1 · axe `color-contrast` en tarjetas P2–P4 a 1024/1280/1440 (scrolly 10/35/63/90 %) | **CERRADO** | 0 violaciones en los 12 estados (`b1_axe.log`) |
| B2 · abort `hero-p3-1440.webp`, 1440 y 390 | **CERRADO** | H1 y CTA `visible` en y = 0…800 en los dos viewports: a 1440, y=300 con el H1 en pantalla y y=450 con la CTA en top 321; a 390, y=600 con la CTA en top 170 (`b2_p3.log`, `stillfail_p3_1440_y450.png`, `stillfail_p3_390_y600.png`, revisada: CTA visible, sin hueco) |
| B2 · abort `hero-p1-1440.webp`, 1440 y 390 | **CERRADO** | Mismo resultado (`b2_p1.log`, `stillfail_p1_*.png`) |
| Regresión · hero normal (sin fallo) 1440 y 390 | **PASS** | 0 requests de video antes del gesto. P1→P4→P1 y flick: `data-active` correcto y el video activo a 1× (≈1.6 s a los 2.5 s de cada llegada); canvas nunca en blanco (`hero_normal_*_238a96c.json`, capturas `hero_normal_*`) |
| Regresión · qa_smoke `--strict`, 2 páginas × 3 viewports, runtime documentado | **PASS** (exit 0) | console 0 · overflow 0 · axe 0/0 · 55 enlaces sin rotos · seq 0/0 · nojs, firstviewport, reduced, savedata, media-abort y deeplinks ×3 en verde (`qa_smoke_rv.log`) |
| Regresión · seo_check `--phase now --strict` | **PASS** (exit 0) | 17 PASS · 0 FAIL · 0 WARN (`seo_rv.log`) |
| Regresión · Lighthouse móvil ×1 (P/A/BP/SEO) | **PASS** | index **96/100/100/100** (LCP 2.4 s, CLS 0.001, TBT 160 ms) · application **97/100/100/100** (LCP 2.3 s, CLS 0, TBT 100 ms). Dentro de la varianza de las corridas anteriores (index 96–98, application 95–96) |

**Veredicto actualizado: PASS con observaciones.**
- 0 BLOCKING.
- Siguen abiertos N1–N6 (no bloqueantes), PARTIAL de scroll_feel (modo *triggered*, falta la entrada en DECISION_LOG), PARTIAL de Q02 y las filas NOT_VERIFIED 👤: PSI público, push/PR/Codespaces, H.264/iOS, sensación de scroll `PENDIENTE_HUMANO`.
- Esta evidencia vale para el working tree actual. Cuando se haga el commit de este fix, conviene comprobar que el sha nuevo contiene exactamente estos dos hashes (`e9d72e5a…`, `cb606937…`); si no, queda `STALE`.
