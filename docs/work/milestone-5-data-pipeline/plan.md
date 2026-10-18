# Milestone 5 — Data Pipeline: Plan

Phase 2 of RPI, based on the approved `research.md`. No code changes in this phase.

## Decisions carried in from approved research

- A1: a committed **curated QID list** drives the pipeline. The 16 existing events are mapped to QIDs and re-derived; a diff against the current `events.json` is reviewed by the user, who decides per event whether Wikidata or the hand-written value wins
- B1: **hybrid discovery**. Two small queries write a ranked *candidates* file; the user picks up to 20 into the curated list. Ranking by Wikipedia sitelink count
- C1 + C3: `description` is the Wikidata description (CC0) for new events; existing hand-written descriptions are kept where they exist. The AI summary is Milestone 6
- D1: the type/validator update for the optional fields and QID ids moves from Milestone 6 to **the start of Milestone 5**
- E1: `scripts/` with a gitignored `.venv`, `requirements.txt` containing `requests` only, a gitignored response cache, pure functions tested with stdlib `unittest`; the exported file is also checked by the existing Vitest `events.test.ts`

## ADR needed?

**None.** All within ADR-007 and ADR-009. The validator change implements ADR-009 as written.

## Files

| File | Action |
| --- | --- |
| `src/types/event.ts` | change — optional `locationName`, `summary`, `image`, `sources` |
| `src/utils/eventValidators.ts` (+ `parseEvents.ts`) and tests | change — QID ids, optional fields, URL checks |
| `scripts/requirements.txt` | create — `requests` |
| `scripts/common.py` | create — HTTP session with User-Agent, delay, file cache; WDQS time parsing |
| `scripts/config/scope.json` | create — class whitelists (events, landmarks), bounding box mirrored from `city.ts` |
| `scripts/config/curated.json` | create — chosen QIDs plus per-event overrides (e.g. kept description) |
| `scripts/fetch_events.py` | create — candidate discovery |
| `scripts/enrich_events.py` | create — Wikipedia summary, links, image and license |
| `scripts/export_events.py` | create — normalize, dedupe, validate, diff, write `src/data/events.json` |
| `scripts/tests/` | create — `unittest` tests for the pure functions |
| `.gitignore` | change — `scripts/.venv/`, `scripts/.cache/`, `__pycache__/` |
| `AGENTS.md` | change — data-script commands |
| `src/data/events.json` | change — regenerated, reviewed by the user |
| `TASKS.md` | change — see "Task list changes" |

## Python conventions (short, no ADR)

Type hints on every function; small pure functions for parsing and normalizing, with I/O (HTTP, files) kept at the edges; no dependencies beyond `requests`; descriptive `User-Agent` with a contact; sequential requests with a small delay; every network response cached on disk so re-runs do no network calls; scripts exit non-zero with a clear message on bad data.

## Task list changes (applied in step 1)

- Move "Update `HistoricalEvent`, `parseEvents` and tests for the optional fields [30m]" from Milestone 6 to the top of Milestone 5 (estimate raised to 45m: QID ids and URL checks added)
- Split "Define scope and confirm the bounding box" into scaffold step 2 (scope config) and tick it there
- Add "User curates the QID list" as its own item
- Milestone 5 total becomes ~4.7h (was ~4h); Milestone 6 loses 30m

## Ordered steps

For every step: implement, run the checks listed, run the `code-reviewer` agent on the step's diff and address findings, report to the user, and **commit only after approval**, with the matching `TASKS.md` items ticked in the same commit.

### 1. Types and validator for the new fields [45m] → ticks the moved "Update `HistoricalEvent`, `parseEvents` and tests"
- `HistoricalEvent`: optional `locationName`, `summary`, `image { url, license?, attribution? }`, `sources { wikipedia?, wikidata? }`
- Validator: `id` accepts kebab-case **or** `^Q[0-9]+$`; new fields are non-empty strings or well-formed objects; `image.url` and `sources.*` must be `http(s)` URLs; unknown fields inside `image`/`sources` are rejected; `KNOWN_FIELDS` extended. Apply the "image only with attribution" rule at display time (Milestone 6), not in the validator
- Tests for each new rule (valid and invalid), existing tests unchanged
- Apply the `TASKS.md` changes above
- Checks: `npm test`, lint, typecheck, build

