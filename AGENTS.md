This file provides guidance to AI Agents when working with code in this repository.


Frontend-only web app showing ~10-20 historical events as markers on a map. Clicking a marker opens a side panel; a year-range filter controls which markers show.

Source docs: `PRD.md` (what), `TRD.md` (how), `product-vision.md` (direction). Decisions that override them live in `docs/adr/`.

## Stack

- Vite + React + **TypeScript**, Leaflet (OpenStreetMap tiles), CSS Modules
- Leaflet is isolated behind an adapter in `src/components/Map/leaflet/` so the map library can be swapped (ADR-005)
- Package manager: **npm**
- Data: static `src/data/events.json` (max 20 events), bundled at build time
- Data preparation: local Python scripts in `scripts/` (Wikidata/Wikipedia, Ollama + Qwen3 summaries); build-time only, never deployed (ADR-007, ADR-008)
- Deploy: GitHub Pages

## Commands

- `npm install` - install deps
- `npm run dev` - dev server
- `npm run build` - production build
- `npm run lint` - oxlint
- `npm run typecheck` - TypeScript check
- `npm test` - unit tests (Vitest)
- `npm run format` - Prettier (code only; docs are excluded)

## Hard constraints (MVP)

- No backend, database, auth, or multi-city support
- No external APIs at runtime; the deployed site is static. Offline data-prep scripts may call Wikimedia APIs (ADR-007)
- No state libraries (Redux etc.); React state/hooks only
- Max 20 events; keep the dataset small, don't over-invest in accuracy
- Simplicity over completeness; timebox every task (~12h total budget)
- AI never decides architecture: propose options, the user decides, record in an ADR

## Event schema

Single unified schema (see `docs/business-rules.md`). Dates are a signed `year` (negative = BCE) with optional `month` and `day`. Optional enrichment fields: `locationName`, `summary`, `image`, `sources` (ADR-009). Do not add fields without an ADR.

## Architecture decisions

See `docs/adr/`: 001 GitHub Pages, 002 flexible date schema, 003 React + Vite + Leaflet + npm, 004 TypeScript, 005 map adapter boundary, 006 Vitest, 007 build-time data pipeline, 008 local AI summaries, 009 event schema extension.

## Workflow

Every non-trivial task follows Research -> Plan -> Implement (`docs/rpi-workflow.md`), using `/research`, `/plan`, `/implement`. Stop for user approval between phases. During implement, each plan step needs user approval and is committed after approval, before the next step starts. Before finishing, run the `code-reviewer` agent on the diff.

Progress is tracked in `TASKS.md`; tick items as they are completed.

## Conventions

Follow `docs/code-standards.md` for code and `docs/business-rules.md` for domain and data rules.
