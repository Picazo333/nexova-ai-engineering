# Public website — Nexova Solutions (4Geeks · caso académico, empresa ficticia)

Sitio público estático: `index.html` (13 secciones, hero inmersivo con video por persona, oficina panal), `application.html` + `validation.js` (formulario con validación y envío simulado), `404.html`, `robots.txt`, `llms.txt`. Sin build ni `package.json`; Tailwind v4 por runtime de navegador.

## Cómo servirlo (local o Codespaces)

```bash
npx --yes serve -l 3000
```

En Codespaces: puerto 3000 → Port Visibility → **Public**.

## Lighthouse (móvil, laboratorio local)

Orden: Performance / Accessibility / Best Practices / SEO. Mediana de 3 corridas en `238a96c`; 1 corrida de regresión tras los fixes de QA (C12).

| Página | Mediana (3 corridas) | Corridas | Tras C12 |
|---|---|---|---|
| index.html | **98 / 100 / 100 / 100** | 98 · 98 · 96 | 96 / 100 / 100 / 100 |
| application.html | **96 / 100 / 100 / 100** | 95 · 96 · 96 | 97 / 100 / 100 / 100 |

Desktop (1 corrida): 100 / 100 / 100 / 100 en ambas. index: LCP 2.1–2.4 s, CLS 0.001. application: LCP 2.3 s, CLS 0.

> PageSpeed Insights sobre la URL pública del Codespace: **pendiente** (se agrega aquí al publicar el puerto).

## QA independiente

Revisor distinto del builder. Veredicto sobre C12: **PASS con observaciones, 0 bloqueantes** (`docs/public-website/QA_REPORT_238a96c.md`).

- qa_smoke `--strict`: 2 páginas × 390/768/1440 — axe 0 serious/critical, consola 0, overflow 0, sin JS, reduced-motion, Save-Data, media abortada.
- seo_check (fase sin dominio): 17 PASS / 0 FAIL.
- Formulario: 38/38 aserciones, `?tipo=` preseleccionado, 0 requests al enviar.
- 2 bloqueantes encontrados en `238a96c` y corregidos en C12: contraste del numeral "/ 04" de las tarjetas; texto del hero oculto si falla un still.

## Observaciones abiertas (no bloqueantes)

- Titles/OG orientados a búsqueda difieren de los slots aprobados `IDX-META-TITLE` / `APP-META-TITLE` (mismas afirmaciones reordenadas; reversible).
- ~22 textos nuevos de C10/C11 (resumen, tabla, 404) derivan de CONTEXT.md y slots aprobados; pendientes de registrar en el copy deck.
- Móvil: hueco en el hero anclado a 390 px; con reduced-motion la CTA fija aparece sobre los beats; el video de P4 sigue reproduciéndose al salir del hero.
- Sensación de scroll y H.264 en iOS Safari: pendiente de revisión en dispositivo real.

## Commits

C2–C6 build y reparaciones de QA · C7–C9 scroll del hero (video real por persona) · C10 tarjetas del hero · C11 SEO sin dominio · C12 fixes de QA.
