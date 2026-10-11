# Research: Milestone 1 - Setup & Map

Scope (TASKS.md, ~2h): init Vite + React with npm, ESLint + Prettier, Leaflet + react-leaflet, map centered on Xi'an, fix default marker icon.

## Current state
- No app code yet. Repo has docs, `.claude/` commands and agent, `.gitignore` (contains only `/notes`; no `node_modules`/`dist` entries), and an ignored `notes/` dir.
- No commits yet on `main`.
- Environment: Node v22.23.3, npm 10.9.9.
- Latest versions (npm registry): react 19.3.0, vite 8.3.4, leaflet 1.9.4, react-leaflet 5.0.0 (peers: leaflet ^1.9.0, react/react-dom ^19).

## Constraints
- Stack fixed by ADR-003: React + Vite, Leaflet, CSS Modules, npm. No state library, no backend.
- Structure per `docs/code-standards.md`: `src/components/Map/` with `Map.jsx` + `Map.module.css`; small scoped components.
- City name, center and bounds must live in one config object, not hard-coded in components.
- Vite `base` for GitHub Pages is Milestone 5, not now.
- Timebox: ~2h total; marker icon fix 10m.

## Unknowns / things to verify
1. **Vite 8 scaffold output**: `npm create vite@latest` templates change between majors (e.g. whether the react template uses the Oxc/Rolldown-based plugin, and which ESLint config it ships). Verify by running it, not from memory.
2. **react-leaflet 5 + React 19**: compatible per peer deps. Note StrictMode double-mount in dev is handled by react-leaflet; verify no "Map container is already initialized" error.
3. **Leaflet default marker icon**: bundlers break the auto-detected icon paths. No markers are rendered in Milestone 1 (events arrive in Milestone 2), so the fix can be verified only with a temporary marker or deferred.
4. **Xi'an coordinates and bounds**: center ~34.34, 108.94 (from TASKS.md). The bounds for the "coordinates within city" rule are not defined anywhere yet.
5. **OSM tile usage**: the public tile server is fine for a low-traffic MVP but requires attribution and has a usage policy. Fine for this scope.

## Options

### A. Map component: react-leaflet vs raw Leaflet
- **react-leaflet (recommended)**: declarative `MapContainer`, `TileLayer`, `Marker`; fits React state for selection and filters; small. Cost: one extra dependency and its abstraction over Leaflet.
- Raw Leaflet in a `useEffect`: no extra dep, but manual lifecycle and more boilerplate for markers that change with the filter.

### B. Map height/layout
- Full-viewport map with the side panel overlaid or beside it later. Set the container to `100vh`/`100%` now, since Leaflet needs an explicit height or the map renders blank. Layout for the panel is deferred to Milestone 3.

### C. Lint/format
- Use the ESLint config the Vite template ships, add Prettier plus `eslint-config-prettier` to avoid rule conflicts. Prettier is "optional but helpful" in the TRD; it's cheap here (20m).

### D. Marker icon fix
- Import marker images from `leaflet/dist/images` and set `L.Icon.Default` options once (small `utils/leafletIcons.js`), called from `main.jsx`.
- Alternative: custom `L.icon` per marker. More repetition; the global fix is simpler.
- Verify with a temporary marker at the city center, then remove it (or leave it out and verify in Milestone 2).

### E. Config location
- `src/config/city.js` exporting `{ name, center: [lat, lng], zoom, bounds }`. Components import it. This keeps the multi-city future cheap without building any multi-city feature. The structure in `code-standards.md` doesn't list `config/`, so it needs a one-line addition to the standards.

## Recommendation
1. Scaffold with `npm create vite@latest` (React, JavaScript) into the repo root, keeping the existing docs and `.claude/`. Since the directory is not empty, check that the scaffold doesn't overwrite anything, or scaffold in a temp directory and copy files in.
2. Install `leaflet` and `react-leaflet`; import `leaflet/dist/leaflet.css`.
3. Add `src/config/city.js` (Xi'an: name, center, zoom ~12, bounds) and update the structure section of `docs/code-standards.md`.
4. Add `src/components/Map/Map.jsx` + `Map.module.css` using react-leaflet, full-height container, OSM tiles with attribution, `maxBounds` omitted for now.
5. Add the icon fix in `src/utils/leafletIcons.js`; verify with a temporary marker, then remove it.
6. Add Prettier + `eslint-config-prettier`, and scripts `lint` and `format`. Extend `.gitignore` with `node_modules` and `dist`.
7. Verify: `npm run lint`, `npm run build`, `npm run dev` and view the map (tiles load, centered on Xi'an, no console errors in StrictMode).

## Decisions needed from the user
- OK to use react-leaflet (option A) and a `src/config/city.js` file (option E, with a small standards update)?
- Xi'an bounds: OK for me to propose a rectangle around the metro area (for example the urban core plus nearby sites like the Terracotta Army in Lintong), for you to review in the plan?
- Scaffold into the repo root, merging with existing files (recommended, with a check that nothing is overwritten)?

## Update: user decisions (round 1)
- **TypeScript** instead of JavaScript (React + Vite `react-ts` template). Changes the stack in ADR-003, so it needs a new ADR; `CLAUDE.md` and `docs/code-standards.md` (`.jsx` -> `.tsx`, typed schema) get updated in the plan.
- **react-leaflet stays, but must be easy to migrate away from.** Registry check: react-leaflet's latest release is 5.0.0 (Dec 2024) with nothing since, and Leaflet itself is 1.9.4 (2023) with only a 2.0 alpha, so the concern about slow maintenance is reasonable.

### Design for migratability
- Define our own map-facing types in `src/types/` (`LatLng`, `Bounds`, `MapMarker`, plus the `HistoricalEvent` type). No Leaflet types leak outside the adapter.
- Confine all `leaflet`/`react-leaflet` imports to one folder, `src/components/Map/leaflet/` (the adapter): the tile layer, marker rendering, icon fix and CSS import.
- `Map` exposes a library-agnostic props interface: `center`, `zoom`, `bounds`, `markers`, `onMarkerClick`, `selectedId`. The rest of the app only talks to this. Replacing the library means rewriting only the adapter folder.
- City config (`src/config/city.ts`) uses our `LatLng`/`Bounds` types, not Leaflet's.
- Trade-off: this is one thin abstraction layer, which `code-standards.md` discourages before a second use. The user's migration requirement justifies it; record it as ADR-005 and keep the layer thin (no generic "map provider" plugin system).

### Candidate migration targets (for reference only)
MapLibre GL via `react-map-gl` or `@vis.gl/react-maplibre` (vector tiles, actively maintained), or Leaflet 2.x directly once stable. The adapter props above map cleanly onto either.

### New ADRs needed
- ADR-004: TypeScript.
- ADR-005: map adapter boundary to isolate Leaflet/react-leaflet.

## Still open
2. May I propose Xi'an bounds in the plan for review?
3. Scaffold into the repo root and merge with existing files, checking nothing is overwritten?
