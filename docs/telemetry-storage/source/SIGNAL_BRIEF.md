# SIGNAL — brief para ejecución académica 4Geeks

## Alcance y autoridad
Perfil ACADÉMICO: herramientas y entregables educativos, no una oferta comercial ni una asociación oficial.
Orden de autoridad: enunciado oficial 4Geeks > este encargo académico > SIGNAL DESIGN.md v4 > contratos v4 > tokens > fundación histórica > referencias.
Resolver conflictos a favor de la rúbrica y documentarlos; no cambiar el stack o restricciones para imponer SIGNAL.
No inventar autoría, colaboradores, clientes, métricas ni aprobación de marca. Nunca enviar al LMS ni hacer merge.
Leer DESIGN.md, contracts/, COPY-UX-RULES.md, QA-ACCEPTANCE.md y brand/README.md del ZIP.
reference-code/ son fragmentos históricos, NO una aplicación ni una certificación. Adaptar, no copiar sus defectos.

## Instalación y tokens exactos
Rutas relativas en el ZIP: tokens/tokens.json (fuente de valores), tokens/tokens.css (base),
tokens/motion.json y tokens/motion.css (extensión normativa v4; importar después de la base).
Conservar nombres semánticos. No mezclar otro tema; base clara. rem corresponde a raíz 100%, no bloquear preferencias.
### Colores (`--color-<nombre>`)
- `--color-canvas`: `#F7F8FA`.
- `--color-surface`: `#FFFFFF`.
- `--color-ink`: `#18202B`.
- `--color-muted`: `#505E70`.
- `--color-border`: `#788598`.
- `--color-subtle`: `#E7ECF2`.
- `--color-action`: `#B53A17`.
- `--color-on-action`: `#FFFFFF`.
- `--color-action-hover`: `#8F2D12`.
- `--color-action-pressed`: `#73230E`.
- `--color-selected`: `#FCEDE6`.
- `--color-focus`: `#164DCC`.
- `--color-danger`: `#A32A26`.
- `--color-success`: `#236344`.
- `--color-warning`: `#765000`.
- `--color-info`: `#204EA0`.
- `--color-on-status`: `#FFFFFF`.
- `--color-overlay`: `rgba(0,0,0,.56)`.
- `--color-link`: `#B53A17`.
### Espaciado (`--space-<n>`, valores en px a raíz 16px)
`--space-0`=0; `--space-1`=4; `--space-2`=8; `--space-3`=12; `--space-4`=16; `--space-5`=20; `--space-6`=24; `--space-8`=32; `--space-10`=40; `--space-12`=48; `--space-16`=64; `--space-20`=80; `--space-24`=96; `--space-28`=112; `--space-32`=128.
### Geometría y tipo
- `--radius-control` y `--radius-card`: 8px (.5rem); `--radius-pill`: 999px sólo tags/badges semánticos.
- `--container`: 1280px (80rem); `--measure`: 68ch; `--gutter`: 16px (<640), 24px (640–1023), 40px (>=1024).
- `--section`: 80px escritorio / `--section-mobile`: 48px; `--header`: 72px / 64px móvil.
- Bordes 1px, selección/foco 2px sin salto de geometría. `--shadow-none`: none;
  `--shadow-overlay`: 0 16px 48px rgba(0,0,0,.16), sólo overlays.
- `--font-body` / `--font-display`: Arial, Helvetica, sans-serif. `--font-mono`: Consolas, "Courier New", monospace, sólo datos técnicos/código.
- Cuerpo 16/24; lead 20/30; UI 14/20; caption >=12/16. Título peso700.
- `--text-display`: clamp(2.5rem, 1.5rem + 4vw, 4.5rem), leading1.05, tracking-.03em.
- `--text-h2`: clamp(2rem, 1.3rem + 2vw, 3rem), leading1.15. h3 24/30.
- No fuentes remotas ni Georgia en UI. La serif del logo exacto no se modifica.
- Estados semánticos sólo para estados reales; selected usa tinta, acción primaria con texto blanco.

