# Business Rules

Domain rules for the Historical Events Map: what an event is, what makes data valid, and how filtering behaves. How the code is written lives in `docs/code-standards.md`; decisions and their reasons live in `docs/adr/`.

## Scope (MVP)
- One city (Xi'an, China); its name, center, zoom and bounds are defined in `src/config/city.ts`
- At most 20 events, from a static JSON file bundled at build time; no backend and no external APIs at runtime (ADR-007)
- The JSON is prepared offline by local Python scripts (Wikidata/Wikipedia, Ollama summaries) and reviewed by a person before it is committed

## Event schema
Type: `HistoricalEvent` in `src/types/event.ts`. The raw data is `src/data/events.json`, an array of:
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
  "description": "string",
  "locationName": "string, optional",
  "summary": "string, optional (AI-generated, ADR-008)",
  "image": { "url": "string", "license": "string, optional", "attribution": "string, optional" },
  "sources": { "wikipedia": "url, optional", "wikidata": "url, optional" }
}
```
Every data source must reduce to this schema (product vision: a unified event schema). New fields require an ADR (see ADR-002, ADR-009). `id` is the Wikidata QID for pipeline events and kebab-case for hand-written ones.

## Validation rules
Enforced by `parseEvents` in `src/utils/`, run once when `src/data/events.ts` loads:
- Array of 1 to 20 events; each an object
- `id`: non-empty, unique; kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`) or a Wikidata QID (`^Q[0-9]+$`)
- `title` and `description`: non-empty strings
- `year`: integer, not 0; `endYear` (optional): integer, not 0, and `>= year`
- `endYear` cannot be combined with `month` or `day`
- `month`: integer 1-12; `day`: integer, requires `month`, within the month's length (February allows 29 in any year; no leap-year logic)
- `lat`/`lng`: finite numbers inside the bounds of the configured city
- Optional fields (`locationName`, `summary`, `image`, `sources`) are non-empty strings or well-formed objects when present; `image.url` and `sources.*` must be `http(s)` URLs; an `image` requires `url`, a `sources` requires at least one link
- Unknown fields are rejected
- All problems are collected and reported together in one error

## Dates
- Precision is implied by which fields are present: year only, year + month, or full date
- A span is expressed with `endYear` and has year precision only: an event with `endYear` cannot also have `month` or `day`
- Dates before 1582 are recorded as given in the source; there is no calendar conversion
- When an early date is stored per calendar model (proleptic Gregorian and proleptic Julian), the pipeline uses the proleptic Gregorian value, so the year matches the BCE year commonly used in sources (user decision D2, Milestone 5)

## Filtering
- The user filters by a start year and an end year (inputs accept negative years for BCE)
- An event matches if its span `[start, end]` overlaps the selected range; a year-only event covers the whole year
- Events outside the range are hidden from the map; only one event's details are shown at a time
- A reset control clears the range, and an empty state is shown when no event matches
- There is no category filter in the MVP

## Data content
- `description` is the Wikipedia intro extract for pipeline events (user decision, Milestone 5); the AI summary (ADR-008) goes in the separate `summary` field. Hand-written events keep short descriptions written for this project
- A historical event is something that happened at an identifiable place and time in or around Xi'an (battle, treaty, founding, construction, uprising, discovery). Generic buildings and ongoing institutions are excluded unless tied to a dated event. Births are excluded, except the birth of a historical figure, which is dated by their birth (user decision, Milestone 5)
- Missing data stays missing; the pipeline never guesses dates, coordinates or images
- A marker needs trustworthy coordinates of the event itself or a specific site; a city- or region-level centroid is rejected, except for an event that belongs to the city as a whole (e.g. the Tang dynasty, whose capital was Xi'an), which uses the city center from `src/config/city.ts` (user decision, Milestone 5)
- AI summaries only restate the supplied source text, are reviewed on a sample, and always appear next to a source link
- Images are shown only with attribution, as remote thumbnails; a missing or failed image falls back to no image
- Do not over-invest in accuracy for the MVP; flag uncertain items for review instead
- Events at the same site get slightly offset coordinates so markers do not stack; other marker overlap is accepted for the MVP
