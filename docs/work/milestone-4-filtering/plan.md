# Milestone 4 — Filtering: Plan

Phase 2 of RPI, based on the approved `research.md`. No code changes in this phase.

## Decisions carried in from approved research

- A1: `eventOverlapsRange` + `filterEventsByRange` in `src/utils/filterEvents.ts`; `null` bound = open-ended; event span is `[year, endYear ?? year]`
- B1: while the input is invalid, show an inline error and keep showing **all** events
- C1: `Filters` component at the top of the left column, above the event panel, inside a new `sidebar` wrapper in `App` (details stay a single `aside`)
- D1: clear the selection in the change handler when the selected event is no longer visible (no `useEffect`)
- Reset, empty state and result count live in `Filters`
- Input type (open item from research): `type="text"` with `inputMode="numeric"`, parsed by our own util. This lets the user type a leading `-` for BCE years, which `type="number"` handles badly. Valid text matches `^-?\d+$` after trimming; `0` is rejected.

## ADR needed?

**None.** All within ADR-002 and `docs/business-rules.md`. `MapProps` is unchanged (ADR-005), no new dependencies, no schema change.

## Checked in this phase

`LeafletMap` renders markers with `key={marker.id}`, so removing and adding markers when the `markers` prop changes works without adapter changes.

## Files

| File | Action |
| --- | --- |
| `src/utils/filterEvents.ts` + `.test.ts` | create |
| `src/utils/parseYearRange.ts` + `.test.ts` | create |
| `src/components/Filters/Filters.tsx` + `.module.css` | create |
| `src/App.tsx` | change — range state, visible events, markers, selection clearing, sidebar wrapper |
| `src/App.module.css` | change — `.sidebar` column |
| `src/components/EventPanel/EventPanel.module.css` | change — drop fixed width/border (moved to `.sidebar`); fill remaining height |
| `TASKS.md` | change — tick items with their steps |

## Ordered steps

Each step is one commit, with its `TASKS.md` item ticked in the same commit. For every step: implement, run tests/lint/typecheck (and build where noted), run the `code-reviewer` agent on the step's diff and address its findings, then report to the user and commit only after approval (per `docs/rpi-workflow.md`, before the next step starts).

### 1. Overlap filter util [45m] → ticks "Overlap filter util with unit tests"
- `type YearRange = { start: number | null; end: number | null }` (in `src/types/` if reused by the next steps, otherwise exported from the util)
- `eventOverlapsRange(event, range)`: `eventStart = event.year`, `eventEnd = event.endYear ?? event.year`; matches when `(start === null || eventEnd >= start) && (end === null || eventStart <= end)`
- `filterEventsByRange(events, range)`
- Tests: year inside/outside; only start / only end; both `null` returns everything; month/day events match by year; span fully inside, partly overlapping, containing the range, touching the boundary year; BCE ranges; a range crossing from BCE to CE (`-1` to `1`)
- Done when: `npm test`, lint and typecheck pass

### 2. Range text parser [20m] → no tick (supports "Handle invalid/empty range input")
- `parseYearRange(startText, endText): { range: YearRange; error: string | null }`
- Empty or whitespace = `null` (open-ended, valid)
- Errors (short user-facing strings): not a whole number; year 0 not allowed; start after end
- On error, `range` is `{ start: null, end: null }` (B1: show everything)
- Tests: both empty, one empty, valid negatives, whitespace, `abc`, `1.5`, `0`, `-0`, start > end, start = end
- Done when: tests, lint and typecheck pass

### 3. Filters component with year inputs, sidebar layout [40m] → ticks "Start/end year number inputs"
- `Filters` props: `startText`, `endText`, `onChange(startText, endText)`; two labelled text inputs (`inputMode="numeric"`), no logic of its own
- `App.module.css` `.sidebar`: fixed 320px column, full height, flex column, right border. `Filters` on top, `EventPanel` below filling the rest and scrolling on its own
- `EventPanel.module.css`: remove `width`, `border-right`; set `flex: 1; min-height: 0`
- `App.tsx`: hold `startText` / `endText` state and render `Filters` (not yet used for filtering)
- Manual check: layout, panel scrolling and sticky header still work, map not distorted
- Done when: typecheck/lint/build pass and the manual check holds

### 4. Wire the filter to the markers [30m] → ticks "Wire filter to visible markers; clear selection if filtered out"
- `App.tsx`: `parseYearRange(startText, endText)` -> `visibleEvents = useMemo(() => filterEventsByRange(events, range), ...)`; `markers = visibleEvents.map(eventToMarker)` (computed from `visibleEvents`)
- Deviation (noted at implementation): `visibleEvents` and `markers` are computed on every render without `useMemo`. `parseYearRange` returns a new `range` object each render, so memoizing on it triggered the `react-hooks/exhaustive-deps` lint warning, and with at most 20 events the cost is negligible.
- Change handler: set the texts, parse the new values, and if `selectedId` is not in the new visible set call `setSelectedId(null)`
- Manual check: narrowing the range hides markers; selecting then filtering the selected event out empties the panel; widening again does not bring it back
- Done when: lint/typecheck/test/build pass

### 5. Invalid input, reset, empty state [50m] → ticks "Handle invalid/empty range input", "Reset filters control", "Empty state when no events match"
- `Filters` gets `error`, `resultCount`, `onReset`
- Inline error message (`role="alert"`) under the inputs when `error` is set; the map shows all events meanwhile
- "Showing N of M events" line; Reset button (clears both texts; disabled when both are already empty)
- Empty state "No events in this range" when the range is valid and `resultCount === 0`
- Selection is cleared on reset only if needed (same helper as step 4)
- Manual check: typing `-` / `abc` / `0` / reversed range shows the error and all markers; reset restores everything; a range with no events shows the empty state
- Done when: lint/typecheck/test/build pass

## Final checks (after step 5)
- Run `npm test`, `npm run lint`, `npm run typecheck`, `npm run build`
- Run the `code-reviewer` agent once more on the whole Milestone 4 diff (each step was already reviewed before its commit) and address findings
- Tick the Milestone 4 items in `TASKS.md` that remain

## Timebox

Steps add up to ~185 minutes against the 180 minutes budgeted in `TASKS.md` for Milestone 4 (150 for the original items plus 30 for reset and the empty state). If any step overruns by 50%, stop and reassess scope.
