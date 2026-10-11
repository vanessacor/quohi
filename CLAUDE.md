# Historical Events Map (quohi)

Frontend-only web app showing ~10-20 historical events as markers on a map. Clicking a marker opens a side panel; a year-range filter controls which markers show.

Source docs: `PRD.md` (what), `TRD.md` (how), `product-vision.md` (direction). Decisions that override them live in `docs/adr/`.

## Stack

- Vite + React, Leaflet (OpenStreetMap tiles), CSS Modules
- Package manager: **npm**
- Data: static `src/data/events.json` (max 20 events)
- Deploy: GitHub Pages

## Commands

- `npm install` - install deps
- `npm run dev` - dev server
- `npm run build` - production build
- `npm run lint` - oxlint
- `npm run typecheck` - TypeScript check
- `npm run format` - Prettier (code only; docs are excluded)

## Hard constraints (MVP)

- No backend, database, auth, external data APIs, or multi-city support
- No state libraries (Redux etc.); React state/hooks only
- Max 20 events; keep the dataset small, don't over-invest in accuracy
- Simplicity over completeness; timebox every task (~12h total budget)
- AI never decides architecture: propose options, the user decides, record in an ADR

## Event schema

Single unified schema (see `docs/code-standards.md`). Dates are a signed `year` (negative = BCE) with optional `month` and `day`. Do not add fields without an ADR.

## Workflow

Every non-trivial task follows Research -> Plan -> Implement (`docs/rpi-workflow.md`), using `/research`, `/plan`, `/implement`. Stop for user approval between phases. During implement, each plan step needs user approval and is committed after approval, before the next step starts. Before finishing, run the `code-reviewer` agent on the diff.

Progress is tracked in `TASKS.md`; tick items as they are completed.

## Conventions

Follow `docs/code-standards.md`.
