# Code Standards

How code is written: TypeScript, React, CSS, structure, testing and git. Domain and data rules (event schema, validation, filtering) live in `docs/business-rules.md`.

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
  config/                # app configuration
  data/                  # static data files and their validated exports
  hooks/
  types/                 # shared types
  utils/                 # pure, unit-tested functions
  App.tsx
```
Each component lives in its own folder with `Name.tsx` and `Name.module.css`.

## Map library boundary
- Only files in `src/components/Map/leaflet/` may import `leaflet` or `react-leaflet`
- The rest of the app uses our own types from `src/types/` and the `Map` props interface, never Leaflet types
- Configuration values (e.g. the city's center, zoom and bounds in `src/config/city.ts`) live in `src/config/`, not in components

## Naming
- Components: `PascalCase`; hooks: `useThing`; utils/vars: `camelCase`
- CSS Module classes: `camelCase`

## Logic
- Keep logic in pure functions in `utils/` so it can be unit tested
- Components stay presentational where possible

## Testing
- Unit test every function in `utils/` with Vitest (ADR-006); `npm test` must pass
- Test files sit next to the code as `name.test.ts` and import `describe`, `it`, `expect` from `vitest`
- Manually verify map interactions

## Git
- Small commits, imperative messages
