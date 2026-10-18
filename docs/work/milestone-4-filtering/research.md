# Milestone 4 — Filtering: Research

Phase 1 of RPI. Findings, constraints, options, recommendation. No code changes.

## Current state

- `src/App.tsx` holds `selectedId` state and maps all `events` to `markers` once at module level. There is no filter state; the map always gets every marker.
- Layout is a flex row: `EventPanel` (an `<aside>`, always rendered, empty-state text when nothing is selected) + `Map`. A previous review fixed this to a single `aside` (`ec44405`).
- `src/components/Filters/` is reserved in `docs/code-standards.md` and `TRD.md` §3 but does not exist.
- `HistoricalEvent` dates: `year` (never 0), optional `month`/`day`, optional `endYear` (a span; cannot combine with month/day). No comparison util exists yet (ADR-002 anticipated it).
- `docs/business-rules.md` "Filtering": two year inputs (negative = BCE); an event matches when its span `[start, end]` overlaps the range; a year-only event covers the whole year; events outside the range are hidden. Also (added with ADR-007): a reset control, an empty state when nothing matches, no category filter.

## Constraints

- Pure logic in `src/utils/` with Vitest tests; components presentational; no state libraries; CSS Modules, no inline styles; no new dependencies.
- No year 0 (`-1` is directly followed by `1`), so plain integer comparison is correct for overlap; no calendar maths.
- Only one event's details at a time; the panel must not show an event whose marker is hidden.
- `npm test`, `lint`, `typecheck`, `build` must pass. Map interactions are verified by hand.

## Unknowns

1. Whether `LeafletMap` adds and removes markers correctly when the `markers` prop changes (markers should be keyed by `id`). Check in the code and by hand in the browser.
2. Where the inputs sit in the layout (options below). This is a product-visible choice.
3. What the map should show while a range is invalid (options below).

## Options

### A. Overlap util

- **A1 (recommended)**: two small pure functions in `src/utils/filterEvents.ts`:
  - `eventOverlapsRange(event, range)` where `range = { start: number | null, end: number | null }` (`null` = open-ended). The event span is `[year, endYear ?? year]`, so year-only, month and full-date events all count as their whole year. Overlap is `eventStart <= end && eventEnd >= start`, skipping a bound when it is `null`.
  - `filterEventsByRange(events, range)`.
- A2: a single function only. Slightly less code, but the per-event predicate is useful for the "clear selection" check.

Tests: year inside/outside; single-bound ranges; both bounds `null` (everything matches); span fully inside, partly overlapping, fully containing the range, touching the boundary year; BCE ranges and BCE/CE-crossing ranges (`-1` to `1`); month/day events match by year.

### B. Range input and invalid values

Inputs hold strings in state (so the user can type `-` on the way to `-221`). A pure `parseYearRange(startText, endText)` util in `src/utils/` turns them into `{ range, error }`:

- Empty field = open-ended (valid).
- Invalid: not an integer, `0`, or `start > end`.

What to do while invalid:

- **B1 (recommended)**: show an inline error message and keep showing **all** events (the range is ignored until fixed). No surprising empty map mid-typing.
- B2: keep applying the last valid range. More state, more confusing.
- B3: show no events. Looks like a bug while typing.

### C. Where the filter UI lives

- **C1 (recommended)**: a `Filters` component at the top of the left column, above the panel. This needs a small `sidebar` wrapper `div` in `App` (still a single `aside` for details). Keeps the map full-height and fits the TRD structure. It also holds the result count, the Reset button and the empty-state message.
- C2: a bar above the map. Costs map height and needs a new vertical layout.
- C3: overlay on the map. Needs positioning rules and covers markers.

### D. Clearing the selection when filtered out

- **D1 (recommended)**: derive `visibleEvents` with `useMemo`, and clear the selection explicitly: when the range changes, if the selected event is no longer in `visibleEvents`, call `setSelectedId(null)`. Done in the change handler, no `useEffect`. Matches the task wording "clear selection if filtered out".
- D2: only derive `selectedEvent` from `visibleEvents`. Simpler, but the selection silently reappears if the range is widened again.

### E. Reset and empty state

Both are in `TASKS.md` under Milestone 4. Reset clears both fields (back to all events). The empty state is a short message in `Filters` ("No events in this range") when `visibleEvents` is empty with a valid range.

## Recommendation

A1, B1, C1, D1, E as above. No ADR is needed: all of this is within ADR-002 and `business-rules.md`.

## Risks

- Layout changes (sidebar wrapper) may break the panel's sticky header or the map height. Verify manually.
- Negative-number input: `type="number"` accepts `-` and `e`, and an empty string can mean either "cleared" or "invalid text". Use `type="text"` with `inputMode="numeric"` and parse it ourselves, or use `type="number"` and rely on `valueAsNumber`. Decide in the plan.
