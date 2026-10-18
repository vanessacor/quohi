import { describe, expect, it } from 'vitest'
import {
  eventOverlapsRange,
  filterEventsByRange,
  type YearRange,
} from './filterEvents'

const range = (start: number | null, end: number | null): YearRange => ({
  start,
  end,
})

describe('eventOverlapsRange', () => {
  it('matches a year-only event inside the range', () => {
    expect(eventOverlapsRange({ year: 1714 }, range(1700, 1750))).toBe(true)
  })

  it('does not match a year-only event outside the range', () => {
    expect(eventOverlapsRange({ year: 1650 }, range(1700, 1750))).toBe(false)
    expect(eventOverlapsRange({ year: 1800 }, range(1700, 1750))).toBe(false)
  })

  it('includes both boundary years', () => {
    expect(eventOverlapsRange({ year: 1700 }, range(1700, 1750))).toBe(true)
    expect(eventOverlapsRange({ year: 1750 }, range(1700, 1750))).toBe(true)
  })

  it('treats a missing bound as open-ended', () => {
    expect(eventOverlapsRange({ year: 1900 }, range(1700, null))).toBe(true)
    expect(eventOverlapsRange({ year: 1600 }, range(1700, null))).toBe(false)
    expect(eventOverlapsRange({ year: 1600 }, range(null, 1700))).toBe(true)
    expect(eventOverlapsRange({ year: 1800 }, range(null, 1700))).toBe(false)
  })

  it('matches everything when both bounds are open', () => {
    expect(eventOverlapsRange({ year: -4000 }, range(null, null))).toBe(true)
    expect(eventOverlapsRange({ year: 2000 }, range(null, null))).toBe(true)
  })

  it('matches a start-equals-end range only for that year', () => {
    expect(eventOverlapsRange({ year: 618 }, range(618, 618))).toBe(true)
    expect(eventOverlapsRange({ year: 619 }, range(618, 618))).toBe(false)
  })

  it('matches a month/day event by its year', () => {
    const event = { year: 618, month: 6, day: 18 }
    expect(eventOverlapsRange(event, range(618, 618))).toBe(true)
    expect(eventOverlapsRange(event, range(619, 700))).toBe(false)
  })

  it('matches a span that partly overlaps the range', () => {
    const span = { year: 1690, endYear: 1710 }
    expect(eventOverlapsRange(span, range(1700, 1750))).toBe(true)
    expect(eventOverlapsRange(span, range(1650, 1695))).toBe(true)
  })

  it('matches a span fully inside the range', () => {
    expect(
      eventOverlapsRange({ year: 1710, endYear: 1720 }, range(1700, 1750)),
    ).toBe(true)
  })

  it('matches a span that contains the whole range', () => {
    expect(
      eventOverlapsRange({ year: 1600, endYear: 1800 }, range(1700, 1750)),
    ).toBe(true)
  })

  it('matches a span that only touches the range at a boundary year', () => {
    const span = { year: 1690, endYear: 1700 }
    expect(eventOverlapsRange(span, range(1700, 1750))).toBe(true)
  })

  it('does not match a span entirely outside the range', () => {
    const span = { year: 1600, endYear: 1650 }
    expect(eventOverlapsRange(span, range(1700, 1750))).toBe(false)
    expect(eventOverlapsRange(span, range(1500, 1599))).toBe(false)
  })

  it('compares BCE years as negative integers', () => {
    expect(eventOverlapsRange({ year: -221 }, range(-300, -200))).toBe(true)
    expect(eventOverlapsRange({ year: -350 }, range(-300, -200))).toBe(false)
    expect(
      eventOverlapsRange({ year: -4700, endYear: -3600 }, range(-4000, -3000)),
    ).toBe(true)
  })

  it('handles ranges and spans that cross from BCE to CE', () => {
    expect(eventOverlapsRange({ year: -1 }, range(-5, 5))).toBe(true)
    expect(eventOverlapsRange({ year: 1 }, range(-5, 5))).toBe(true)
    expect(eventOverlapsRange({ year: 6 }, range(-5, 5))).toBe(false)
    expect(eventOverlapsRange({ year: -10, endYear: 5 }, range(1, 100))).toBe(
      true,
    )
  })

  it('treats 1 BCE and 1 CE as adjacent years', () => {
    expect(eventOverlapsRange({ year: -1 }, range(1, 10))).toBe(false)
    expect(eventOverlapsRange({ year: 1 }, range(-10, -1))).toBe(false)
  })
})

describe('filterEventsByRange', () => {
  it('returns every event for an open range', () => {
    const sample = [{ year: -300 }, { year: 5 }, { year: 900, endYear: 950 }]
    expect(filterEventsByRange(sample, range(null, null))).toEqual(sample)
  })

  it('returns only overlapping events, keeping their order', () => {
    const sample = [
      { id: 'a', year: 100 },
      { id: 'b', year: 200 },
      { id: 'c', year: 150, endYear: 250 },
      { id: 'd', year: 300 },
    ]
    expect(
      filterEventsByRange(sample, range(200, 260)).map((e) => e.id),
    ).toEqual(['b', 'c'])
  })

  it('returns an empty array when nothing matches', () => {
    expect(filterEventsByRange([{ year: 1 }], range(100000, null))).toEqual([])
  })

  it('returns a new array and leaves the input untouched', () => {
    const sample = [{ year: 1 }, { year: 2 }]
    const result = filterEventsByRange(sample, range(null, null))
    expect(result).not.toBe(sample)
    expect(sample).toHaveLength(2)
  })

  it('returns nothing for an inverted range (the parser rejects these)', () => {
    expect(filterEventsByRange([{ year: 5 }], range(10, 1))).toEqual([])
  })
})