## Composición y anti-genéricos
Contenido antes de layout: registrar por bloque público, pregunta, hechos/fuente y acción siguiente.
Aplicaciones operativas: título/acción, filtros, tabla/lista y detalle; NO imponer hero comercial a un dashboard.
Landing si procede: hero asimétrico7/5 con una acción y demostración real; no cajas vacías que simulan producto.
Evitar tres cards idénticas por costumbre, bento vacío, pills ornamentales, sombras por fila, glassmorphism,
gradientes neón/lila, orbes, rayos/cerebros universales, coordenadas/slashes “01 /”, métricas/testimonios falsos.
Eliminar slogans intercambiables (“Precisión, sin ruido”, “a otro nivel”, “X, sin Y”). Copy concreto de la tarea;
CTA con verbo y objeto; demo rotulada y sin atribuir datos ficticios a personas reales.
Cada componente justifica contenedor y función; tablas para comparación, listas para proceso.

## Estados, rutas y accesibilidad
Por cada petición: idle → loading → success | empty | error; conservar datos al refrescar y entradas al fallar.
Carga accesible, vacío con siguiente acción, error legible con reintento; nunca porcentajes falsos.
Default/hover/focus-visible/active/disabled; prevenir doble envío y respuestas obsoletas; éxito sólo tras confirmación.
Inventariar rutas/estados con templates/; 404 real y errores seguros según arquitectura. No agregar páginas sin función.
Privacidad/consentimiento sólo según datos y terceros reales; sin trackers o banners ficticios.
Objetivo WCAG 2.2 AA: texto >=4.5:1 (grande>=3:1), controles/foco>=3:1; no depender sólo del color.
Outline2px offset3px visible, sin recorte; botones/objetivos>=44px, campos>=48px y labels persistentes.
Landmarks, skip link, h1 editorial por ruta, lang real; alt contextual / vacío si decorativo.
Teclado completo, Escape/restaurar foco en modal, estados anunciados; no interacción exclusiva de hover/drag.
Probar texto200%, zoom400%, reflow320px, forced-colors y axe sin serious/critical; no certificar WCAG por score.

## Responsive, motion y SEO
Verificación OBLIGATORIA a 390/768/1280 CSS px; capturas reales de cada ancho y estados aplicables.
Complementar matriz del kit 320/1024/1440/1920; sin overflow del documento; tablas con scroll local etiquetado.
Retícula4/8/12 columnas; colapsar antes de comprimir; conservar orden DOM.
Motion2D sólo cuando explica estado/relación. Aplicación académica no necesita hero o arte ornamental para cumplir.
Si hay hero/proceso significativo: entrada automática y registro visible, no sólo botón Repetir.
CSS/WAAPI/IntersectionObserver primero; sin WebGL, 3D, scroll-jacking, cursor personalizado o loops decorativos.
Microfeedback120ms, estado180ms, registro560ms, conexión240ms; easing cubic-bezier(.2,.8,.2,1).
Máximo una secuencia principal/viewport <=1600ms (hero<=1200ms). Texto/CTA legibles desde primer paint.
Puntero sólo en arte útil con fine/hover: <=6px, raster<=2.4px; sin mover hit targets ni animar logos.
Respetar prefers-reduced-motion desde primer paint Y al cambiar: cancelar WAAPI/rAF/timers/listeners,
limpiar transforms y mostrar estado final; coarse/touch sin seguimiento; sin JS debe seguir útil.
Fichas de efectos: propósito, trigger, duración, amplitud, cleanup, fallback y evidencia.
SEO COMPLETO sólo en landings públicas: title/description, canonical con dominio confirmado,
OG, robots/sitemap, HTTP status, schema sólo hechos verificables y enlaces rastreables.
En apps internas/CLI/API: semántica y metadata aplicables, no inventar campañas, dominio, schema ni sitemap.
Previews públicos: noindex verificable; robots no protege privacidad. No publicar producción sin autorización.

