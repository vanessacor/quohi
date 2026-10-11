# Business Rules

Domain rules for the Historical Events Map: what an event is, what makes data valid, and how filtering behaves. How the code is written lives in `docs/code-standards.md`; decisions and their reasons live in `docs/adr/`.

## Scope (MVP)
- One city (Xi'an, China); its name, center, zoom and bounds are defined in `src/config/city.ts`
- At most 20 events, from a static JSON file; no backend or external data sources

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
  "description": "string"
}
```
Every data source must reduce to this schema (product vision: a unified event schema). New fields require an ADR (see ADR-002).

## Validation rules
Enforced by `parseEvents` in `src/utils/`, run once when `src/data/events.ts` loads:
- Array of 1 to 20 events; each an object
- `id`: non-empty, kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`), unique
- `title` and `description`: non-empty strings
- `year`: integer, not 0; `endYear` (optional): integer, not 0, and `>= year`
- `endYear` cannot be combined with `month` or `day`
- `month`: integer 1-12; `day`: integer, requires `month`, within the month's length (February allows 29 in any year; no leap-year logic)
- `lat`/`lng`: finite numbers inside the bounds of the configured city
- Unknown fields are rejected
- All problems are collected and reported together in one error

## Dates
- Precision is implied by which fields are present: year only, year + month, or full date
- A span is expressed with `endYear` and has year precision only: an event with `endYear` cannot also have `month` or `day`
- Dates before 1582 are recorded as given in the source; there is no calendar conversion

## Filtering
- The user filters by a start year and an end year (inputs accept negative years for BCE)
- An event matches if its span `[start, end]` overlaps the selected range; a year-only event covers the whole year
- Events outside the range are hidden from the map; only one event's details are shown at a time

## Data content
- Descriptions are short summaries written for this project, not copied text
- Do not over-invest in accuracy for the MVP; flag uncertain items for review instead
- Events at the same site get slightly offset coordinates so markers do not stack; other marker overlap is accepted for the MVP
