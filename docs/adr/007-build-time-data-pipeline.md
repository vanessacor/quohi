# ADR-007: Build-time data pipeline (Python, Wikidata/Wikipedia)

- Status: Accepted
- Date: 2026-10-18
- Amends: TRD.md section 6 and CLAUDE.md ("no external data APIs")

## Context
`notes/wiki-plan.md` proposes generating `events.json` from Wikidata and Wikipedia instead of writing it by hand. The MVP constraint "no external data APIs" was meant to keep the deployed site static and free of runtime dependencies, not to forbid preparing the dataset offline.

## Decision
- "No external APIs" now means **no external APIs at runtime**. The deployed site only ships static files.
- Dataset preparation runs locally as Python scripts in `scripts/` (with `requirements.txt`). They are developer tools, not a backend: they are never deployed and never called by the frontend.
- The frontend stays TypeScript (ADR-004) and keeps importing the bundled `src/data/events.json`.
- Pipeline: Wikidata SPARQL -> normalize -> enrich from Wikipedia -> dedupe by QID -> validate -> export. Scope is Xi'an only, inside the bounding box in the city config.
- The exported file is capped at **20 events** (the script ranks and truncates). A person reviews the output before it is committed.
- Scripts cache responses and respect the Wikimedia usage policies. Missing data stays missing; nothing is guessed.
- The output must pass the same validation as hand-written data (`parseEvents`).

## Consequences
- A second language (Python) is added to the repo, for build-time use only
- The dataset is reproducible and sourced, but still needs manual fact-checking
- Data refresh stays a manual local task; multi-city and live updates remain out of scope
