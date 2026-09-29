# Visual implementation notes

The visual lock is implemented through `packages/design-system/theme.css` plus a small shared art asset set.

## Shared layer
The shared package contains only tokens/primitives that are already reused by both applications. Page-specific layouts remain inside each application.

## Art assets
Runtime artwork is implemented as lightweight SVG abstractions derived from the approved visual language (oni, peony, torii, moon and lacquer textures). The original generated boards remain design references rather than production dependencies.

## Accessibility contract
- target WCAG 2.2 AA;
- visible focus states;
- reduced-motion support;
- 44px-class primary interaction targets;
- semantic sections/tables/navigation;
- decorative imagery kept out of the accessibility tree where appropriate.
