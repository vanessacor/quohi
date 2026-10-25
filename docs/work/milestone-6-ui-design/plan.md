# Milestone 6 — UI Design: Plan

Phase 2 of RPI, based on the approved research. No code changes yet.

## Decisions (from the user)

- Mobile drawer: tap-to-toggle, one open height (drag gesture goes to the backlog)
- Dark map: CSS filter on the OSM tiles now; a tile provider is a backlog follow-up (ADR needed then)
- `--surface-color` and `--border-color` added to `src/variables.css` as `color-mix` derived tokens
- Fonts self-hosted via `@fontsource-variable/montserrat` and `@fontsource/ibm-plex-mono`
- Detail card floats in the map corner (not anchored to the marker)
- Plan-level choices, for the user to confirm or change:
  - On mobile the card is docked above the collapsed drawer, and selecting an event collapses the drawer (map and card stay visible), instead of rendering the card inside the drawer. One render location, no duplicated card
  - Errors use `--secondary-color`; the selected marker ring uses `--highligth-tertiary-color`

## ADR needed

**ADR-010 (UI design)**: self-hosted fonts (two new npm dependencies, amends ADR-003), derived tokens, CSS-filter dark tiles, the mobile bottom drawer overriding PRD section 9 ("mobile optimization beyond basic responsiveness"), and the tile-provider follow-up. Written in step 1; status Accepted once the user approves it.

## Target structure

```
src/
  components/
    Sidebar/        Sidebar.tsx, Sidebar.module.css   # shell: header, toggle, scroll body
    EventList/      EventList.tsx, EventList.module.css
    EventCard/      EventCard.tsx, EventCard.module.css   # renamed from EventPanel
    Filters/        (restyled)
    Map/            Map.tsx, Map.module.css (mapArea wrapper lives in App)
      leaflet/      LeafletMap.tsx (+ marker icons, ResizeObserver, panTo, tile filter)
  config/layout.ts  # MOBILE_QUERY = '(max-width: 767px)', mirrored by the CSS media queries
  hooks/useMediaQuery.ts
  variables.css     # + --surface-color, --border-color
```

State stays in `App`: `selectedId`, filter texts, and new `isSidebarOpen`. `isMobile` comes from `useMediaQuery(MOBILE_QUERY)`; `isSidebarOpen` starts as `!isMobile`. `selectEvent(id)` sets `selectedId` and, on mobile, `isSidebarOpen = false`.

## Steps

Each step ends with the app building and working, stops for approval, then is committed with its `TASKS.md` items ticked.

