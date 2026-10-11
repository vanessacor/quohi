# Plan: Milestone 1 - Setup & Map

Based on the approved `research.md` (decisions: TypeScript, react-leaflet behind an adapter, Xi'an bounds proposed here, scaffold into repo root). Timebox: ~2h45m including the ADR and doc updates; if any step overruns by 50%, stop and reassess.

## Decisions needing ADRs (to be written during implement)
- **ADR-004: TypeScript.** Amends ADR-003 (React + Vite + Leaflet, JS implied). Reason: type-safe event schema and adapter interface.
- **ADR-005: Map adapter boundary.** All `leaflet`/`react-leaflet` imports confined to `src/components/Map/leaflet/`; app code uses our own types. Reason: react-leaflet's latest release is Dec 2024 and Leaflet is on 1.9.x with only a 2.0 alpha; migration must stay cheap. Thin layer only, no provider plugin system.

## Proposed Xi'an config (for your review)
```ts
name: "Xi'an, China"
center: { lat: 34.3416, lng: 108.9398 }   // city centre (Bell Tower area)
zoom: 11
bounds: { south: 34.05, west: 108.60, north: 34.60, east: 109.45 }
```
Rationale: covers the walled city and urban core, the Han and Tang sites around it, Huaqing Pool and the Terracotta Army in Lintong (~34.38, 109.28), and the surrounding suburbs, without much of the Qinling mountains to the south. The bounds are used later to validate event coordinates (Milestone 2); they are not applied as `maxBounds` on the map yet. Tell me if you want them tighter or looser.

## Files

### Created
- `package.json`, `package-lock.json`, `index.html`, `vite.config.ts`, `tsconfig*.json`, `eslint.config.js` (from the Vite `react-ts` scaffold)
- `.prettierrc`
- `src/main.tsx`, `src/App.tsx`, `src/App.module.css`
- `src/types/map.ts` - `LatLng`, `Bounds`, `MapMarker`
- `src/config/city.ts` - city config using our types
- `src/components/Map/Map.tsx` - library-agnostic component and props
- `src/components/Map/Map.module.css` - full-height container
- `src/components/Map/leaflet/LeafletMap.tsx` - react-leaflet implementation (`MapContainer`, `TileLayer`, markers)
- `src/components/Map/leaflet/setupLeafletIcons.ts` - default marker icon fix
- `docs/adr/004-typescript.md`, `docs/adr/005-map-adapter-boundary.md`

### Changed
- `.gitignore` - add `node_modules`, `dist`, keep `/notes`
- `docs/code-standards.md` - `.jsx` -> `.tsx`; add `config/` and `types/` to the structure; add the adapter-boundary rule and "no `any`"; note CSS Modules typing
- `CLAUDE.md` - stack line (TypeScript), commands (`npm run format`, `npm run typecheck`), pointer to ADR-004/005
- `docs/adr/003-react-vite-leaflet.md` - add "Amended by ADR-004, ADR-005" line
- `TRD.md` - structure section updated for `.tsx`, `config/`, `types/`
- `TASKS.md` - tick Milestone 1 items as done; adjust the icon-fix and config items to match

## Step approval and commits
Applies to every numbered step below:
1. Do the step, then stop and report what changed and how it was verified.
2. Wait for the user's explicit approval. Do not start the next step before it.
3. After approval, commit that step's changes only, with an imperative message (e.g. `Scaffold Vite react-ts project`) ending with the attribution line from the session. Stage specific files, not `git add -A`.
4. If the user requests changes, make them, re-report, and wait for approval again before committing.
Step 1 is the first commit on `main`; the existing untracked docs (`PRD.md`, `TRD.md`, `product-vision.md`, `CLAUDE.md`, `TASKS.md`, `docs/`, `.claude/`, `.gitignore`) are committed separately as a "Add project docs and workflow" commit before it, once the user approves.

Timebox note: approval pauses are not counted against the ~2h45m.

## Steps
1. **Scaffold (30m).** In a scratch directory (`/tmp/claude-1000/-web-quohi/59800cd3-4ac7-48a3-912a-c21c48a566ae/scratchpad/scaffold`), run `npm create vite@latest` with the `react-ts` template. Inspect what Vite 8 generated (plugin, ESLint config, scripts). Copy into the repo root with `cp -n` (no overwrite), and handle `.gitignore` by merging by hand. Delete template demo assets (logo, counter CSS). Run `npm install`. Confirm `npm run dev` starts.
2. **Prettier + lint (20m).** Install `prettier` and `eslint-config-prettier`; wire it into the ESLint flat config; add scripts `format`, `typecheck` (`tsc -b --noEmit` or what the template uses). Run `npm run lint`.
3. **Map deps (20m).** `npm install leaflet react-leaflet` and `npm install -D @types/leaflet`. Pin to the researched versions (leaflet 1.9.4, react-leaflet 5.0.0).
4. **Types and config (20m).** Write `src/types/map.ts` and `src/config/city.ts` with the proposed values above.
5. **Map adapter (40m).**
   - `Map.tsx` exposes props `{ center, zoom, markers?, selectedId?, onMarkerClick? }` (our types only) and renders `LeafletMap`.
   - `LeafletMap.tsx` is the only place importing `react-leaflet`/`leaflet`, including `leaflet/dist/leaflet.css`. Converts our `LatLng` to Leaflet tuples internally. Uses OSM tiles with attribution.
   - Markers props exist in the interface now (empty in this milestone) so Milestone 2 doesn't change the contract.
   - `Map.module.css`: container `height: 100vh; width: 100%`.
6. **Icon fix (10m).** `setupLeafletIcons.ts` imports the marker images from `leaflet/dist/images` and sets `L.Icon.Default` options; called from `LeafletMap.tsx` at module load (inside the adapter folder).
7. **Wire up App (10m).** `App.tsx` renders `<Map center={city.center} zoom={city.zoom} />`. Remove template leftovers.
8. **Verify (20m).**
   - `npm run lint`, `npm run typecheck`, `npm run build` all pass
   - `npm run dev`: map is centred on Xi'an, tiles load, attribution visible, pan and zoom work, no console errors under StrictMode
   - Temporarily add one marker at the city centre to confirm the icon fix, then remove it
   - Grep check: `grep -rn "leaflet" src --include=*.ts --include=*.tsx` shows matches only under `src/components/Map/leaflet/`
9. **Docs and ADRs (25m).** Write ADR-004 and ADR-005, make the doc changes listed above, tick `TASKS.md`.
10. **Review (10m).** Run the `code-reviewer` agent on the diff and address findings.

## Tests
- No unit tests this milestone: there is no logic yet beyond config and rendering. Vitest is introduced in Milestone 4 with the overlap filter (per `TASKS.md`).
- Verification is lint + typecheck + build + manual dev-server check, plus the grep boundary check in step 8.

## Out of scope
Vite `base` / deploy workflow (Milestone 5), event data and markers (Milestone 2), side panel (Milestone 3), `maxBounds` on the map.

## Risks
- Vite 8 scaffold differs from expectations (mitigated by inspecting it in a scratch directory first).
- Scaffold collides with existing files (mitigated by `cp -n` and manual `.gitignore` merge).
- OSM tile policy: fine for a low-traffic MVP; revisit if traffic grows.
