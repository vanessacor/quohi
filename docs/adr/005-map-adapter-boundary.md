# ADR-005: Map adapter boundary

- Status: Accepted
- Date: 2026-10-11
- Amends: ADR-003 (Leaflet as map library)

## Context
`react-leaflet` 5.0.0 was last released in December 2024 and Leaflet is still on 1.9.x with only a 2.0 alpha. We want to be able to move to another library (for example MapLibre GL) without touching the rest of the app.

## Decision
- All imports of `leaflet` and `react-leaflet` live only in `src/components/Map/leaflet/`
- `Map` (`src/components/Map/Map.tsx`) exposes a library-agnostic props interface: `center`, `zoom`, `markers`, `selectedId`, `onMarkerClick`
- The app and config use our own types from `src/types/map.ts` (`LatLng`, `Bounds`, `MapMarker`), never Leaflet types
- Keep the layer thin: no generic "map provider" plugin system

## Consequences
- Replacing the library means rewriting only `src/components/Map/leaflet/`
- One small abstraction exists before its second use, deliberately, which is an exception to the "no abstractions until used twice" rule in `docs/code-standards.md`
- Leaflet-only features need the interface to be extended first, with an ADR if the change is not trivial
- Boundary check: `grep -rn "leaflet" src` should only match the adapter folder (plus `Map.tsx` importing it)
