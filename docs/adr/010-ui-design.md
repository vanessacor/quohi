# ADR-010: UI design (theme, fonts, dark tiles, mobile drawer)

- Status: Accepted
- Date: 2026-10-24
- Amends: ADR-003 (adds two font dependencies); overrides PRD section 9 ("mobile optimization beyond basic responsiveness" is out of scope)

## Context
Milestone 6 restyles the app after `ui-inspiration.png`: a sidebar with a list beside the map, a floating detail card and round markers. The tokens already live in `src/variables.css` (spacing, fonts, colors, light/dark through `prefers-color-scheme`). Two fonts they reference are not loaded, OSM tiles have no dark variant, and the requested mobile layout (bottom drawer) goes beyond the PRD's "basic responsiveness".

## Decision
- **Tokens**: all styling uses `src/variables.css`. Two derived tokens are added, `--surface-color` and `--border-color`, computed with `color-mix` from the existing colors so both themes work without a second palette. No hard-coded colors or sizes in components
- **Fonts**: self-hosted through `@fontsource-variable/montserrat` and `@fontsource/ibm-plex-mono`, bundled by Vite. No runtime request to a font provider (the deployed site stays static)
- **Dark map**: keep the OSM tiles and darken them with a CSS filter on the tile pane under `prefers-color-scheme: dark`, inside the map adapter. A dark/light tile provider is a backlog follow-up and needs its own ADR
- **Sidebar**: collapsible on desktop. Below a 768px breakpoint it becomes a bottom drawer with a peek state and one open height, toggled by tap (no drag gesture). The map adapter resizes itself with a `ResizeObserver`, so `MapProps` does not change
- **Detail card**: floats in the map corner on desktop and is docked above the collapsed drawer on mobile; selecting an event on mobile collapses the drawer
- **Markers**: round `divIcon` markers styled with CSS, created in the adapter only (ADR-005)

## Consequences
- Two new npm dependencies (fonts), both build-time only
- The mobile drawer overrides PRD section 9; `PRD.md` is not rewritten, this ADR is the record
- Filtered dark tiles are approximate; the tile-provider follow-up replaces them if they look poor
- Removing the default Leaflet marker images simplifies `setupLeafletIcons.ts` away
- The breakpoint is a literal in CSS (media queries cannot read custom properties) and is mirrored in `src/config/layout.ts`
