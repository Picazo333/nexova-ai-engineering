# ASSET_MANIFEST — Nexova public website (Storyboard v3)

Generado el 2026-09-29. Los masters **no** están en el repo: viven en `C:\Users\migue\Desktop\Repos\_nexova_media_v3\masters_silent\` (clips de Google Flow, sin audio) y en Figma `jtODuK6vOsigUDQn0M3MP8` (página 05 · Storyboard v3).

## Masters (sha256)

| Master | sha256 |
|---|---|
| `G1opt_consultora_guino_1080p.mp4` | `9bb927c1230fbc29629018a0a68e44a10123416ac57a46541ae5bb9cd835cda5` |
| `G2_saluda_1080p.mp4` | `6a0330b80b14d9a5d690eece08d75ab7733bc8f2987a9b9ec7a209c82459cbe8` |
| `G3_lengua_1080p.mp4` | `6f4baf043fffb270dc782b504d78cfd819b5f3b859790ef4092dbc5892401f76` |
| `G4_guino_1080p.mp4` | `f8b11e87220982ad0bb2e08648f82d65dc45b88a8719c1594a5ebb2ef6860a0b` |
| `V-O1_desarme_parcial_1080p.mp4` | `8e7bb9fa86d2776d71de18c6f6eba8c3c906bc652641dd71da8e60acd5a0b71e` |
| `V-O2_personas_1080p.mp4` | `6459c218387588f27175d369b840dc60cd9e497b6c6edfd4931d311d49f8b9f8` |

## Derivación (reproducible)

- **Stills del hero** `assets/img/hero-p{1..4}-*.{avif,webp}`: fotograma 0 de G1/G2/G3/G4 (`ffmpeg -frames:v 1`). El still coincide exactamente con el primer fotograma de su gesto. Desktop 16:9 (1024/1440/1920); mobile = recorte 4:5 x 1056–1920 (480/800). Pillow AVIF q42–45 speed 4, WebP q72 method 6.
- **Stills de la oficina** `assets/img/office-o{1,2,3}-*`: o1 = último fotograma de V-O1 (paredes separadas); o2 = fotograma 0 de V-O2 (oficina armada); o3 = último fotograma de V-O2 (oficina viva). 1280/1920.
- **Secuencias** `assets/seq/<id>/NNN.webp` (libwebp, compression_level 6):
  - g1: G1 · crop 864×1080 @x1056 → 576×720, 8 fps, q38
  - g2: G2 · cuadro completo → 1152×648, 7 fps, q38 (la mano cruza el lado izquierdo)
  - g3: G3 · crop → 576×720, 8 fps, q38
  - g4: G4 · crop → 576×720, 9 fps, q38
  - o1: V-O1 0–2.4 s **invertido** → 1280×720, 10 fps, q46 (paredes que se cierran)
  - o2: V-O2 → 1280×720, 6 fps, q40
- **Fuentes**: Newsreader variable (latin, wght) + Inter 400/500/600 (latin), @fontsource, OFL.
- **Marca**: Logo B aprobado (`assets/brand/*.svg`, `assets/favicon.svg`), vector redibujado en Figma.

## Derivados

| Archivo / carpeta | Fotogramas | Peso | sha256 (archivo) o del listado |
|---|---|---|---|
| `assets/img/hero-p1-1024.avif` | — | 18 KB | `e653f79b26041b75…` |
| `assets/img/hero-p1-1024.webp` | — | 39 KB | `75e8320e8fdb0112…` |
| `assets/img/hero-p1-1440.avif` | — | 32 KB | `7b428111bdf6b5fc…` |
| `assets/img/hero-p1-1440.webp` | — | 66 KB | `80f91a295e6a1e09…` |
| `assets/img/hero-p1-1920.avif` | — | 56 KB | `bd9f23cbf2375890…` |
| `assets/img/hero-p1-1920.webp` | — | 97 KB | `691c396171db71e9…` |
| `assets/img/hero-p1-m-480.avif` | — | 15 KB | `35e5c788a7e5e252…` |
| `assets/img/hero-p1-m-480.webp` | — | 35 KB | `42441644233b334a…` |
| `assets/img/hero-p1-m-800.avif` | — | 33 KB | `2b9e3d56ac141dbf…` |
| `assets/img/hero-p1-m-800.webp` | — | 70 KB | `232b70368837a80b…` |
| `assets/img/hero-p2-1440.avif` | — | 29 KB | `6c9e6424159cb787…` |
| `assets/img/hero-p2-1440.webp` | — | 66 KB | `d4224edc636e70a0…` |
| `assets/img/hero-p2-m-480.avif` | — | 17 KB | `8a76942de58b9275…` |
| `assets/img/hero-p2-m-480.webp` | — | 40 KB | `b3592ec18b6521a6…` |
| `assets/img/hero-p2-m-800.avif` | — | 36 KB | `d181f34fb326edeb…` |
| `assets/img/hero-p2-m-800.webp` | — | 78 KB | `da537585da2fc15f…` |
| `assets/img/hero-p3-1440.avif` | — | 22 KB | `6ba965f3778d0447…` |
| `assets/img/hero-p3-1440.webp` | — | 46 KB | `cdaac065354f0950…` |
| `assets/img/hero-p3-m-480.avif` | — | 11 KB | `053482ab7d53c719…` |
| `assets/img/hero-p3-m-480.webp` | — | 26 KB | `fe20a9f272c543d5…` |
| `assets/img/hero-p3-m-800.avif` | — | 25 KB | `9eb9aae66484100b…` |
| `assets/img/hero-p3-m-800.webp` | — | 52 KB | `d6c753a40c0accf5…` |
| `assets/img/hero-p4-1440.avif` | — | 37 KB | `c087e7f25b8470ca…` |
| `assets/img/hero-p4-1440.webp` | — | 80 KB | `06d8db818df48cbd…` |
| `assets/img/hero-p4-m-480.avif` | — | 18 KB | `7467ba31525c2e79…` |
| `assets/img/hero-p4-m-480.webp` | — | 40 KB | `d4ca0bb8320734cf…` |
| `assets/img/hero-p4-m-800.avif` | — | 40 KB | `8fc703d8a8027bac…` |
| `assets/img/hero-p4-m-800.webp` | — | 81 KB | `8c35dda647e54944…` |
| `assets/img/office-o1-1280.avif` | — | 25 KB | `718e2b0fb34c091f…` |
| `assets/img/office-o1-1280.webp` | — | 43 KB | `8ed6d79efb4208e4…` |
| `assets/img/office-o1-1920.avif` | — | 45 KB | `9e9c1aaba968a4a2…` |
| `assets/img/office-o1-1920.webp` | — | 73 KB | `484eef8d927031b6…` |
| `assets/img/office-o2-1280.avif` | — | 23 KB | `10735491916f9753…` |
| `assets/img/office-o2-1280.webp` | — | 43 KB | `0ccdb42036f2b5ab…` |
| `assets/img/office-o2-1920.avif` | — | 46 KB | `9189745b637c5abf…` |
| `assets/img/office-o2-1920.webp` | — | 77 KB | `2618927a70dc4481…` |
| `assets/img/office-o3-1280.avif` | — | 26 KB | `a5ea4b3814c465f0…` |
| `assets/img/office-o3-1280.webp` | — | 48 KB | `6f0ea1f1dcc56ca2…` |
| `assets/img/office-o3-1920.avif` | — | 48 KB | `3af3e54aa6bb9a39…` |
| `assets/img/office-o3-1920.webp` | — | 80 KB | `129c716761e279d7…` |
| `assets/fonts/inter-latin-400-normal.woff2` | — | 23 KB | `8909904ab6c872eb…` |
| `assets/fonts/inter-latin-500-normal.woff2` | — | 23 KB | `f3779f1efccc4bdc…` |
| `assets/fonts/inter-latin-600-normal.woff2` | — | 23 KB | `f9a06e79cd3a2a20…` |
| `assets/fonts/newsreader-latin-wght.woff2` | — | 56 KB | `62981321d9a3cc7a…` |
| `assets/brand/favicon.svg` | — | 0 KB | `5619eeed557ae04d…` |
| `assets/brand/nexova-symbol-marfil.svg` | — | 0 KB | `f2d5476e153dec8f…` |
| `assets/brand/nexova-symbol-tinta.svg` | — | 0 KB | `5619eeed557ae04d…` |
| `assets/favicon.svg` | — | 0 KB | `5619eeed557ae04d…` |
| `assets/seq/g1/` | 32 | 873 KB | `8503593e97abd538…` (hash de hashes) |
| `assets/seq/g2/` | 39 | 1123 KB | `32f933a3b4c68e46…` (hash de hashes) |
| `assets/seq/g3/` | 36 | 728 KB | `366c757fefecb35a…` (hash de hashes) |
| `assets/seq/g4/` | 29 | 924 KB | `0ae27be8c0d5cc0a…` (hash de hashes) |
| `assets/seq/o1/` | 24 | 729 KB | `015f22a0adc2915c…` (hash de hashes) |
| `assets/seq/o2/` | 48 | 1491 KB | `91a477e6fc270964…` (hash de hashes) |

## Presupuestos (medidos)

- Carga inicial index (Lighthouse mobile, local con gzip): 224 KiB; LCP 2.3–2.4 s; CLS 0.001; TBT 140–190 ms.
- Hero bajo demanda: secuencias g1–g4 ≈ 3.9 MB + stills P1–P4 1440 ≈ 0.26 MB (objetivo plan §24: ≤3.5 MB; desviación documentada, cada gesto ≤1.2 MB).
- Oficina bajo demanda: o1 + o2 ≈ 2.3 MB + stills ≈ 0.13 MB (objetivo ≤2 MB; desviación menor documentada).
- Ninguna secuencia se pide antes del primer scroll; con `prefers-reduced-motion` o Save-Data no se pide ninguna (verificado con Playwright).
