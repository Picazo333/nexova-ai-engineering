# SOURCE — 021 ai-eng-milestone-backend-development

Fecha de lectura: 2026-11-06.

## Enunciado

- Inglés: `content/projects/ai-eng-milestone-backend-development/README.md` en el syllabus `fd2da034894ba93ba738559280ccde074ab1d953`.
- SHA256 del archivo leído: `83906f828588290dec53501448c253665284226083bbcf6e133524801d3f1903`. Coincide con `PROVENANCE.json`.
- Español: SHA256 `47eeaea5a8fdf1255cc2224b8802d633c2db5f0904fe9a51eab97ce9ee6cc6e0`. Coincide.
- `learn.json`: SHA256 `84dbc9fcb4fd72eb3861cf5987b74bc51dc2a9c4f3db3648f4b8deecd6a94392`. Coincide.

## Briefing de Nexova

El enunciado manda leer el briefing de `content/contexts/05-backend-development` antes de nombrar entidades. Para Nexova son `Asset`, `AssetEntry` y `AssetExit`.

Copias guardadas en `source/`:

- `nexova-BRIEFING.en.md` — SHA256 `34a829fd735a5a7724a5b87993d99de4df038ba1f4ef59e593d171da35cb9138`. Nombres, SKU, categorías y oficinas de la semilla salen de aquí.
- `nexova-BRIEFING.es.md` — SHA256 `f63d6e046724070dabb9663c6c5ce198c7b3e1b7f33e3f272500a7b2f43b0b66`. Traduce los mismos seis activos. El mensaje de stock insuficiente está en inglés en las dos versiones.

## Cláusula anti-IA

Se buscó en el README en inglés y en español, y en el briefing de Nexova, alguna prohibición de usar IA o una exigencia de escritura manual («No utilices herramientas de IA», «Do not use AI tools», «write each one yourself», «escrito por ti», «sin copiar», «no uses ChatGPT»). No aparece. El trabajo sigue.

## Autoridad

Enunciado 4Geeks, luego el briefing de Nexova, luego este encargo. SIGNAL no añade una UI: el hito no pide pantallas. El lockup no se copia.

## Base de código

`feature/company-monorepo-container` en `2232caf225a0e899fea4c93ab83ce2f36ecdfafe` (PR #22). La API y el JWT de TinyDB ya están en `services/api`. Este hito no crea otro servicio.