1. **ADR-010** [15m]. `docs/adr/010-ui-design.md`, and the ADR list in `AGENTS.md`. Amend nothing else yet.
2. **Tokens and base styles** [25m]. Import `./variables.css` in `main.tsx`; add `--surface-color` and `--border-color` (`color-mix` of `--primary-font-color` into `--background-color`, about 8% and 20%); `index.css` sets `body` background, color, `--text-font`, and heading `--title-font`; `color-scheme: dark light`. Replace hard-coded colors in the existing CSS Modules with tokens so the current UI already follows the theme. Verify in both themes.
3. **Fonts** [15m]. `npm i @fontsource-variable/montserrat @fontsource/ibm-plex-mono` (exact versions, matching the repo's pinned style), import in `main.tsx` (Plex Mono weights 400 and 500 only). Verify the files are bundled and no external request is made.
4. **App layout and Sidebar shell** [40m]. New `Sidebar` (header with app name and city from `config/city.ts`, scroll body). `App` renders `Sidebar` (Filters + the current panel inside) and a `mapArea` wrapper (`position: relative`) around `Map`. Desktop fixed-width column using spacing tokens and `--surface-color`. Add `config/layout.ts`.
5. **Collapsible desktop sidebar** [30m]. `isSidebarOpen` state, toggle `<button>` with `aria-expanded` and `aria-controls` in the header, collapsed state hides the body and narrows the sidebar to a rail with only the toggle. Adapter: `ResizeObserver` on the map container calling `invalidateSize` (via `useMap`), cleaned up on unmount. Manual check: no gray tile strips after toggling.
6. **Filters restyle** [30m]. Compact layout in the sidebar, tokens only, visible focus styles, error text with `--secondary-color`. No behavior change; existing tests untouched.
7. **Event list** [45m]. `EventList` of `<button>` rows (title and `formatEventDate`), `aria-pressed` on the selected row, fed `visibleEvents`, selecting calls `selectEvent`. Sits under `Filters` in the sidebar body. Tick the backlog results-list item.
8. **Event card** [45m]. Rename `EventPanel` to `EventCard` (`git mv`), render only when an event is selected, absolutely positioned top-right inside `mapArea` over the map, `--surface-color` with border and radius, title, date, description, close button. Remove the empty-state text (the list now covers discovery). The empty state remains for no matches in `Filters`.
9. **Mobile drawer** [60m]. Below the breakpoint the sidebar becomes `position: fixed` bottom sheet: rounded top corners, handle button (`aria-expanded`), peek height shows the handle and header, open height about 60% of `dvh` with safe-area bottom padding. `useMediaQuery` hook (`useSyncExternalStore` on `matchMedia`) and `isSidebarOpen` initialised from it. Desktop and mobile share the toggle.
10. **Mobile card and selection** [20m]. Card docked above the collapsed drawer on mobile (full width, `max-height` with scroll); `selectEvent` collapses the drawer on mobile. Marker click uses the same function.
11. **Markers and pan** [45m]. In the adapter: `L.divIcon` round markers styled by a CSS Module (circle in `--highligth-color`; selected gets a larger ring in `--highligth-tertiary-color`), icons memoized by selected state, remove `setupLeafletIcons.ts` and the Leaflet PNG imports, and `panTo` the selected marker when `selectedId` changes (no `MapProps` change). Boundary check: `grep -rn "leaflet" src`.
12. **Dark map and controls** [20m]. CSS filter (invert, hue-rotate, brightness, contrast) on the tile pane under `prefers-color-scheme: dark`, in the adapter CSS; restyle Leaflet zoom buttons and the attribution box with tokens. Verify attribution is readable in both themes.
13. **Visual and a11y check** [30m]. Dark and light, desktop expanded and collapsed, mobile at ~375px (peek, open, card), keyboard-only pass (toggle, list, card close, filter), contrast of text and markers. Fix what shows up.
14. **Final review**. Run `npm run lint`, `typecheck`, `test`, `format`, `build`; run the `code-reviewer` agent on the whole milestone diff and address findings; tick the remaining `TASKS.md` items.

## Tests

No new pure logic, so no new unit tests are expected. The existing suite (filters, dates, schema) must keep passing. `useMediaQuery` and the layout are verified manually (Vitest here has no DOM environment, and adding one is out of scope). If any step introduces a pure function, it goes in `utils/` with a test.

## Timebox

Steps sum to ~7h (15 + 25 + 15 + 40 + 30 + 30 + 45 + 45 + 60 + 20 + 45 + 20 + 30 = 420 min). The heading in `TASKS.md` said ~5.5h; that was a miscount of its own task list, now corrected to ~7h. If a step overruns by 50%, stop and reassess scope. Likeliest overruns: step 9 (viewport units and iOS safe area) and step 12 (filter looks poor; fallback is leaving the tiles light, or the tile-provider ADR).

## Risks

- Tile filter quality is subjective; the backlog follow-up covers a proper dark basemap.
- `ResizeObserver` plus `invalidateSize` while the map is mid-transition: use no CSS width transition on the sidebar if it causes strips, or call `invalidateSize` on `transitionend`.
- Removing the default Leaflet icon setup must not break anything else that uses default markers (there is none today).
- Fonts add about two woff2 files per family to the bundle; fine for a static site.

## Revision (after step 7, user feedback)

- Two scroll areas in the sidebar looked wrong, so event details now expand inside the selected list row. There is no `EventPanel`, no floating card (step 8) and no docked mobile card (step 10). Step 8 became "expandable rows" and is done together with step 7
- The selected row has a tinted highlight (`--selected-color`, a new derived token in `variables.css`), and the selected marker uses the solid highlight color. The `divIcon` markers from step 11 were done early; the pan to the selected marker remains in step 11
- Step 10 is reduced to checking that the drawer stays open on selection and the expanded row scrolls into view
- ADR-010, `TASKS.md`, `docs/code-standards.md` and `TRD.md` are updated to match

## Revision 2 (user feedback on the list)

- The event list did not work well and was removed (step 7 dropped). Selecting a marker shows the event's details in a sidebar section under the filters, on the highlight background (`EventDetails`, replacing the briefly used `EventList`). Markers are the only way to select an event again, so the "results list" backlog item is open again
- Pan to the selected marker (step 11) now only matters for off-screen markers and is optional
- ADR-010, `TASKS.md`, `docs/code-standards.md` and `TRD.md` are updated to match

## Revision 3 (`change-ui.md`: palettes, markers, mobile drawer)

Input: `change-ui.md` with `dark-mode-pallete.png`, `light-mode-palette.png` and `mobile-bug.png`. The three PNGs are temporary: they stay untracked in the repo root, are never committed, and are deleted when steps A-D are finished (the palette values are recorded in the table below). Four new steps, A-D, run before the remaining original steps (pan, dark map, visual check, final review). Each is one commit after approval, as before.

### Palettes (from the images)

| Role | Dark | Light |
| --- | --- | --- |
| Background | `#004643` | `#f8f5f2` |
| Headline | `#fffffe` | `#232323` |
| Paragraph | `#abd1c6` | `#222525` |
| Button / highlight | `#f9bc60` | `#078080` |
| Button text | `#001e1d` | `#232323` |
| Stroke | `#001e1d` | `#232323` |
| Main | `#e8e4e6` | `#fffffe` |
| Secondary | `#abd1c6` | `#f45d48` |
| Tertiary | `#e16162` | `#f8f5f2` |

Mapping onto the existing tokens (approved by the user): `--background-color` = background; `--secondary-font-color` = headline; `--primary-font-color` = paragraph; `--highligth-color` = button/highlight; `--secondary-color` and `--highligth-*-color` keep following the palette's secondary and tertiary values. New tokens: `--button-text-color`, `--stroke-color`, and `--error-color` (dark `#e16162`, light `#f45d48`), because the palettes' "secondary" is not an error color in the dark theme (it equals the paragraph color), so the current use of `--secondary-color` for errors must move to `--error-color`. `--surface-color`, `--border-color` and `--selected-color` stay derived with `color-mix`, so they follow the new palettes.

Contrast pre-check (WCAG ratio, estimated from the derived colors; 4.5 is the AA target for body text, 3 for UI shapes):

- Dark: paragraph on background 6.5, on surface 5.5 (fine); headline on selected 5.4 (fine), but **paragraph on selected 3.3 (fails)**, so the description in the selected details uses the headline color, or the selected mix is lowered
- Light: paragraph on background 14.2 (fine); selected tint with paragraph 8.4 (fine); highlight teal on surface 3.8 (fine for borders and shapes, not for small text); **button text `#232323` on teal `#078080` is 3.3 (fails)**. Options: keep the palette (fails for small text), or use `#fffffe` on teal (about 4.8). The user approved the plan's default: the palette value for large or bold button text only, with `#fffffe` if any small text needs it

### Steps

- **A. Palette** [30m]. Replace the values in `src/variables.css` (dark default, light under `prefers-color-scheme: light`), add the three tokens, move error styles in `Filters.module.css` to `--error-color`, use the headline color for the description text on the selected background, and amend ADR-010 (palette, token mapping and the contrast decisions). Verify with screenshots in both themes (Chrome headless can emulate `prefers-color-scheme`)
- **B. Teardrop markers** [30m]. In `markerIcons`: a square rotated 45 degrees with `border-radius: 50% 50% 50% 0`, anchored at the tip (`iconAnchor` bottom center), tooltip offset updated. Every marker has a 1px border in `--stroke-color` (user decision); the selected one differs by the highlight fill and a larger size. Drop the old selected ring. The marker stays inside the adapter (ADR-005)
- **C. Drawer cannot be reopened** [10m]. Not reproducible in headless Chrome at 412x924: after collapsing, the strip with the chevron stays visible and tapping it reopens the drawer. The user confirmed they cannot scroll in their setup, which matches `mobile-bug.png`: DevTools device mode in an IDE window at 100% zoom, with an emulated viewport (924px) taller than the visible area, so the fixed bottom strip is outside the visible part. Treated as an emulator artifact, not an app bug. The step is only a check: the user sets the DevTools zoom to "Fit to window" (or picks a shorter device) and confirms the strip is visible and reopens the drawer; if it still fails, the user sends a new screenshot and the step becomes a fix. No code change is planned beforehand
- **D. Full-screen drawer on selection** [35m]. Three drawer sizes on mobile: collapsed (strip), open (60dvh), full (100dvh). Selecting a marker grows the drawer to full screen. Closing the details (the close button) returns the drawer to **open** (60dvh), not full screen and not collapsed (user decision), whatever size it had before. Implementation: derive the mobile height from `isSidebarOpen` and whether an event is selected (full = open and selected), plus closing the details keeps `isSidebarOpen` true; no extra state. The collapse chevron during full screen collapses to the strip and keeps the selection; reopening it shows full screen again. Desktop is unchanged (sidebar opens on selection and stays as is). The pan step is desktop-only afterwards

### Effects on the rest of the plan

- Pan to the selected marker (step 11): desktop only
- Dark map (step 12): the dark palette is teal, so a gray inverted OSM map may clash; tune the filter (hue, brightness) to the palette and check it against the highlight markers. The tile-provider backlog item gains weight if it looks poor
- Visual check (step 13) covers both palettes and the three mobile drawer sizes
- ADR-010 is amended in step A. No other ADR is needed

### Timebox

Steps A-D add 105 minutes (30 + 30 + 10 + 35), and the dark map and visual check grow by 15 minutes. Milestone 6 is now ~9h in `TASKS.md`, against ~7h in revision 1 and ~5.5h at the start. That is over the 50% overrun rule for the milestone, so scope was reassessed with the user: B and D are requirements, C shrank to a check. If a further cut is needed, the pan step and the visual check polish go first.