### 2. Python scaffold and scope config [20m] → ticks "Define historical event scope and confirm the bounding box"
- `scripts/requirements.txt`, `.gitignore` entries, `common.py` (session, cache, delay, `parse_wikidata_time(value, precision)` returning year/month/day or an error)
- `scope.json`: event classes (battle, coup, mutiny, incident, protest, siege, rebellion, treaty, ...) and landmark classes (pagoda, Buddhist temple, mosque, tomb, palace, city gate, archaeological site, mausoleum, cathedral, ...); bounding box copied from `city.ts` with a test asserting they match
- Tests: time parsing for year/month/day precision, rejection of decade/century precision, **BCE convention verified against a known BCE item** (the open unknown from research)
- Checks: `python -m unittest discover scripts/tests`

### 3. `fetch_events.py` [75m] → ticks "`fetch_events.py`: Wikidata SPARQL with local caching"
- Q1: items of the explicit event classes located (`P276`/`P131`) in Xi'an, with date and optional own coordinates. Q2: items with inception inside the bounding box, whitelisted class, English Wikipedia article, with sitelink count. No `P279*` property paths (they time out)
- Writes `scripts/.cache/candidates.json` and prints a ranked table (QID, title, date, precision, class, own-coordinates yes/no, sitelinks)
- Also resolves the 16 existing events to QIDs (by label search) and prints the mapping for confirmation
- Checks: unit tests on query result parsing with saved fixtures; one live run

### 4. User curates the QID list [20m, user] → ticks "User curates the QID list"
- Together we fill `scripts/config/curated.json`: up to 20 QIDs, the confirmed mapping for the existing events, and overrides (keep hand-written description, exclude a field, ...)
- No code; the user decides, the list is committed

### 5. `enrich_events.py` [50m] → ticks "`enrich_events.py`: Wikipedia extracts, links and images"
- For each curated QID: Wikipedia REST summary (title, `content_urls`, thumbnail) and, when an image exists, Commons `extmetadata` for license and attribution (strip the `utm_` query string, URL-decode the file name, strip HTML from the artist)
- No image or no license found = no `image` (missing data stays missing)
- Output cached enriched records; tests on the pure helpers (file name extraction, HTML stripping) using fixtures
- Checks: unit tests; one live run for the curated list

### 6. `export_events.py` and review [40m + 30m user review] → ticks "Normalize to the schema, dedupe by QID, validate, export" and "User reviews and fact-checks the output"
- Merge curated + enriched into the schema: `id` = QID, date from Wikidata (precision-checked), coordinates (own `P625` only; reject city-level or out-of-bounds), `description` per C1/C3, `sources`, optional `image`/`locationName`
- Refuse to write if more than 20 events, any duplicates, or any missing required field; sort by year then id
- Print a review table and a per-event diff against the current `events.json`, then write `src/data/events.json`
- The user fact-checks the table and diff; fixes go into `curated.json` overrides and the script is re-run
- Checks: `npm test` (existing `events.test.ts` and `parseEvents` validate the output), lint, typecheck, build, and a manual look at the map and panel with the new data

## Final checks (after step 6)
- `npm test`, `npm run lint`, `npm run typecheck`, `npm run build`, and the Python tests
- Run the `code-reviewer` agent once more on the whole Milestone 5 diff and address findings
- Update `AGENTS.md` with the data-script commands

## Timebox

~280 minutes of work (45 + 20 + 75 + 20 + 50 + 40 + 30) against the ~4.7h now budgeted for Milestone 5 in `TASKS.md`. If any step overruns by 50%, stop and reassess scope. Likeliest overrun: step 3 (SPARQL tuning), where the fallback is dropping Q1 and relying on Q2 plus a hand-picked event list.
