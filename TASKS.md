# Tasks

Timebox in brackets. The original MVP budget was ~12h; Milestones 5-7 (data pipeline, UI design, summaries and images, ADR-007/008/009) are timeboxed separately on top of it. If a task overruns by 50%, stop and reassess scope.

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
- [x] Load JSON and render one marker per event [40m]

## Milestone 3: Interaction (~2h)
- [x] Marker click sets selected event in App state [30m]
- [x] Side panel with title, formatted date, description [45m]
- [x] Only one event shown at a time; close/deselect behavior [20m]
- [x] Date formatting util (BCE, year-only, full date) [25m]

## Milestone 4: Filtering (~2.5h)
- [x] Overlap filter util with unit tests (year-only counts as whole year) [45m]
- [x] Start/end year number inputs [40m]
- [x] Wire filter to visible markers; clear selection if filtered out [30m]
- [x] Handle invalid/empty range input [25m]
- [x] Reset filters control [15m]
- [x] Empty state when no events match [15m]

## Milestone 5: Data Pipeline (~4.7h, extra budget, ADR-007/009)
- [x] Update `HistoricalEvent`, `parseEvents` and tests for the optional fields [45m]
- [x] Define "historical event" scope for Xi'an and confirm the bounding box in `src/config/city.ts` [20m]
- [x] `scripts/fetch_events.py`: Wikidata SPARQL with local caching; set up `requirements.txt` [75m]
- [x] User curates the QID list [20m]
- [x] `scripts/enrich_events.py`: Wikipedia extracts, links and images [50m]
- [x] Normalize to the schema, dedupe by QID, validate, export `src/data/events.json` capped at 20 [40m]
- [x] User reviews and fact-checks the output [30m]

## Milestone 6: UI Design (~7h, extra budget)
Visual direction: `ui-inspiration.png` (dark left sidebar with a list, map on the right, floating detail card, round pin markers). Layout requirements: on desktop the sidebar is collapsible; on mobile it becomes a bottom drawer (like a native sheet) instead of a left column. Styling uses only the tokens in `src/variables.css` (spacing, fonts, colors, dark/light via `prefers-color-scheme`); no hard-coded colors or sizes in components.
- [x] Research: analyse `ui-inspiration.png`, map its elements to the existing components (sidebar, list, filters, detail card, markers) and decide what is out of scope (search, sort, route line, ratings) [30m]
- [x] Write ADR-010 (UI design: theme tokens, self-hosted fonts, CSS-filter dark tiles, mobile drawer overriding PRD section 9) [15m]
- [ ] Wire `src/variables.css` into the app (import once in `main.tsx`), add derived `--surface-color` and `--border-color`, set base styles in `index.css` (background, text color, `--text-font`/`--title-font`) [25m]
- [ ] Load the fonts the tokens reference (Montserrat Variable, IBM Plex Mono); self-hosted via `@fontsource-variable/montserrat` and `@fontsource/ibm-plex-mono` (decided, ADR-010) [15m]
- [ ] App layout: fixed-width sidebar (filters + event list) beside a full-height map, using `--screen-size` and spacing tokens [40m]
- [ ] Collapsible desktop sidebar: toggle button, collapsed state leaves the map full width, the adapter observes its own container with a `ResizeObserver` and calls `invalidateSize` (ADR-005, `MapProps` unchanged); React state only [30m]
- [ ] Mobile bottom drawer (below a breakpoint): collapsed handle with peek height, expands to one open height, tap on the handle toggles it (drag gesture deferred to backlog); the map stays visible and usable above it; keyboard accessible (button with `aria-expanded`) [60m]
- [ ] Mobile detail card: docked above the collapsed drawer; selecting an event on mobile collapses the drawer so the map and card stay visible [20m]
- [ ] Filters restyled as a compact sidebar section (year inputs, reset button) [30m]
- [ ] Event list in the sidebar: one row per visible event with title and formatted date; selecting a row selects the marker (this promotes the "results list" backlog item) [45m]
- [ ] Event detail as a floating card in the map corner, replacing the full side panel: title, date, description, close button (summary, image and source links come in Milestone 7) [45m]
- [ ] Custom map markers (round `divIcon` pins with the selected state highlighted, drop the default PNG icon setup) and pan to the selected marker, via the Leaflet adapter only (ADR-005) [45m]
- [ ] Dark map via a CSS filter on the OSM tile pane; restyle Leaflet zoom and attribution controls with the tokens; check that attribution stays visible [20m]
- [ ] Visual check in dark and light mode, keyboard focus styles, text contrast; check desktop collapsed/expanded and the mobile drawer states at ~375px width [30m]

