# Public website — Nexova Solutions (4Geeks · caso académico, empresa ficticia)

Sitio público estático: `index.html` (13 secciones, hero inmersivo con video por persona, oficina panal), `application.html` + `validation.js` (formulario con validación y envío simulado), `404.html`, `robots.txt`, `llms.txt`. Sin build ni `package.json`; Tailwind v4 por runtime de navegador.

## Cómo servirlo

```bash
npx --yes serve -l 3000
```

En Codespaces: puerto 3000 → Port Visibility → **Public**.

## Performance — gate final

4Geeks exige Performance ≥80 (ideal >90) y permite **Lighthouse** como fallback cuando PageSpeed Insights no puede alcanzar/completar el análisis del preview.

### Evidencia final persistida

Auditoría móvil sobre el source commit `2162745a4537cc1034d54264330c68d693348b13`, servido con el comando documentado:

| Métrica | Resultado |
|---|---:|
| Performance | **100** |
| Accessibility | **100** |
| Best Practices | **96** |
| SEO | **91** |
| FCP | **0.7 s** |
| LCP | **0.7 s** |
| TBT | **10 ms** |
| CLS | **0** |

- Captura: `docs/public-website/evidence/lighthouse-mobile.png`
- Reporte JSON: `docs/public-website/evidence/lighthouse-mobile.report.json`
- Preview público del source auditado: https://raw.githack.com/Picazo333/nexova-ai-engineering/2162745a4537cc1034d54264330c68d693348b13/index.html
- PageSpeed se intentó durante el cierre; el servicio externo no completó una medición utilizable (rate limiting / acceso del preview). Se usa el fallback Lighthouse permitido por la rúbrica.
- No se inventó una URL de Codespaces: la URL forwarded exacta no quedó persistida. El preview público anterior permite inspeccionar el mismo source auditado.

![Lighthouse mobile evidence](https://raw.githubusercontent.com/Picazo333/nexova-ai-engineering/ef0bb275c6b09bbfa13fc795147e21b1dad82a30/docs/public-website/evidence/lighthouse-mobile.png)

## Lighthouse previo / regresión C12

Orden: Performance / Accessibility / Best Practices / SEO.

| Página | Mediana (3 corridas) | Tras C12 |
|---|---|---|
| index.html | **98 / 100 / 100 / 100** | 96 / 100 / 100 / 100 |
| application.html | **96 / 100 / 100 / 100** | 97 / 100 / 100 / 100 |

Desktop: 100 / 100 / 100 / 100 en ambas.

## QA independiente

Veredicto final: **PASS con observaciones, 0 bloqueantes** (`docs/public-website/QA_REPORT_238a96c.md`).

- `qa_smoke --strict`: 2 páginas × 390/768/1440 — axe 0 serious/critical, consola 0, overflow 0, sin JS, reduced-motion, Save-Data y media abortada.
- `seo_check`: 17 PASS / 0 FAIL.
- Formulario: 38/38 aserciones, `?tipo=` preseleccionado, 0 requests al enviar.
- Los 2 bloqueantes detectados por QA (contraste del numeral y contenido del hero oculto ante fallo de still) quedaron corregidos en C12.

## Observaciones abiertas — no bloqueantes

- Titles/OG orientados a búsqueda difieren de los slots aprobados `IDX-META-TITLE` / `APP-META-TITLE` (mismas afirmaciones reordenadas; reversible).
- ~22 textos nuevos de C10/C11 derivan de `CONTEXT.md` y slots aprobados; pendientes de registrar en copy deck.
- Móvil: hueco en hero a 390 px; con reduced-motion la CTA fija aparece sobre los beats; video P4 sigue reproduciéndose al salir del hero.
- Sensación de scroll y H.264 en iOS Safari siguen como revisión de dispositivo real, no bloqueante.

## Estado de entrega

- Rubric QA: **PASS**
- Performance: **PASS**
- Vercel check: **PASS**
- Evidencia remota: **persistida en el repo**
