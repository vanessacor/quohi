# quohi

An interactive map of historical events in Xi'an, China. Events appear as markers on a map; clicking a marker opens a side panel with the event's title, date and description, and a year-range filter controls which markers are shown.

quohi is a frontend-only static site. The event data is prepared offline and bundled at build time, so the deployed app makes no network calls of its own apart from loading map tiles.

## Purpose

quohi is a personal learning project. Quohi is the vehicle; the goal is to practice AI-assisted development and agentic workflows:

- using AI as a development partner, not an authority: it proposes, a person decides, and every decision is recorded in an ADR
- designing a multi-step process (research, plan, implement, review) with a stop for approval between phases, described in [`docs/rpi-workflow.md`](docs/rpi-workflow.md)
- breaking work into small, AI-executable slices, one feature per session, within a weekend-sized time budget
- separating data, logic and UI, and keeping the scope small to avoid premature complexity

Success means shipping the MVP end to end and leaving behind a process that can be reused in future projects.

## Status

MVP in progress; see [`TASKS.md`](TASKS.md).

- Done: map, markers, side panel, date formatting, year-range filter, data pipeline and a first dataset of 16 events (fact-checking still pending).
- Next: UI design (Milestone 6), AI-generated summaries and images in the event card (Milestone 7), then GitHub Pages deployment (Milestone 8).

## Stack

- Vite, React and TypeScript
- Leaflet with OpenStreetMap tiles, behind an adapter so the map library can be swapped
- CSS Modules
- Vitest for unit tests, oxlint and Prettier
- Python scripts (data preparation only, never deployed)

## Getting started

Requires Node.js and npm.

```sh
npm install
npm run dev
```

| Command | What it does |
|---|---|
| `npm run dev` | Start the dev server |
| `npm run build` | Type-check and build for production |
| `npm run preview` | Serve the production build locally |
| `npm test` | Run the unit tests (Vitest) |
| `npm run lint` | Lint with oxlint |
| `npm run typecheck` | TypeScript check |
| `npm run format` | Format code with Prettier |

## Event data

The app reads `src/data/events.json`, at most 20 events. The file is validated by `parseEvents` when the app loads, and an invalid file fails loudly. Dates are a signed `year` (negative for BCE) with an optional `month` and `day`. The full schema and validation rules are in [`docs/business-rules.md`](docs/business-rules.md).

### Regenerating the data

`events.json` is produced by local Python scripts in [`scripts/`](scripts/) from Wikidata and Wikipedia. They are developer tools: they run on your machine before a release and are never part of the deployed site.

```sh
python3 -m venv scripts/.venv
scripts/.venv/bin/pip install -r scripts/requirements.txt

scripts/.venv/bin/python scripts/fetch_events.py     # discover candidates in Wikidata
scripts/.venv/bin/python scripts/enrich_events.py    # enrich the curated list, write events.json
scripts/.venv/bin/python -m unittest discover scripts/tests
```

- The events to include are chosen by hand in `scripts/config/curated.json`, together with any manual dates or coordinates that override Wikidata.
- Network responses are cached in `scripts/.cache`, so re-runs make no requests.
- Events with a missing date, coordinates or Wikipedia extract are skipped and reported; the pipeline never guesses.
- A person should fact-check the output before it is committed.

## Project layout

```
src/            React app (components, map adapter, utils, config, data)
scripts/        Python data-preparation scripts, config and tests
docs/           Business rules, code standards, workflow and ADRs
```

## Documentation

- [`PRD.md`](PRD.md): what the product does
- [`TRD.md`](TRD.md): how it is built
- [`product-vision.md`](product-vision.md): where it is heading
- [`docs/adr/`](docs/adr/): architecture decisions; they override the documents above
- [`docs/business-rules.md`](docs/business-rules.md) and [`docs/code-standards.md`](docs/code-standards.md): domain and code rules
- [`docs/rpi-workflow.md`](docs/rpi-workflow.md): the research, plan, implement workflow
- [`AGENTS.md`](AGENTS.md): guidance for AI agents working in this repository

## Data sources and attribution

Event text comes from Wikipedia and dates and coordinates from Wikidata. Wikipedia text is available under CC BY-SA; each event links to its source article. Images are Wikimedia Commons thumbnails and are shown only with their author and license. Map tiles are © OpenStreetMap contributors.
