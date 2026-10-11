import type { HistoricalEvent } from '../types/event'
import type { Bounds } from '../types/map'
import {
  findUnknownFields,
  isNonEmptyString,
  readCoordinates,
  readDate,
  readId,
  readText,
} from './eventValidators'

export const MAX_EVENTS = 20

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function readEvent(
  raw: unknown,
  index: number,
  seenIds: Set<string>,
  bounds: Bounds,
  errors: string[],
): HistoricalEvent | undefined {
  if (!isRecord(raw)) {
    errors.push(`events[${index}]: must be an object`)
    return undefined
  }

  const problems: string[] = []
  findUnknownFields(raw, problems)
  const id = readId(raw.id, seenIds, problems)
  const title = readText('title', raw.title, problems)
  const description = readText('description', raw.description, problems)
  const date = readDate(raw, problems)
  const coordinates = readCoordinates(raw, bounds, problems)

  if (
    problems.length > 0 ||
    !id ||
    !title ||
    !description ||
    !date ||
    !coordinates
  ) {
    const label = isNonEmptyString(raw.id)
      ? `events[${index}] (${raw.id})`
      : `events[${index}]`
    for (const problem of problems) errors.push(`${label}: ${problem}`)
    return undefined
  }

  return { id, title, ...date, ...coordinates, description }
}

/**
 * Validates raw event data against the rules in docs/business-rules.md.
 * Throws one error listing every problem found.
 */
export function parseEvents(
  data: unknown,
  bounds: Bounds,
): readonly HistoricalEvent[] {
  if (!Array.isArray(data)) {
    throw new Error('Invalid events data: events must be an array')
  }

  const errors: string[] = []
  if (data.length < 1) errors.push('events must contain at least 1 event')
  if (data.length > MAX_EVENTS) {
    errors.push(`events must contain at most ${MAX_EVENTS} events`)
  }

  const seenIds = new Set<string>()
  const events: HistoricalEvent[] = []
  data.forEach((raw: unknown, index) => {
    const event = readEvent(raw, index, seenIds, bounds, errors)
    if (event) events.push(event)
  })

  if (errors.length > 0) {
    throw new Error(`Invalid events data:\n- ${errors.join('\n- ')}`)
  }
  return events
}
