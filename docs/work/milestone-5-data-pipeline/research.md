# Milestone 5 — Data Pipeline: Research

Phase 1 of RPI. Findings, constraints, options, recommendation. No code changes. Probes were run against the live Wikidata Query Service, Wikipedia REST API and Commons API (scratch scripts only, nothing added to the repo).

## Current state

- `src/data/events.json` holds **16 hand-written events** (user fact-checked), ids are kebab-case slugs (`big-wild-goose-pagoda-built`). Most are the construction or founding of a landmark (pagodas, mosque, city wall, mausoleum, palaces), plus a few real events (Xi'an Incident, Tang founded, Terracotta Army discovered).
- City config (`src/config/city.ts`): Xi'an, bounds `south 34.05, west 108.6, north 34.6, east 109.45`. `parseEvents` rejects coordinates outside these bounds.
- `parseEvents` currently **rejects unknown fields** and requires kebab-case ids (`^[a-z0-9]+(-[a-z0-9]+)*$`). `docs/business-rules.md` and ADR-009 already allow `Q123` ids and the optional `summary`, `image`, `sources`, `locationName`, but the code does not yet (that update is a Milestone 6 task).
- No `scripts/`, no `requirements.txt`. Python 3.10.12 and `requests` 2.25.1 are installed system-wide. `notes/` is gitignored.
- Network access to Wikidata and Wikimedia works from this machine.

## Findings from the probes

**1. Wikidata has very few real "events" for Xi'an.**
- Entities with their own coordinates in the bounding box **and** a point-in-time (`P585`): only 4 (Xi'an Incident 1936, Xuanwu Gate Incident 626, a 1994 plane crash, and a duplicate).
- Items located in Xi'an (`P276 = Q5826`) with a date: 74, but almost all are **academic conferences and sports championships** with no coordinates. This is noise, not history.
- A query restricted to common event classes (battle, coup, mutiny, protest, ...) returned only 5 usable items: Battle of Chang'an (192), Xuanwu Gate Incident (626), Jingyuan Mutiny (783), Xi'an Incident (1936) and the 2022 protests. Only two have their own coordinates.
- A query using the full class tree (`P31/P279*`) **timed out** (504). Property paths over the class hierarchy are too heavy for WDQS; use explicit class lists.

**2. Dated landmarks are the richest source.** Items in the bounding box with an inception date (`P571`), an English Wikipedia article and a date before 1950 gave 20 results, e.g. Fenghao (~1050 BCE), Terracotta Army (247 BCE), Giant Wild Goose Pagoda (648), Daci'en Temple (1466), St. Francis Cathedral (1716). Roughly half are universities, stations, a diocese or whole states (Han dynasty, Northern Wei), which are not good events or not point locations. A class filter is required.

**3. Wikipedia REST summary** (`/api/rest_v1/page/summary/<title>`) returns, in one call: `extract`, `description`, `wikibase_item` (the QID), `content_urls`, `thumbnail`, `originalimage`, and coordinates. 20 events = 20 requests.

**4. Image licensing works through the Commons API.** For the Giant Wild Goose Pagoda image: `LicenseShortName = CC BY-SA 3.0`, `AttributionRequired = true`, and an `Artist` field that is an HTML snippet (needs tag stripping). Two gotchas found: the REST image URLs carry a `?utm_source=...` query string that must be stripped before looking up the file name, and file names must be URL-decoded.

**5. Dates.** Wikidata times carry a **precision** (9 = year, 10 = month, 11 = day, 8 = decade, 7 = century). Century/decade-precision values do not fit the schema honestly. A BCE value such as `-0247` came back for the Terracotta Army; whether Wikidata's BCE years are offset by one from our "no year 0" convention is **unverified** and must be checked against a known BCE date before trusting any BCE output.

## Constraints

- ADR-007: scripts are local build-time tools, output capped at **20 events**, a person reviews the result, missing data stays missing, responses are cached, Wikimedia policies respected.
- ADR-009 / business rules: an event needs trustworthy coordinates of the event or a specific site (no city-level centroid); an image is shown only with attribution; unknown fields are rejected by the validator.
- Wikimedia policies: send a descriptive `User-Agent` with a contact; keep requests sequential and few; WDQS has a 60 s query timeout.
- Wikipedia text is licensed **CC BY-SA**. Business rules say descriptions are "written for this project, not copied text".

## Decisions needed (user)

### A. What happens to the 16 hand-written events

- **A1 (recommended)**: a committed **curated QID list** (`scripts/config/`) drives the pipeline. The 16 existing events are mapped to QIDs and re-derived from Wikidata, so every event has a source link. The pipeline prints a diff against the existing file; the user reviews it and decides per event whether Wikidata or the hand-written data wins. New events can fill the remaining slots.
- A2: keep the 16 as they are and have the pipeline only add `sources`/`image` by QID. Preserves the fact-checked work but the dataset is then mostly not data-driven, and only 4 slots remain for new events.
- A3: replace the file entirely with whatever the queries return. Fastest but loses reviewed content and the query noise (finding 1) would need heavy filtering.

### B. How candidates are discovered

- **B1 (recommended)**: **hybrid**. Two small queries produce a *candidates file*: (Q1) events from an explicit class list located in Xi'an, (Q2) landmarks with inception in the bounding box from a whitelist of classes (pagoda, temple, mosque, tomb, palace, city gate/wall, archaeological site, mausoleum, cathedral). Candidates are ranked by Wikipedia sitelink count as a significance proxy. The user picks up to 20 into the curated QID list (A1).
- B2: pure seed list of QIDs, no discovery queries. Simplest and fully deterministic, but it does not demonstrate discovery from Wikidata.
- B3: fully automatic top-20 by sitelinks. Reproducible but likely to include universities and stations unless the class filter is perfect.

### C. Source of the `description` field (required, non-empty)

- **C1 (recommended)**: Milestone 5 fills `description` with the **Wikidata description** (CC0, one line, e.g. "Buddhist pagoda in Xi'an"), flagged for the user to expand by hand. Milestone 6 adds the richer AI `summary` from the Wikipedia extract, always shown with a source link.
- C2: copy the first sentences of the Wikipedia extract. Richer, but it is CC BY-SA copied text, contradicting the business rule, and needs attribution handling in the panel.
- C3: keep the existing hand-written descriptions for events that already have one (works naturally with A1) and use C1 only for new events.

### D. Ids and the validator

`parseEvents` rejects QID ids and the new optional fields today. Either:
- **D1 (recommended)**: move the "Update `HistoricalEvent`, `parseEvents` and tests for the optional fields" task from Milestone 6 to the **start of Milestone 5**, so the exporter can write `id` = QID and `sources` (useful for review) and the existing `events.test.ts` validates the output.
- D2: keep slug ids and write only the current core fields until Milestone 6. Pipeline output then has no source links to review, and QIDs need a side mapping file.

### E. Python tooling

- **E1 (recommended)**: `scripts/` with a `.venv` (gitignored) and `requirements.txt` containing `requests` only; cache in `scripts/.cache/` (gitignored); keep normalization logic in pure functions tested with the stdlib `unittest` (no new dependency); the exported JSON is also checked by the existing Vitest `events.test.ts`.
- E2: add `pytest` as a dev dependency. Slightly nicer, one more thing to install.
- E3: no Python tests, rely on the Vitest check of the output only.

## Other design notes

- **Coordinates:** prefer the item's own `P625`. Reject an item whose only coordinate is its city or a district (compare with the Xi'an item's coordinate and the item's class). Reject anything outside the city bounds. Never fall back to the city centroid.
- **Dates:** read value + precision (`psv:` nodes / `wikibase:timePrecision`). Accept precision 9, 10, 11 (map to year / year+month / full date). Reject decade/century precision or flag it for manual dating. Spans use `P580`/`P582` or `P571` + `P576`, mapped to `year`/`endYear` (spans carry no month/day per the schema).
- **Verify the BCE convention** with one known BCE item before generating output (add a unit test with that item).
- **Dedupe** by QID; the exporter sorts by year then id for stable diffs.
- **Pipeline stages** (matching TASKS.md): `fetch_events.py` (queries + cache -> candidates), `enrich_events.py` (Wikipedia summary, links, image + Commons license), normalize/validate/export to `src/data/events.json`. Exact file names can follow the wiki-plan (`export_events.py`) or TASKS (one normalize+export step); the plan will fix them.
- **Manual review:** the export prints a table of title, date, coordinates and source URL for the user to fact-check, and refuses to write more than 20 events or any invalid one.

## Risks

- Event coverage for Xi'an on Wikidata is thin; the final 20 will be mostly landmark foundations, not battles and treaties. This matches the existing dataset but is worth knowing.
- Image licensing needs per-image checks; some Wikipedia images are non-free (fair use) and are not on Commons, so the lookup returns nothing. Those events get no image.
- Wikidata data quality (wrong or imprecise dates and coordinates) can still pass validation; the manual review is the real safeguard.
- The pipeline adds roughly 4 h of work (budgeted separately in `TASKS.md`); moving the validator update into this milestone (D1) shifts ~30 min from Milestone 6.

## Recommendation

A1, B1, C1 (with C3 for events that already have a good hand-written description), D1, E1. No new ADR is needed if these are accepted, since they sit inside ADR-007 and ADR-009. If you choose D2, or want `description` copied from Wikipedia (C2), say so, because C2 conflicts with the business rule and would need either a rule change or an ADR.
