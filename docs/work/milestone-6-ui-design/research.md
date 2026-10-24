# Milestone 6 — UI Design: Research

Phase 1 of RPI. Findings, constraints, options, recommendation. No code changes.

## Current state

- `App.tsx` renders a flex row: a 320px `.sidebar` (`Filters` + `EventPanel`) and `Map`. Colors, sizes and fonts are hard-coded in every CSS Module (`#ffffff`, `#dddddd`, `16px`, `0.9rem`, `#b3261e`). `src/variables.css` exists but is imported nowhere, and `index.css` only resets margins.
- `LeafletMap` renders `TileLayer` (OSM standard tiles) and one default `Marker` per event. Selected state is only a `zIndexOffset`, with no visual change.
- `EventPanel` is an always-rendered `<aside>` with an empty-state text. There is no event list; the only way to select an event is a marker click.
- The map adapter interface (`MapProps`) has `center`, `zoom`, `markers`, `selectedId`, `onMarkerClick`.
- `src/variables.css` defines spacing, two font families (`Montserrat Variable`, `IBM Plex Mono`), a fluid type scale, and six colors, with a `prefers-color-scheme: light` override. Neither font is loaded anywhere.

## Reading the inspiration (`ui-inspiration.png`)

| Element | Maps to | Decision |
| --- | --- | --- |
| Header with logo and name | Sidebar header: app name and city (from `config/city.ts`) | in |
| Scrollable list rows (avatar, name, meta) | Event list: title + formatted date | in |
| "Show me / Sort by / Filters" controls | Existing year filter (compact) | in, restyled only |
| Search box, sort, status badges, ratings | none of our data needs them | out |
| Floating card on the map (title, meta, text, button) | Event detail card | in |
| Round markers with a label | Round themed markers | in |
| Green route line | none | out |
| Dark map | Theme-matched tiles | in (see B) |

## Constraints

- No new fields, no backend, no runtime external APIs (the deployed site is static). Tiles are the one existing runtime request (OSM).
- Leaflet only inside `src/components/Map/leaflet/` (ADR-005). Markers, tile theming and resize handling must live there.
- Styling only from `variables.css` tokens; CSS Modules; no inline styles; React state only; components small and presentational.
- Not every event has `image`, `summary` or `sources`; the card must tolerate any of them missing. Showing them is Milestone 7, so the card here renders title, date and description.
- PRD §9 lists "Mobile optimization beyond basic responsiveness" as **out of scope**. The bottom drawer goes beyond that. The user decided it, so this is an override that belongs in an ADR.
- Token gaps: there is no surface/card color, no border color, and no error color. `variables.css` also spells `--highligth-*` (typo, used consistently). In dark mode `--highligth-color` and `--highligth-secondary-color` are the same value.
- CSS media queries cannot read custom properties, so the mobile breakpoint is a literal in CSS (the `--screen-size: 1200px` token is a max content width, not a breakpoint).

## Unknowns

1. How the desktop and mobile layouts share state (see C).
2. Whether the user wants a draggable drawer or tap-to-toggle (see C).
3. Which tile source gives a dark map (see B).
4. Whether the user accepts adding derived tokens to `variables.css` (see A).

## Options

### A. Tokens and theme

- **A1 (recommended)**: import `variables.css` once in `main.tsx`; add two derived tokens to it, `--surface-color` and `--border-color`, defined with `color-mix(in srgb, var(--primary-font-color) N%, var(--background-color))` so they follow both themes without a second palette. Errors use `--secondary-color` (red-orange in both themes). `variables.css` is the user's file, so this addition needs approval.
- A2: no new tokens; every component repeats the `color-mix` expression. Duplicated, harder to retune.
- A3: use `--background-color` for everything and rely only on spacing. Loses the sidebar/map/card separation in the inspiration.

### B. Fonts and map tiles

Fonts:

- **B1 (recommended)**: `@fontsource-variable/montserrat` and `@fontsource/ibm-plex-mono` from npm (self-hosted, bundled by Vite). Matches the tokens' family names, adds no runtime third-party request. Two dev-time dependencies; needs an ADR.
- B2: Google Fonts `<link>`. Zero dependencies, but a runtime request to a third party and a GDPR-flavoured privacy issue; goes against the "no external requests at runtime" constraint.

Tiles for the dark theme (OSM standard tiles have no dark variant):

- **B3 (recommended)**: keep OSM tiles and darken them with a CSS filter on the tile pane (`invert` + `hue-rotate` + lower brightness/contrast) inside a `prefers-color-scheme: dark` query. No new provider, no JS, one rule. The look is approximate, not as polished as the inspiration.
- B4: switch to a dark/light basemap provider (for example CARTO Dark Matter / Positron). Best match for the inspiration, but a new tile provider with its own usage terms and attribution; needs an ADR and a check of those terms.
- B5: keep light tiles in both themes. Zero work, but a bright map beside a dark sidebar looks wrong.

Leaflet's own controls (zoom buttons, attribution box) are light-themed by default and need restyling with the tokens in the adapter CSS under any option.

