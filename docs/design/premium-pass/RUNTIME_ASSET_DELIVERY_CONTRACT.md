# Runtime Asset Delivery Contract — Nexova Premium Website

**Status:** LOCKED FOR CODEX PRODUCTION  
**Scope:** A1/A2 web delivery only  
**Masters:** Never overwrite approved source masters.

## Principle

A production master and a runtime-delivery asset are different artifacts.

Masters preserve creative quality.
Runtime derivatives preserve visual intent while controlling transfer size, decoding cost and responsive waste.

## A1 — Hero

Roles:
- desktop hero LCP;
- mobile-specific hero crop.

Required runtime families:
```
a1-hero-desktop-{w}.avif
a1-hero-desktop-{w}.webp
a1-hero-mobile-{w}.avif
a1-hero-mobile-{w}.webp
```

Initial width candidates:
- desktop: 960 / 1440 / 1920 only if source quality justifies it;
- mobile: 480 / 768.

Implementation:
- semantic `picture`;
- AVIF preferred;
- WebP fallback;
- width/height or aspect-ratio reserved;
- `sizes` describes actual rendered width;
- hero may receive high fetch priority;
- no duplicate desktop + mobile download.

## A2 — Crimson fibrous material

Required runtime families:
```
a2-crimson-fibrous-{w}.avif
a2-crimson-fibrous-{w}.webp
```

Initial widths:
- 640 / 960 / 1440 only as needed by actual rendered geometry.

Implementation:
- lazy load;
- no high fetch priority;
- crop may differ between desktop/mobile through CSS/object-position or separate derivative only if required;
- do not deliver the raw heavy master by default.

## Quality rule

Choose the smallest derivative whose visual degradation is not material at its rendered size.

Do not create variants merely because a tool can.

## Evidence required

For every delivered source:
- file path;
- format;
- dimensions;
- byte size;
- consumer;
- loading strategy.

H3 fails if:
- heavy masters are the default network delivery;
- responsive markup causes duplicate downloads;
- crop materially deviates from H2;
- the LCP strategy is undocumented.