## Milestone 7: Summaries & Images (~2.5h, extra budget, ADR-008/009)
- [ ] Check hardware requirements; install Ollama + Qwen3 4B [20m]
- [ ] `scripts/generate_summaries.py`: constrained prompt, output validation, cache [75m]
- [ ] Side panel: summary, image with fallback and attribution, source links [45m]
- [ ] Verify missing optional fields do not break the UI [15m]

## Milestone 8: Finalization (~2.5h)
- [ ] Final mobile check on a real device or emulator (responsive layout and the drawer are built in Milestone 6) [15m]
- [ ] GitHub Pages config (`base` in Vite config) + Actions deploy workflow [45m]
- [ ] Deploy and verify live URL [20m]
- [ ] Check success criteria in PRD section 10, including a mobile check [15m]

## Backlog (deferred, not scheduled)
- [ ] Dark/light tile provider (e.g. CARTO Dark Matter / Positron) to replace the CSS-filter dark map: check usage terms and attribution, record in an ADR (follow-up of Milestone 6)
- [ ] Draggable mobile drawer with snap heights (Milestone 6 ships tap-to-toggle only) [~1h]
- [ ] Image markers on the map, as in `ui-inspiration.png` (after Milestone 7 images)
- [ ] Filter: when the "from" year is valid and the "to" year is invalid (or the reverse), treat the invalid one as open-ended (null) and still apply the valid bound, instead of ignoring the whole range (currently any error shows all events, Milestone 4 decision B1)
- [x] Results list as an accessible alternative to the map markers (delivered by the Milestone 6 event list)
- [ ] Fix the Daming Palace date in `events.json`: the pipeline used the heritage park's 2010 opening (P571); the palace dates from 634. Add a `manual_dates` entry in `scripts/config/curated.json`, and check the Jianguomen (1939) and Guangren Temple (1705) dates the same way
- [ ] Remove the vague `# not ideal: births are out of scope` comment in `infer_date_property` (`scripts/enrich_events.py`); births of historical figures are kept (`docs/business-rules.md`), so state that decision in the code through naming instead
- [ ] Migrate the hand-written `parseEvents` validator to Zod (decided in Milestone 2 to start hand-written; revisit when the schema grows or AI-generated data arrives, Phase 2 of the vision; ADR-009 grows the validator, which strengthens the case)
- [ ] Marker clustering or overlap handling (overlapping markers accepted for the MVP; TRD lists clustering as optional later)
- [ ] Milestone 1 review nits:
  - [ ] `main.tsx` imports `./App.tsx` with the extension while other imports omit it
  - [ ] Set `"strict": true` explicitly in `tsconfig.app.json` (ADR-004 relies on the TS 6 default)
  - [ ] Replace the Vite template favicon
  - [ ] Add a `format:check` script (CI can't verify formatting without writing files)
  - [ ] Add more oxlint rules (e.g. `react/exhaustive-deps`)
  - [x] Map height is fixed at `100vh`; revisit when the side panel and filter land (Milestone 3)
  - [ ] `TRD.md` references "step 2 of milestone-1 plan"; link the plan file or drop the reference
  - [ ] Decide whether to rename the `Map` component (shadows the global `Map`)
