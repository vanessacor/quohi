# ADR-002: Flexible year/month/day date schema

- Status: Accepted
- Date: 2026-10-11
- Supersedes: TRD.md section 4 (`date: "YYYY-MM-DD"`)

## Context
Historical events worldwide span thousands of years, including BCE. ISO date strings cannot represent BCE or year-only precision cleanly. Modern events need month/day precision.

## Decision
Events use an integer `year` (negative = BCE, no year 0) with optional `month` and `day`, plus optional `endYear` for spans. Precision is implied by which fields are present.

Filtering uses range overlap: an event matches if its span overlaps the selected year range; year-only events cover the whole year. The filter UI takes two year number inputs.

## Consequences
- Handles ancient and modern events in one schema, in line with the "unified event schema" principle in `product-vision.md`
- Needs custom date formatting and comparison utils (unit tested)
- Future AI-generated data must conform to this schema
