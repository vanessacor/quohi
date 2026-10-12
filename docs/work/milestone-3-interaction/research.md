# Milestone 3 — Interaction: Research

Phase 1 of RPI. Findings, constraints, options, recommendation. No code changes.

## Current state

- `src/App.tsx` is thin: maps `events` → markers at module level and renders `<Map markers={…} />`. **No selection state yet.**
- The map adapter is already prepared for this milestone: `MapProps` (`src/types/map.ts`) has `selectedId?: string | null` and `onMarkerClick?: (id) => void`; `LeafletMap.tsx` already fires `onMarkerClick?.(id)` on marker click and raises `zIndexOffset` for the selected marker (ADR-005 anticipated this).
- **No panel exists.** `src/components/EventPanel/` is reserved in the structure by `docs/code-standards.md` and `TRD.md` §3 but not created.
- **No date formatting util exists.** ADR-002 explicitly says the schema "needs custom date formatting and comparison utils (unit tested)" — formatting lands here (Milestone 4 needs comparison).
- Layout: `Map.module.css .container { height: 100vh }` — the backlog item says revisit when the side panel lands (now).
- The data exercises every date shape: BCE years (`-4700`), a span (`endYear`), and 4 events with `month` + `day`. No event currently uses `month` alone, but the schema allows it.

## Constraints

- **Business rules**: only one event's details shown at a time; precision implied by present fields (year / year+month / full); no calendar conversion (pre-1582 dates as given); no year 0.
- **Code standards**: panel lives in `src/components/EventPanel/` (`Name.tsx` + `Name.module.css`, no inline styles); date formatting is a pure function in `src/utils/` with Vitest tests; plain React state only, no state libraries; `Map` stays Leaflet-free (panel consumes `HistoricalEvent`, never map types).
- **MVP**: no new dependencies; simplicity over completeness; no architecture decisions without an ADR.
- `npm test`, `npm run lint`, `npm run typecheck`, `npm run build` must pass.

## Unknowns

1. **Container resize vs Leaflet sizing.** If the panel appears/disappears and changes the map's width, Leaflet may leave grey bands until `invalidateSize()`. Leaflet 1.9.4 (installed) has ResizeObserver-based detection that should handle this automatically — verify by hand in the browser; if it misbehaves, fall back to a layout where the map size never changes.
2. **Date format wording** (CE style, month names, span rendering) is a product-visible choice — decided below, confirmable in plan approval.
3. Deselect triggers beyond a close button (map background click, Escape) — scope question, see options.

## Options

### A. Where selection state lives

- **A1 — `App.tsx` with `useState<string | null>` (recommended).** Map and panel are siblings; both get props (`selectedId`, `onMarkerClick` / `event`). Matches "App stays thin" and plain-React-state standard. Not an architecture decision → no ADR.
- A2 — a `useSelectedEvent` hook in `src/hooks/`. Directory is reserved but unused; extraction on second use only — premature now.

### B. Panel layout (resolves the `100vh` backlog item)

- **B1 — Fixed side column (recommended).** App root becomes a flex row: panel column (fixed ~300–320px) + map filling the rest; map container switches from `100vh` to `height: 100%` inside the flex parent (`html/body/#root` are already `height: 100%`). The column **always exists**: empty state text ("Select an event") when nothing is selected. Map width never changes → no `invalidateSize` concern at all. Simplest, most robust.
- B2 — Panel only rendered when an event is selected, pushing the map. Prettier empty map, but the map resizes at runtime (unknown #1) and the layout jumps.
- B3 — Panel overlaid on the map (absolute). Keeps full map width but covers markers and needs positioning rules; "side panel" in the PRD reads as beside, not on top.

### C. Date formatting util (`formatEventDate(event: HistoricalEvent): string`)

Rendering per precision, using a fixed month-name array and `Math.abs()` (never the `Date` object — avoids timezone/calendar conversion):

- Year only: `350 BCE` / `1949`
- Year + month: `June 221 BCE` (month name, no day)
- Full date: `18 June 221 BCE` (day + month name + year)
- Span: `<start> – <end>`, each endpoint formatted independently → `4700 – 3600 BCE`, and a hypothetical era-crossing span renders `10 BCE – 5 CE`

Open sub-choices for your approval:

- **C1 (recommended)**: BCE gets a `BCE` suffix; CE years render bare (`1949`) — the common editorial convention, less noise for a minimal UI.
- C2: explicit `CE` suffix on all positive years (`1949 CE`) — symmetric but busier.
- Month names as words (recommended, per examples above) vs numeric (`18/6/221`, ambiguous across locales).

### D. Deselect / close behavior

- **D1 (recommended)**: close button (×) in the panel header → `setSelectedId(null)`. Clicking another marker replaces the current event (satisfies "only one at a time").
- D2 — add Escape-to-close (small, keyboard-friendly; optional).
- D3 — click empty map to deselect: requires a new adapter surface (`onMapClick` in `MapProps` — an ADR-005 interface change) for little gain. Skip for MVP.

### E. Selected event lookup

Keep `selectedId: string | null` in state and derive `selectedEvent = events.find(e => e.id === selectedId) ?? null` in `App`. Id-based matches the existing `MapProps`; a stale/unknown id simply renders the empty state. Derived, not stored — no duplication.

## Recommendation

1. State in `App.tsx` (A1): `const [selectedId, setSelectedId] = useState<string | null>(null)`; pass `selectedId` + `onMarkerClick={setSelectedId}` to `Map`, and the derived event to `EventPanel`.
2. Layout B1: flex row, always-present `EventPanel` column (~320px, empty state when null), map container `height: 100%` — closes the `100vh` backlog item without runtime resizing.
3. `src/utils/formatEventDate.ts` + `formatEventDate.test.ts` covering: year-only CE/BCE, month-only, full date, span, era-crossing span, and a real event from `events.json` (format C1/C2 + month-name choice pending your call).
4. Close button only (D1), Escape (D2) optional; no map-click deselect (D3).
5. New files: `src/components/EventPanel/EventPanel.tsx`, `EventPanel.module.css`, `src/utils/formatEventDate.ts`, `formatEventDate.test.ts`. Modified: `App.tsx`, `src/components/Map/Map.module.css` (and possibly `index.css`). No new dependencies, no ADR required — `MapProps` is unchanged, so ADR-005 is untouched.

## Approval

Approve this research (including choices **C1 vs C2** and **D1/D2**) to proceed to the plan phase, or tell me what to change.
