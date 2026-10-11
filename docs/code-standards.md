# Code Standards

## General
- Keep it simple; no abstractions until used twice
- Function components and hooks only; no class components
- Plain React state (`useState`, `useMemo`); no state libraries
- oxlint must pass; Prettier formatting (`npm run lint`, `npm run format`)

## Components
- Keep components small and scoped: one clear responsibility each. If a component does more than one thing, or grows hard to read at a glance, split it
- Avoid repetition: when the same markup or logic appears more than once, extract it into a reusable component (or a hook / `utils/` function for non-visual logic)
- Reusable pieces take props rather than hard-coding values, and stay free of app-specific state where possible
- Don't extract speculatively: extract on the second use, not before

## Structure
```
src/
  components/
    Map/
    EventPanel/
    Filters/
  data/events.json
  hooks/
  utils/        # pure functions: date formatting, overlap filter, validation
  App.jsx
```
Each component lives in its own folder with `Name.jsx` and `Name.module.css`.

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
