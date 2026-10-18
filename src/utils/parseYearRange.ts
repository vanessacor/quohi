import type { YearRange } from './filterEvents'

export interface ParsedYearRange {
  readonly range: YearRange
  readonly error: string | null
}

const WHOLE_NUMBER = /^-?\d+$/
const NO_FILTER: YearRange = { start: null, end: null }

type ParsedYear =
  | { readonly ok: true; readonly value: number | null }
  | { readonly ok: false; readonly error: string }

// Empty text is an open-ended bound, not an error.
function parseYear(text: string, label: string): ParsedYear {
  const trimmed = text.trim()
  if (trimmed === '') return { ok: true, value: null }
  if (!WHOLE_NUMBER.test(trimmed)) {
    return { ok: false, error: `${label} year must be a whole number.` }
  }
  const value = Number(trimmed)
  if (value === 0) {
    return {
      ok: false,
      error: `${label} year cannot be 0 (there is no year 0).`,
    }
  }
  return { ok: true, value }
}

/**
 * Turns the two filter inputs into a range (docs/business-rules.md
 * "Filtering"). On any error the range is open (show everything) and `error`
 * holds a short message for the user.
 */
export function parseYearRange(
  startText: string,
  endText: string,
): ParsedYearRange {
  const start = parseYear(startText, 'Start')
  if (!start.ok) return { range: NO_FILTER, error: start.error }
  const end = parseYear(endText, 'End')
  if (!end.ok) return { range: NO_FILTER, error: end.error }

  if (start.value !== null && end.value !== null && start.value > end.value) {
    return {
      range: NO_FILTER,
      error: 'Start year must not be after the end year.',
    }
  }
  return { range: { start: start.value, end: end.value }, error: null }
}
