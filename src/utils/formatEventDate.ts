import type { HistoricalEvent } from '../types/event'

type DateFields = Pick<HistoricalEvent, 'year' | 'month' | 'day' | 'endYear'>

const MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
] as const

// No Date object: dates are plain integers (docs/business-rules.md "Dates").
function formatYear(year: number): string {
  return year < 0 ? `${Math.abs(year)} BCE` : `${year}`
}

function formatSpan(year: number, endYear: number): string {
  // Same era: share the suffix ("4700 – 3600 BCE", "1936 – 1945").
  // Mixed era: format each endpoint on its own ("10 BCE – 5").
  if (year < 0 && endYear < 0) {
    return `${Math.abs(year)} – ${Math.abs(endYear)} BCE`
  }
  if (year >= 0 && endYear >= 0) {
    return `${year} – ${endYear}`
  }
  return `${formatYear(year)} – ${formatYear(endYear)}`
}

/**
 * Formats an event's date by its precision (docs/business-rules.md "Dates"):
 * year only, year + month, or full date; spans have year precision only.
 */
export function formatEventDate(event: DateFields): string {
  const { year, month, day, endYear } = event
  if (endYear !== undefined) return formatSpan(year, endYear)

  const yearText = formatYear(year)
  if (day !== undefined && month !== undefined) {
    return `${day} ${MONTHS[month - 1]} ${yearText}`
  }
  if (month !== undefined) {
    return `${MONTHS[month - 1]} ${yearText}`
  }
  return yearText
}
