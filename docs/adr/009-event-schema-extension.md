# ADR-009: Optional enrichment fields on the event schema

- Status: Accepted
- Date: 2026-10-18
- Amends: ADR-002 (adds fields; the date model is unchanged)

## Context
The data pipeline (ADR-007) and summaries (ADR-008) produce information the current schema cannot hold. `notes/wiki-plan.md` proposed a different schema (ISO dates, `datePrecision`, nested `coordinates`, `category`, `summaryStatus`). Replacing ADR-002 would break date formatting, filtering and validation for little gain.

## Decision
Keep `id`, `title`, `year`, `month`, `day`, `endYear`, `lat`, `lng`, `description` exactly as in ADR-002, and add these **optional** fields:

- `locationName`: string
- `summary`: string (AI-generated, ADR-008)
- `image`: `{ url: string, license?: string, attribution?: string }`
- `sources`: `{ wikipedia?: string, wikidata?: string }`

Not adopted: `startDate`/`datePrecision` (ADR-002 covers it), nested `coordinates`, `category` (category filtering is out of scope), `summaryStatus` (pipeline metadata only).

Rules:
- `id` should be the Wikidata QID for pipeline events
- Images are remote thumbnails, never embedded in JSON; an `image` is only shown when it has attribution, and a missing or failed image must not break the panel
- The UI treats every new field as optional

## Consequences
- Existing events and utils keep working unchanged
- `HistoricalEvent`, `parseEvents`, tests and `docs/business-rules.md` must be updated together
- The hand-written validator grows, which strengthens the case for the Zod backlog item