## Assets y lockup exactos
Usar `brand/lockups/signal-horizontal.svg` en footer discreto (mínimo400 CSS px).
En móvil usar `brand/lockups/signal-stacked.svg` (mínimo280 CSS px); no comprimir horizontal por debajo del mínimo.
Variantes permitidas según fondo: `brand/lockups/signal-mono.svg`, `brand/lockups/signal-reverse.svg`.
Procedencia/mínimos: `brand/README.md`; safe area>=24 unidades del viewBox, proporcional; conservar proporciones.
Originales: `brand/originals/4geeks.png`, `brand/originals/divinivid.svg`.
No redibujar, reescribir, recomprimir ni regenerar SVG/PNG/WebP. Copiar bytes exactos y conservar procedencia.
No inferir colaboración/endorsement oficial ni agregar colaboradores por usar este crédito visual.
Miguel aceptó el riesgo del lockup 4Geeks × Divinivid: incluir en footer UI sin competir con producto.
Si enunciado lo impide, omitir y documentar regla/motivo/evidencia en EXCELLENCE_REVIEW.md.
Las capturas de referencias son investigación, nunca fondos o assets redistribuidos como propios.
Verificar hashes SHA256 contra MANIFEST.json antes/después; cambiar asset sin permiso es FAIL.
Desde raíz descomprimida (sólo archivos presentes, pues el manifest original también inventaría referencias omitidas):
```bash
python3 - <<'PYVERIFY'
import json, pathlib, hashlib
for e in json.load(open('MANIFEST.json'))['files']:
    p=pathlib.Path(e['path'])
    if p.is_file():
        assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'], str(p)
        print('PASS', p)
PYVERIFY
sha256sum brand/lockups/signal-horizontal.svg brand/lockups/signal-stacked.svg
```
Además verificar que cada asset efectivamente usado existe en manifest; comparar su destino con hash original.

## Proyectos sin frontend
CLI/API/docs: aplicar lenguaje preciso, estados/errores claros, jerarquía y ejemplos reproducibles en README/terminal.
No imponer colores ANSI si perjudican legibilidad ni agregar UI sólo para mostrar marca.
Lockup NO APLICA salvo que exista UI; docs HTML propias sí usan tokens/tipo/AA/responsive pertinentes.
CLI: evidenciar comandos reales; API: requests/responses/tests y docs; capturas/video de UI sólo si hay UI.

## Evidencia y entrega
Capturas 390/768/1280 con commit/build y un video corto real (5–10s) del recorrido, carga/scroll/interacciones.
Si hay motion, video sin Repetir, reduced antes/durante y puntero; captura fija no demuestra motion.
Build/lint/typecheck y tests disponibles, consola/red, teclado, contraste, hash y matriz DESIGN-QA.md.
Presupuestos JS<=170KiB gzip, CSS<=40KiB, primera pantalla móvil<=1MiB, LCP image<=220KiB;
objetivos LCP<=2.5s, CLS<=.10, INP<=200ms. Laboratorio390×844 CPU×4/red150ms 1.6Mbps,3 corridas.
No afirmar resultados o fps no medidos; NO EJECUTADO no es PASS; NO APLICA lleva razón.
Entregar RUBRIC_JUSTIFICATION.md con cada criterio y evidencia, EVIDENCE_MANIFEST.yaml,
EXCELLENCE_REVIEW.md, DESIGN-QA.md y TELEMETRY (tokens reales/null si no medidos, tiempo, iteraciones, reparaciones).
Al menos un extra visible y uno técnico sin sustituir requisitos. Control Tower eval→repair hasta cierre comprobado.
Revisión del ejecutor no es aprobación visual del dueño. No marcar READY_TO_SUBMIT antes de revisión del Orquestador.
No merge, no LMS, sin secretos en cliente/repo/logs/capturas; nunca mostrar FOURGEEKS_API_TOKEN.
