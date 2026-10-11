import type { HistoricalEvent } from '../types/event'
import type { Bounds, LatLng } from '../types/map'

// Field-level validators for raw event data (rules: docs/business-rules.md).
// Each reader returns the validated value, or undefined after pushing a message to `problems`.

export type EventDate = Pick<
  HistoricalEvent,
  'year' | 'month' | 'day' | 'endYear'
>

const ID_PATTERN = /^[a-z0-9]+(-[a-z0-9]+)*$/
const KNOWN_FIELDS: ReadonlySet<string> = new Set([
  'id',
  'title',
  'year',
  'month',
  'day',
  'endYear',
  'lat',
  'lng',
  'description',
])
// February allows 29 in any year; there is no leap-year logic.
const DAYS_IN_MONTH: readonly number[] = [
  31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31,
]

export function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim() !== ''
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

function isYear(value: unknown): value is number {
  return Number.isSafeInteger(value) && value !== 0
}

function isIntegerInRange(
  value: unknown,
  min: number,
  max: number,
): value is number {
  return (
    typeof value === 'number' &&
    Number.isSafeInteger(value) &&
    value >= min &&
    value <= max
  )
}

function describeYear(name: string, value: unknown): string {
  if (!Number.isInteger(value)) return `${name} must be an integer`
  return Number.isSafeInteger(value)
    ? `${name} must not be 0`
    : `${name} must be a safe integer`
}

export function findUnknownFields(
  raw: Record<string, unknown>,
  problems: string[],
): void {
  for (const field of Object.keys(raw)) {
    if (!KNOWN_FIELDS.has(field)) problems.push(`unknown field "${field}"`)
  }
}

/** Reads a kebab-case id that is unique within `seenIds`; records every non-empty id it sees. */
export function readId(
  value: unknown,
  seenIds: Set<string>,
  problems: string[],
): string | undefined {
  if (!isNonEmptyString(value)) {
    problems.push('id must be a non-empty string')
    return undefined
  }
  const isDuplicate = seenIds.has(value)
  seenIds.add(value)
  if (!ID_PATTERN.test(value)) {
    problems.push(`id "${value}" must be kebab-case`)
    return undefined
  }
  if (isDuplicate) {
    problems.push(`duplicate id "${value}"`)
    return undefined
  }
  return value
}

export function readText(
  name: string,
  value: unknown,
  problems: string[],
): string | undefined {
  if (!isNonEmptyString(value)) {
    problems.push(`${name} must be a non-empty string`)
    return undefined
  }
  return value
}

function readEndYear(
  value: unknown,
  year: number | undefined,
  problems: string[],
): number | undefined {
  if (value === undefined) return undefined
  if (!isYear(value)) {
    problems.push(describeYear('endYear', value))
    return undefined
  }
  if (year && value < year) {
    problems.push('endYear must be >= year')
    return undefined
  }
  return value
}

function readMonth(value: unknown, problems: string[]): number | undefined {
  if (value === undefined) return undefined
  if (!isIntegerInRange(value, 1, 12)) {
    problems.push('month must be an integer 1-12')
    return undefined
  }
  return value
}

function readDay(
  value: unknown,
  rawMonth: unknown,
  month: number | undefined,
  problems: string[],
): number | undefined {
  if (value === undefined) return undefined
  if (rawMonth === undefined) {
    problems.push('day requires month')
    return undefined
  }
  if (!month) return undefined // the invalid month is already reported
  const max = DAYS_IN_MONTH[month - 1]
  if (!isIntegerInRange(value, 1, max)) {
    problems.push(`day must be an integer 1-${max} for month ${month}`)
    return undefined
  }
  return value
}

function checkSpanPrecision(
  raw: Record<string, unknown>,
  problems: string[],
): void {
  if (
    raw.endYear !== undefined &&
    (raw.month !== undefined || raw.day !== undefined)
  ) {
    problems.push('endYear cannot be combined with month or day')
  }
}

/** Reads year, endYear, month and day. Returns undefined when `year` is invalid. */
export function readDate(
  raw: Record<string, unknown>,
  problems: string[],
): EventDate | undefined {
  const year = isYear(raw.year) ? raw.year : undefined
  if (!year) problems.push(describeYear('year', raw.year))

  const endYear = readEndYear(raw.endYear, year, problems)
  const month = readMonth(raw.month, problems)
  const day = readDay(raw.day, raw.month, month, problems)
  checkSpanPrecision(raw, problems)

  if (!year) return undefined
  return {
    year,
    ...(month !== undefined && { month }),
    ...(day !== undefined && { day }),
    ...(endYear !== undefined && { endYear }),
  }
}

function readCoordinate(
  name: string,
  value: unknown,
  min: number,
  max: number,
  problems: string[],
): number | undefined {
  if (!isFiniteNumber(value)) {
    problems.push(`${name} must be a finite number`)
    return undefined
  }
  if (value < min || value > max) {
    problems.push(`${name} ${value} is outside bounds (${min} to ${max})`)
    return undefined
  }
  return value
}

/** Reads lat and lng, which must be finite numbers inside `bounds`. */
export function readCoordinates(
  raw: Record<string, unknown>,
  bounds: Bounds,
  problems: string[],
): LatLng | undefined {
  const lat = readCoordinate(
    'lat',
    raw.lat,
    bounds.south,
    bounds.north,
    problems,
  )
  const lng = readCoordinate('lng', raw.lng, bounds.west, bounds.east, problems)
  if (lat === undefined || lng === undefined) return undefined
  return { lat, lng }
}
