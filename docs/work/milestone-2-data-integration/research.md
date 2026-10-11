# Research: Milestone 2 - Data Integration

Scope (TASKS.md, ~3h): finalize the event schema in `docs/code-standards.md` [20m]; draft 10-20 Xi'an events in `src/data/events.json`, user fact-checks [90m]; add a small schema validation util [30m]; load the JSON and render one marker per event [40m].

## Current state
- Milestone 1 is done and committed. `src/` has `App.tsx`, `main.tsx`, `index.css`, `components/Map/` (agnostic `Map` + `leaflet/` adapter), `config/city.ts` (Xi'an name, center, zoom 11, bounds S 34.05, W 108.60, N 34.60, E 109.45), and `types/map.ts` (`LatLng`, `Bounds`, `MapMarker`, `MapProps`).
- `Map` already accepts `markers?: MapMarker[]` (`id`, `position`, `title`), `selectedId` and `onMarkerClick`, and the marker icon fix is in place. Nothing renders markers yet.
- No `src/utils/`, `src/data/` or event type exists. No test runner is installed (Vitest is planned for Milestone 4).
- The event schema is already drafted in `docs/code-standards.md` (ADR-002): `id`, `title`, `year` (negative = BCE, no year 0), optional `month`, optional `day` (requires month), optional `endYear`, `lat`, `lng`, `description`.

## Constraints
- Static `src/data/events.json`, max 20 events, no backend or external data APIs.
- New schema fields require an ADR (code-standards, ADR-002). The schema is the contract for future AI-generated data (product vision), so keep it small.
- Coordinates must fall inside `city.bounds`.
- Leaflet imports only inside `src/components/Map/leaflet/` (ADR-005); the app converts events to our `MapMarker` type.
- TypeScript strict, no `any`, no inline styles, small scoped components, utils are pure functions with unit tests (code-standards).
- Don't over-invest in data accuracy (PRD risk); the user fact-checks the draft.
- Marker clustering is out of scope (TRD "optional later").

## Unknowns
1. **JSON typing**: the template tsconfig doesn't set `resolveJsonModule` explicitly. With `moduleResolution: bundler` it should default to on; verify when implementing. A JSON import is inferred loosely (optional fields become unions), so it must be validated and narrowed, not cast.
2. **Marker overlap**: Bell Tower and Drum Tower are ~400 m apart and the walled-city sites are close together. At zoom 11 their markers overlap. Without clustering, some markers will be hard to click. Not a blocker for M2, but it affects which events we pick.
3. **Same-place events**: two events at identical coordinates stack and one becomes unclickable. Avoid identical coordinates in the dataset.
4. **Span events and precision**: `endYear` is year-precision only. A span like "Ming city wall built 1370-1378" works; the start can carry month/day, the end cannot. Fine for the MVP.
5. **Candidate coordinates and dates are from memory**, not verified. They are drafts for you to fact-check; I'd confirm coordinates against Wikipedia/OpenStreetMap during implementation.

## Options

### A. Validation approach
- **Hand-written `parseEvents(data: unknown): HistoricalEvent[]` (recommended).** Checks required fields and types, ranges (month 1-12, day valid for the month, year != 0, `endYear >= year`, `day` requires `month`), unique kebab-case ids, `lat`/`lng` inside `city.bounds`, and max 20. Throws a descriptive error listing every problem. No new dependency; fits "simple" and the unified-schema principle.
- **Zod (or similar).** Concise and gives inferred types, but adds a runtime dependency for ~10 fields, and bounds/uniqueness/date-validity rules need custom refinements anyway.
- **Build-time script only.** Catches bad data before deploy but not at dev runtime; harder to unit test and nothing guards the app load.

### B. Where validation runs
- **At load, once (recommended):** `src/data/loadEvents.ts` (or a `useEvents` hook later) imports the JSON and runs `parseEvents`; invalid data fails loudly in dev and build. 20 events cost nothing at runtime.
- Dev-only check: skips a production guard, but production data is the same file, so little gain.

### C. Tests for the validator
- **Introduce Vitest now (recommended):** `npm install -D vitest` (v5.0.3, supports Vite 8). Code standards require unit tests for utils, and the validator is the first real logic. Cost ~20 min. This pulls the Vitest setup forward from Milestone 4, which would then just add the filter tests. Include a test that the real `events.json` passes validation.
- Defer tests to M4: breaks the standard and leaves the validator unverified.
- Manual check only: weak.

### D. Event type placement
- `src/types/event.ts` exports `HistoricalEvent`. A pure `eventToMarker(event): MapMarker` lives in `src/utils/`. App state derives markers from events; `Map` stays unaware of events.

### E. Data loading
- **Static `import events from '../data/events.json'` (recommended):** bundled, typed after validation, zero async states. Matches the TRD.
- `fetch` from `public/`: adds loading/error states for no MVP benefit.

### F. Code structure for rendering
- Keep `App.tsx` thin: `const events = loadEvents()`, `markers = events.map(eventToMarker)`, `<Map ... markers={markers} />`. `selectedId` and the click handler wait for Milestone 3.

## Candidate dataset (draft, unverified; for your review)
16 events across eras, spread over distinct locations (coordinates approximate, to be verified). Descriptions will be my own 1-3 sentence summaries.

| # | Event | Year | Approx. location |
|---|-------|------|------------------|
| 1 | Banpo Neolithic village inhabited (span) | -4500 to -3750 | Banpo Museum, 34.27, 109.06 |
| 2 | Qin moves its capital to Xianyang | -350 | Xianyang ruins, ~34.38, 108.72 |
| 3 | Qin Shi Huang's mausoleum under construction (span) | -246 to -208 | Mausoleum mound, ~34.38, 109.25 |
| 4 | Han builds Weiyang Palace at Chang'an | -200 | Weiyang Palace ruins, ~34.29, 108.87 |
| 5 | Zhang Qian departs on his Western Regions mission (start of the Silk Road) | -138 | Chang'an, Han city site, ~34.30, 108.92 |
| 6 | Tang dynasty founded, Chang'an as capital | 618 | Daming Palace area, ~34.29, 108.96 |
| 7 | Big Wild Goose Pagoda built to house Xuanzang's scriptures | 652 | 34.219, 108.964 |
| 8 | Small Wild Goose Pagoda completed | 709 | 34.240, 108.939 |
| 9 | Great Mosque of Xi'an founded | 742 | ~34.263, 108.936 |
| 10 | Nestorian Stele erected | 781 | Beilin Museum, ~34.257, 108.953 |
| 11 | Tang Chang'an dismantled; capital moved to Luoyang | 904 | Daming Palace site, near #6 (offset to avoid stacking) |
| 12 | City renamed "Xi'an" under the Ming | 1369 | Bell Tower area, ~34.258, 108.942 |
| 13 | Ming city wall built (span) | 1370 to 1378 | South Gate, ~34.256, 108.941 |
| 14 | Xi'an Incident | 1936-12-12 | Huaqing Pool, ~34.363, 109.215 |
| 15 | Terracotta Army discovered | 1974-03 | Lintong, ~34.385, 109.278 |
| 16 | Xi'an Metro opens (Line 2) | 2011-09-16 | ~34.34, 108.94 |

Gaps and risks: only one pre-Qin event; #12 and #13 are near each other (<1 km); #6 and #11 share a site. I'd offset or substitute where markers would stack. Items I'm least sure of: the Banpo span end, the Xianyang and Weiyang coordinates, and the exact dates for #5 and #11.

## Recommendation
1. **Schema**: keep the ADR-002 schema unchanged (no new fields). Finalize it in `docs/code-standards.md` by adding the validation rules above (year != 0, `endYear >= year`, date validity, `day` requires `month`, kebab-case unique ids, coordinates in `city.bounds`, max 20). Add `src/types/event.ts` with `HistoricalEvent`.
2. **Validation**: hand-written `parseEvents` in `src/utils/` (option A) run once at load (option B), with Vitest unit tests (option C), including a test that the real `events.json` is valid.
3. **Data**: draft the 16 events above (or your edited list) as `src/data/events.json`, loaded by static import (option E), with verification of coordinates before you review.
4. **Render**: `eventToMarker` util plus a thin `App.tsx` (options D, F). No selection yet.
5. Suggested commit order for the plan: types + schema doc; Vitest setup; validator with tests; dataset; marker rendering and visual check.

## Decisions needed from the user
- Introduce Vitest now (option C) instead of in Milestone 4?
- Hand-written validator instead of Zod (option A)?
- Is the candidate event list a good starting point? Tell me events to add, drop or swap, and whether you want the pre-Qin gap filled.
- Overlapping markers: accept for now and leave clustering out of the MVP, or move one event to avoid the overlap?
