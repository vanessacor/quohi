# Code Standards

## General
- Keep it simple; no abstractions until used twice
- Function components and hooks only; no class components
- Plain React state (`useState`, `useMemo`); no state libraries
- TypeScript everywhere (ADR-004); no `any`. `npm run typecheck` must pass
- oxlint must pass; Prettier formatting (`npm run lint`, `npm run format`)

## Components
- Keep components small and scoped: one clear responsibility each. If a component does more than one thing, or grows hard to read at a glance, split it
- Avoid repetition: when the same markup or logic appears more than once, extract it into a reusable component (or a hook / `utils/` function for non-visual logic)
- No inline styles (`style={{ ... }}`); use CSS Modules
- Reusable pieces take props rather than hard-coding values, and stay free of app-specific state where possible
- Don't extract speculatively: extract on the second use, not before

## Structure
```
src/
  components/
    Map/
      Map.tsx            # library-agnostic component
      leaflet/           # only place that imports leaflet / react-leaflet (ADR-005)
    EventPanel/
    Filters/
  config/                # city config (name, center, zoom, bounds)
  data/events.json
  hooks/
  types/                 # shared types: map types, event type
  utils/                 # pure functions: date formatting, overlap filter, validation
  App.tsx
```
Each component lives in its own folder with `Name.tsx` and `Name.module.css`.

## Map library boundary
- Only files in `src/components/Map/leaflet/` may import `leaflet` or `react-leaflet`
- The rest of the app uses our own types from `src/types/` and the `Map` props interface, never Leaflet types
- City-specific values (name, center, zoom, bounds) live in `src/config/city.ts`, not in components

## Naming
- Components: `PascalCase`; hooks: `useThing`; utils/vars: `camelCase`
- CSS Module classes: `camelCase`

## Logic
- Keep date/filter logic in pure functions in `utils/` so it can be unit tested
- Components stay presentational where possible

## Event schema
```json
{
  "id": "string (unique, kebab-case)",
  "title": "string",
  "year": "integer (negative = BCE, no year 0)",
  "month": "integer 1-12, optional",
  "day": "integer 1-31, optional (requires month)",
  "endYear": "integer, optional (for spans)",
  "lat": "number",
  "lng": "number",
  "description": "string"
}
```
Rules:
- Unique `id`; max 20 events
- Coordinates must fall within the bounds of the configured city
- Precision is implied by which fields are present (year only, year+month, full date)
- Filtering: an event matches if its span `[start, end]` overlaps the selected year range; year-only events cover the whole year
- New fields require an ADR (see ADR-002)

## Testing
- Unit test `utils/` (overlap filter, date formatting, validation)
- Manually verify map interactions

## Git
- Small commits, imperative messages
