# ADR-003: React + Vite + Leaflet, npm

- Status: Accepted
- Date: 2026-10-11
- Amended by: ADR-004 (TypeScript), ADR-005 (map adapter boundary)

## Context
The MVP needs a simple interactive map with a side panel and filter, built in ~12 hours with a map library that is low risk.

## Decision
Use React with Vite, Leaflet with OpenStreetMap tiles (no API key), CSS Modules, and npm as the package manager (the TRD suggested pnpm).

## Consequences
- Leaflet is simple and free; vector map features are out of scope
- React state is enough for selection and filter; no state library
- npm needs no extra tooling install
