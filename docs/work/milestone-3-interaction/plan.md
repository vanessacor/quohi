# Milestone 3 — Interaction: Plan

Phase 2 of RPI, based on the approved `research.md`. No code changes in this phase.

## Decisions carried in from approved research

- Selection state: `useState<string | null>` in `App.tsx`; derived event via `events.find()` (research A1/E)
- Layout: fixed side column, always present with empty state; map container becomes `height: 100%` flex child, closing the `100vh` backlog item (B1)
- Date format: bare CE years, `BCE` suffix (`350 BCE` / `1949`), month names as words (C1)
- Deselect: close button only, no Escape, no map-click deselect (D1)

## ADR needed?

**None.** `MapProps` is unchanged (ADR-005 untouched), no new dependencies, no schema change (ADR-002 already anticipates the formatting util), plain React state (ADR-003).

## Files

| File | Action |
| --- | --- |
| `src/utils/formatEventDate.ts` | create — pure date formatter |
| `src/utils/formatEventDate.test.ts` | create — Vitest unit tests |
| `src/App.tsx` | change — selection state, layout wrapper, props to `Map` and `EventPanel` |
| `src/App.module.css` | create — flex row layout |
| `src/components/EventPanel/EventPanel.tsx` | create — panel component |
| `src/components/EventPanel/EventPanel.module.css` | create — panel styles |
| `src/components/Map/Map.module.css` | change — `height: 100vh` → `height: 100%` |
| `TASKS.md` | change — tick items with their steps |

## Ordered steps

Each step is one commit, approved by the user before the next starts (per `docs/rpi-workflow.md`), with its `TASKS.md` item ticked in the same commit.

### 1. Date formatting util [25m] → ticks "Date formatting util (BCE, year-only, full date)"
- `formatEventDate(event: Pick<HistoricalEvent, 'year' | 'month' | 'day' | 'endYear'>): string` in `src/utils/formatEventDate.ts`
- Fixed month-name array + `Math.abs()`; never the `Date` object (no calendar conversion, no timezones)
- Formatting rules:
  - year only: `1949` (CE bare) / `350 BCE`
  - year + month: `June 221 BCE`
  - full date: `18 June 221 BCE`
  - span: endpoints formatted independently, joined with ` – `: `4700 – 3600 BCE`, era-crossing `10 BCE – 5 CE`
- Tests (`formatEventDate.test.ts`): year-only CE, year-only BCE, month-only, full date BCE, span both-BCE, era-crossing span, no year 0 in output, one real event from `events.json`
- Done when: `npm test` passes

### 2. Marker click sets selection in App [30m] → ticks "Marker click sets selected event in App state"
- `App.tsx`: `const [selectedId, setSelectedId] = useState<string | null>(null)`
- Derive `const selectedEvent = events.find(e => e.id === selectedId) ?? null`
- Pass `selectedId={selectedId}` and `onMarkerClick={setSelectedId}` to `<Map>` (types already match; selected marker already gets the `zIndexOffset` bump in the adapter)
- Keep `markers` computation as-is (no re-render cost worth memoizing at 20 events)
- Done when: typecheck/lint pass; selection visible only via marker zIndex for now (panel lands in step 3)

### 3. Side panel with details [45m] → ticks "Side panel with title, formatted date, description"
- `EventPanel.tsx`: props `{ event: HistoricalEvent | null; onClose: () => void }`
  - Empty state text when `event` is null (e.g. "Select an event marker to see details")
  - Otherwise title (`<h2>`), `formatEventDate(event)`, description — no Leaflet or map imports (panel is app-level, consumes `HistoricalEvent`)
  - Close button markup with `aria-label="Close"`, handler wired to `onClose` (behavior confirmed fully in step 4)
- `App.module.css`: `.app { display: flex; height: 100% }`; `Map.module.css`: `height: 100vh` → `height: 100%` (plus `flex: 1; min-width: 0` so the map shrinks correctly)
- Panel: fixed width ~320px, `overflow-y: auto` for long descriptions, CSS Modules only (no inline styles)
- Done when: clicking a marker shows title/date/description; empty state otherwise; `npm run lint` + `typecheck` pass; manual check that the map still sizes correctly (verify Leaflet's ResizeObserver handles the layout; map width is constant so it should)

### 4. Close / only-one-at-a-time behavior [20m] → ticks "Only one event shown at a time; close/deselect behavior"
- Close button: `onClose={() => setSelectedId(null)}` → panel returns to empty state
- Confirm clicking a different marker replaces the current panel content (single `selectedId` makes double-open impossible by construction)
- Manual verification: select → switch → close → reselect
- Done when: `npm test`, `npm run lint`, `npm run typecheck`, `npm run build` all pass

### 5. Review [15m, outside the 2h task budget]
- Run the `code-reviewer` agent on the full Milestone 3 diff; address findings with user approval; commit separately, tick nothing new

## Tests

- **Unit**: `formatEventDate.test.ts` (step 1) — the only new `utils/` function this milestone
- **Manual**: marker click → panel content, marker switching, close button, map sizing at window resize, panel scrolling
- Regression: `npm test`, `npm run lint`, `npm run typecheck`, `npm run build` after every step

## Timebox

| Step | Time |
| --- | --- |
| 1. Date formatting util | 25m |
| 2. Selection state | 30m |
| 3. Side panel + layout | 45m |
| 4. Close/deselect | 20m |
| **Tasks total** | **120m (~2h, matches TASKS.md)** |
| 5. Review | +15m |

If a step overruns by 50%, stop and reassess scope (TASKS.md rule).

## Approval

Approve this plan to start implementation, or request changes first.
