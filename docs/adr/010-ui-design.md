# ADR-010: UI design (theme, fonts, dark tiles, mobile drawer)

- Status: Accepted
- Date: 2026-10-24
- Amends: ADR-003 (adds two font dependencies); overrides PRD section 9 ("mobile optimization beyond basic responsiveness" is out of scope)

## Context
Milestone 6 restyles the app after `ui-inspiration.png`: a sidebar with a list beside the map, a floating detail card and round markers. The tokens already live in `src/variables.css` (spacing, fonts, colors, light/dark through `prefers-color-scheme`). Two fonts they reference are not loaded, OSM tiles have no dark variant, and the requested mobile layout (bottom drawer) goes beyond the PRD's "basic responsiveness".

## Decision
- **Tokens**: all styling uses `src/variables.css`. Two derived tokens are added, `--surface-color` and `--border-color`, computed with `color-mix` from the existing colors so both themes work without a second palette. No hard-coded colors or sizes in components
- **Palette (amended 2026-10-25)**: the dark and light palettes come from `dark-mode-pallete.png` and `light-mode-palette.png` (Happy Hues). `variables.css` holds the values: dark background `#004643`, headline `#fffffe`, paragraph `#abd1c6`, highlight `#f9bc60`; light background `#f8f5f2`, headline `#232323`, paragraph `#222525`, highlight `#078080`. Three tokens are added: `--button-text-color`, `--stroke-color` (borders of markers) and `--error-color` (the palettes' secondary color is not an error color in the dark theme). The error color is too dim for text on the surface (about 2.6:1), so `--error-text-color` mixes it 50/50 with the headline color (about 5:1) for error messages and the invalid-input border. The text on the selected-details background uses the headline color for contrast. Small button text in the light theme (`#232323` on `#078080`, about 3.3:1) is limited to large or bold text, with `#fffffe` as the fallback
- **Fonts**: self-hosted through `@fontsource-variable/montserrat` and `@fontsource/ibm-plex-mono`, bundled by Vite. No runtime request to a font provider (the deployed site stays static)
- **Dark map**: keep the OSM tiles and darken them with a CSS filter on the tile pane under `prefers-color-scheme: dark`, inside the map adapter. A dark/light tile provider is a backlog follow-up and needs its own ADR
- **Sidebar**: collapsible on desktop. Below a 768px breakpoint it becomes a bottom drawer with a peek state and one open height, toggled by tap (no drag gesture). The map adapter resizes itself with a `ResizeObserver`, so `MapProps` does not change
- **Event details**: no event list and no floating card. Selecting a marker shows the event's details (title, date, description) in a section of the sidebar under the filters, on a highlight background (`--selected-color`), so the sidebar has a single scroll area. On mobile the drawer stays open on selection so the details are visible
- **Selection feedback**: the details section and the selected marker share the highlight color
- **Markers**: round `divIcon` markers styled with CSS, created in the adapter only (ADR-005)

## Consequences
- Two new npm dependencies (fonts), bundled into the build as static assets
- The mobile drawer overrides PRD section 9; `PRD.md` is not rewritten, this ADR is the record
- Filtered dark tiles are approximate; the tile-provider follow-up replaces them if they look poor
- `setupLeafletIcons.ts` and the default Leaflet marker images are removed
- The breakpoint is a literal in CSS (media queries cannot read custom properties) and is mirrored in `src/config/layout.ts`
