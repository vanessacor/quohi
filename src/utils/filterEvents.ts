import type { HistoricalEvent } from '../types/event'

/** A `null` bound is open-ended. Years are signed integers (negative = BCE). */
export interface YearRange {
  readonly start: number | null
  readonly end: number | null
}

type SpanFields = Pick<HistoricalEvent, 'year' | 'endYear'>

/**
 * True when the event's span overlaps the range (docs/business-rules.md
 * "Filtering"). Month and day are ignored: an event covers its whole year,
 * and a span covers `year` to `endYear`. Year 0 does not exist, so plain
 * integer comparison is correct across BCE and CE.
 */
export function eventOverlapsRange(
  event: SpanFields,
  range: YearRange,
): boolean {
  const eventStart = event.year
  const eventEnd = event.endYear ?? event.year
  const afterStart = range.start === null || eventEnd >= range.start
  const beforeEnd = range.end === null || eventStart <= range.end
  return afterStart && beforeEnd
}

export function filterEventsByRange<T extends SpanFields>(
  events: readonly T[],
  range: YearRange,
): T[] {
  return events.filter((event) => eventOverlapsRange(event, range))
}
