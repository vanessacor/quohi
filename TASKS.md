# Tasks

Timebox in brackets; total budget ~12h. If a task overruns by 50%, stop and reassess scope.

## Milestone 1: Setup & Map (~2h)
- [x] Init Vite + React project with npm [30m]
- [x] Add oxlint (template default) and Prettier [20m]
- [x] Install Leaflet + react-leaflet [10m]
- [ ] Import Leaflet CSS (inside the map adapter) [10m]
- [ ] Render map centered on the MVP city, Xi'an, China (~34.34, 108.94); keep city name, center and bounds in one config object, not hard-coded in components [40m]
- [ ] Fix default marker icon issue with Vite bundling [10m]

## Milestone 2: Data Integration (~3h)
- [ ] Finalize event schema in `docs/code-standards.md` [20m]
- [ ] Draft 10-20 events for the MVP city with coordinates in `src/data/events.json` (user fact-checks) [90m]
- [ ] Add a small schema validation script/util [30m]
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