### C. Sidebar behavior: desktop collapse and mobile drawer

Layout: one `Sidebar` shell component (header, toggle, scrolling body) containing `Filters` and the event list. CSS decides presentation with a media query (about 768px):

- Desktop: left column, 320px wide; collapsing sets its width to a narrow rail (or 0) and the map fills the rest.
- Mobile: `position: fixed` at the bottom, full width, `border-radius` on top corners; collapsed shows only a handle and header (peek), expanded takes about 60% of the viewport height (`dvh`).

State:

- **C1 (recommended)**: one `useState` boolean `isOpen` in `App`, plus a small `useMediaQuery` hook (`src/hooks/`) used only for the initial value, so mobile starts collapsed (peek) and desktop starts open. The toggle is a real `<button>` with `aria-expanded` and `aria-controls`. Drawer has two states (peek/expanded), tap to toggle.
- C2: C1 plus a drag gesture on the handle (pointer events, snap between peek, half and full). Closest to a native sheet, about +45–60 min, with real edge cases (scroll vs drag, touch-action). Can be added later without rework because the state stays the same.
- C3: two independent states (`desktopCollapsed`, `mobileExpanded`) and no JS media query. More state, but no hook; it breaks when the window is resized across the breakpoint.

On mobile, selecting an event (marker or list row) expands the drawer to show the card. On desktop the card floats over the map and the sidebar stays as is.

Map resize: when the sidebar collapses the map container changes width, and Leaflet needs `invalidateSize()`. **Recommended**: the adapter observes its own container with a `ResizeObserver` and calls `invalidateSize` (via `useMap`). `MapProps` stays unchanged and nothing in the app needs to know about it. On mobile the drawer overlays the map, so no resize occurs.

### D. Event detail card

- **D1 (recommended)**: `EventPanel` becomes `EventCard`, a plain absolutely positioned element in a `mapArea` wrapper around `Map` (top-right of the map on desktop); on mobile it renders at the top of the drawer body. No Leaflet involvement. Not anchored to the marker, unlike the inspiration, but no adapter change.
- D2: a Leaflet `Popup` anchored to the marker, as in the inspiration. Requires the adapter to render React content inside a popup (new prop on `MapProps` or a render prop), conflicting with ADR-005's "no abstraction creep", and it reflows badly under the mobile drawer.

### E. Markers and selection feedback

- **E1 (recommended)**: `L.divIcon` created in the adapter: a round pin colored with `--highligth-color`, a larger ring in `--highligth-tertiary-color` when selected. Icon objects memoized per selected state. Replaces the default PNG marker, so `setupLeafletIcons.ts` and the three Leaflet image imports can go.
- E2: round marker with the event image, as in the inspiration. Images are optional, mostly not yet reviewed for display, and are Milestone 7. Revisit then.
- Optional small addition: pan the map to the selected marker when it is chosen from the list (`panTo` inside the adapter, driven by the existing `selectedId`). Without it, selecting a row may select an off-screen marker. Needs no interface change. Recommended; about 15 min.

### F. Event list

A list of `<button>` rows (title and formatted date), inside a `<ul>`, one per visible event, with `aria-pressed` on the selected row. Selecting a row calls the same `setSelectedId`. Reuses `formatEventDate`. Empty state stays in `Filters` (count line) and the list shows nothing when no events match. This also delivers the "results list" backlog item, which should be ticked.

## Recommendation

A1, B1, B3, C1, D1, E1 plus `panTo`, F. Defer C2 (drag gesture) and E2 (image markers) unless the user wants them now; both fit the current structure.

One ADR (proposed ADR-010, "UI design: theme, fonts, tiles, mobile drawer") records: self-hosted fonts via fontsource (new dependency), CSS-filter dark tiles, the bottom drawer overriding PRD §9, and the derived tokens. The user decides; the ADR is written during planning once they choose.

## Risks and timebox

- Drawer and viewport units on mobile browsers (`100vh` vs `dvh`, address bar) and the iOS safe area; needs a manual check at ~375px.
- Tile CSS filter can look washed out; fallback is B5 for dark mode, or B4 with an ADR.
- The `ResizeObserver` plus Leaflet inside `MapContainer` needs a manual check that tiles do not show gray strips after collapsing.
- Estimate stays at ~5.5h with `TASKS.md` as written. C2 would add about 1h and should come out of Backlog, not this milestone. If any task overruns by 50%, stop and reassess.
- Verification is manual (no browser test tooling is installed); pure logic is minimal, so few new unit tests are expected (at most `useMediaQuery` is not unit-tested).

## Questions for the user

1. Mobile drawer: tap-to-toggle with two heights (C1), or a draggable sheet (C2)?
2. Dark map: CSS filter on OSM (B3), or a dark/light tile provider with an ADR (B4)?
3. OK to add `--surface-color` and `--border-color` to `variables.css` (A1)?
4. OK to self-host the fonts through two fontsource npm packages (B1)?
5. Selected event card: floating in the map corner (D1) or anchored to the marker (D2)?
