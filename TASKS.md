# Tasks

Timebox in brackets; total budget ~12h. If a task overruns by 50%, stop and reassess scope.

## Milestone 1: Setup & Map (~2h)
- [x] Init Vite + React project with npm [30m]
- [x] Add oxlint (template default) and Prettier [20m]
- [x] Install Leaflet + react-leaflet [10m]
- [x] Import Leaflet CSS (inside the map adapter) [10m]
- [x] Render map centered on the MVP city, Xi'an, China (~34.34, 108.94); keep city name, center and bounds in one config object, not hard-coded in components [40m]
- [x] Fix default marker icon issue with Vite bundling [10m]

## Milestone 2: Data Integration (~3h)
- [x] Finalize event schema in `docs/business-rules.md` and add `HistoricalEvent` type [20m]
- [x] Set up Vitest (`npm test`) [20m]
- [x] Draft 10-20 events for the MVP city with coordinates in `src/data/events.json` (user fact-checks) [90m]
- [x] Add a small schema validation script/util [30m]
- [ ] Load JSON and render one marker per event [40m]

## Milestone 3: Interaction (~2h)
- [ ] Marker click sets selected event in App state [30m]
- [ ] Side panel with title, formatted date, description [45m]
- [ ] Only one event shown at a time; close/deselect behavior [20m]
- [ ] Date formatting util (BCE, year-only, full date) [25m]

## Milestone 4: Filtering (~2.5h)
- [ ] Overlap filter util with unit tests (year-only counts as whole year) [45m]
- [ ] Start/end year number inputs [40m]
- [ ] Wire filter to visible markers; clear selection if filtered out [30m]
- [ ] Handle invalid/empty range input [25m]

## Milestone 5: Finalization (~2.5h)
- [ ] Basic UI cleanup and basic responsiveness [60m]
- [ ] GitHub Pages config (`base` in Vite config) + Actions deploy workflow [45m]
- [ ] Deploy and verify live URL [20m]
- [ ] Check success criteria in PRD section 10 [15m]

## Backlog (deferred, not scheduled)
- [ ] Migrate the hand-written `parseEvents` validator to Zod (decided in Milestone 2 to start hand-written; revisit when the schema grows or AI-generated data arrives, Phase 2 of the vision)
- [ ] Marker clustering or overlap handling (overlapping markers accepted for the MVP; TRD lists clustering as optional later)
- [ ] Milestone 1 review nits:
  - [ ] `main.tsx` imports `./App.tsx` with the extension while other imports omit it
  - [ ] Set `"strict": true` explicitly in `tsconfig.app.json` (ADR-004 relies on the TS 6 default)
  - [ ] Replace the Vite template favicon
  - [ ] Add a `format:check` script (CI can't verify formatting without writing files)
  - [ ] Add more oxlint rules (e.g. `react/exhaustive-deps`)
  - [ ] Map height is fixed at `100vh`; revisit when the side panel and filter land (Milestone 3)
  - [ ] `TRD.md` references "step 2 of milestone-1 plan"; link the plan file or drop the reference
  - [ ] Decide whether to rename the `Map` component (shadows the global `Map`)
