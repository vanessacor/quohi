# Plan: Milestone 2 - Data Integration

Based on `research.md` and the user's decisions: Vitest now; hand-written validator (Zod deferred, documented in the `TASKS.md` backlog); the 16-event list; marker overlap accepted for now (clustering deferred, documented in the backlog). Timebox: ~3h, not counting approval pauses.

## Step approval and commits
Same rules as Milestone 1, for every step: do the step, report what changed and how it was verified, **stop for the user's explicit approval**, then commit that step only (specific files, imperative message, attribution line) with the matching `TASKS.md` items ticked in the same commit.

## Decisions needing an ADR
- **ADR-006: Vitest for unit tests** (new dev dependency and test runner, written in step 3). Everything else follows ADR-002 (schema), ADR-004 (TypeScript) and ADR-005 (adapter boundary); no schema fields are added.

## Design

### Types (`src/types/event.ts`)
```ts
export interface HistoricalEvent {
  id: string
  title: string
  year: number
  month?: number
  day?: number
  endYear?: number
  lat: number
  lng: number
  description: string
}
```

### Validation rules for `parseEvents(data: unknown, bounds: Bounds): HistoricalEvent[]`
- `data` is an array with 1 to `MAX_EVENTS` (20) items; each item is an object
- `id`: non-empty kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`) and unique
- `title`, `description`: non-empty strings
- `year`: integer, not 0; `endYear` (optional): integer, not 0, `>= year`
- `month` (optional): integer 1-12; `day` (optional): integer, requires `month`, and `1..daysInMonth` (February allows 29; no leap-year logic, since the calendar for ancient dates is not Gregorian anyway)
- `lat`/`lng`: finite numbers inside `bounds`
- Unknown extra fields are rejected (new fields need an ADR)
- It collects all problems and throws one `Error` whose message lists them, each prefixed with the event index/id

### Other utils
- `eventToMarker(event: HistoricalEvent): MapMarker` in `src/utils/eventToMarker.ts`
- `src/data/events.ts` exports `events = parseEvents(rawJson, city.bounds)`, so invalid data fails loudly at app load and in tests

## Files
Created: `docs/adr/006-vitest.md`, `src/types/event.ts`, `src/utils/parseEvents.ts` + `.test.ts`, `src/utils/eventToMarker.ts` + `.test.ts`, `src/data/events.json`, `src/data/events.ts` + `.test.ts`
Changed: `package.json`/`package-lock.json` (vitest, `test` script), `vite.config.ts` (test config, `vitest/config` import), `docs/code-standards.md` (schema rules, testing), `CLAUDE.md` (commands, ADR list), `TASKS.md` (ticks), `src/App.tsx` (render markers)

## Steps

1. **Document deferred items (5m).** Commit the `TASKS.md` backlog already written (Zod migration, clustering, Milestone 1 nits) and the two new Milestone 2 items ("add `HistoricalEvent` type" folded into the schema item, "Set up Vitest"). Verify: `TASKS.md` renders sensibly. No ticks.

2. **Finalize schema (20m).** Add `src/types/event.ts`. Update `docs/code-standards.md`: validation rules (above), the `HistoricalEvent` type, "Dates before 1582 are recorded as given in the source; no calendar conversion", and a pointer to `parseEvents`. Verify: lint, typecheck, build. Tick: "Finalize event schema ... and add `HistoricalEvent` type".

3. **Set up Vitest (20m).** Install `vitest` pinned (npm, `save-exact`); import `defineConfig` from `vitest/config` and set `test.environment: 'node'`; add `"test": "vitest run"`; write ADR-006; update `CLAUDE.md` (commands, ADR list) and the Testing section of the standards. No real tests yet, so verify with `npx vitest run --passWithNoTests`, plus lint, typecheck, build. Tick: "Set up Vitest".

4. **Validator, test first (40m).** Write `parseEvents.test.ts` covering: a valid event with only `year`; with month; with full date; with `endYear`; BCE year; year 0 rejected; `endYear < year`; `day` without `month`; Feb 30 rejected, Feb 29 accepted; month 13; non-integer year; duplicate ids; non-kebab id; empty title; out-of-bounds coordinates; unknown field; non-array input; empty array; 21 events; multiple errors reported together. Then implement `parseEvents.ts`. Verify: `npm test`, lint, typecheck, build. Tick: "Add a small schema validation script/util".

5. **Dataset (90m).**
   - I verify coordinates and dates for the 16 candidates against Wikipedia/OpenStreetMap (web search), draft `src/data/events.json` with my own short descriptions (no copied text), offsetting same-site markers slightly where needed, and note anything uncertain.
   - Write `events.ts` and `events.test.ts` (loads without throwing; between 10 and 20 events; all ids unique).
   - **Review gate:** present the full dataset as a table (title, date, coordinates, source, confidence) for the user to fact-check before the commit. Changes requested by the user are applied before committing.
   - Verify: `npm test`, lint, typecheck, build. Tick: "Draft 10-20 events ...".

6. **Marker conversion (15m).** `eventToMarker.test.ts` first (position, id, title mapping), then `eventToMarker.ts`. Verify: `npm test`, lint, typecheck, build. No tick yet.

7. **Render markers (25m).** `App.tsx` maps `events` to markers via `eventToMarker` and passes them to `Map`. Verify: lint, typecheck, build, tests, then the user checks the dev server: 16 markers visible at the right places on the map, hovering shows titles, no console errors, nothing happens on click (Milestone 3). Tick: "Load JSON and render one marker per event".

8. **Review (15m).** Run the `code-reviewer` agent on the Milestone 2 diff, fix findings the user selects, tick nothing new, commit separately with approval.

## Tests
`parseEvents` (the rules above), `eventToMarker` (mapping), `events.ts` (real dataset is valid, 10-20 events). Manual: marker positions and hover titles on the dev server.

## Out of scope
Selection and side panel (Milestone 3), date formatting, filtering (Milestone 4), clustering, Zod, any new schema field, `maxBounds` on the map.

## Risks
- Dataset accuracy: mitigated by verification against sources and the review gate; keep to the timebox, don't chase precision on uncertain items (flag them instead).
- Same-site markers stacking: offset coordinates slightly and note it; overlap otherwise accepted for the MVP.
- Vitest 5 and Vite 8 compatibility: peer range includes Vite 8; confirmed by running tests in step 3/4.
