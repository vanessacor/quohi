import { describe, expect, it } from 'vitest'
import type { Bounds } from '../types/map'
import { MAX_EVENTS, parseEvents } from './parseEvents'

const bounds: Bounds = { south: 34, west: 108, north: 35, east: 109 }

const valid = {
  id: 'bell-tower',
  title: 'Bell Tower built',
  year: 1384,
  lat: 34.5,
  lng: 108.5,
  description: 'A tower.',
}

function errorOf(data: unknown): string {
  try {
    parseEvents(data, bounds)
  } catch (error) {
    return error instanceof Error ? error.message : String(error)
  }
  throw new Error('expected parseEvents to throw')
}

describe('parseEvents: valid input', () => {
  it('accepts an event with only a year', () => {
    expect(parseEvents([valid], bounds)).toEqual([valid])
  })

  it('accepts year and month', () => {
    const event = { ...valid, month: 3 }
    expect(parseEvents([event], bounds)).toEqual([event])
  })

  it('accepts a full date', () => {
    const event = { ...valid, month: 12, day: 12 }
    expect(parseEvents([event], bounds)).toEqual([event])
  })

  it('accepts an endYear span, including equal years', () => {
    expect(parseEvents([{ ...valid, endYear: 1400 }], bounds)).toHaveLength(1)
    expect(parseEvents([{ ...valid, endYear: 1384 }], bounds)).toHaveLength(1)
  })

  it('accepts BCE years and spans', () => {
    const event = { ...valid, year: -246, endYear: -208 }
    expect(parseEvents([event], bounds)).toEqual([event])
  })

  it('accepts February 29 in any year', () => {
    expect(parseEvents([{ ...valid, month: 2, day: 29 }], bounds)).toHaveLength(
      1,
    )
  })

  it('accepts coordinates on the bounds edge', () => {
    const event = { ...valid, lat: 34, lng: 109 }
    expect(parseEvents([event], bounds)).toHaveLength(1)
  })

  it('accepts exactly MAX_EVENTS events', () => {
    const events = Array.from({ length: MAX_EVENTS }, (_, i) => ({
      ...valid,
      id: `event-${i}`,
    }))
    expect(parseEvents(events, bounds)).toHaveLength(MAX_EVENTS)
  })
})

describe('parseEvents: invalid structure', () => {
  it('rejects non-array input', () => {
    expect(errorOf({})).toMatch(/array/)
    expect(errorOf(null)).toMatch(/array/)
  })

  it('rejects an empty array', () => {
    expect(errorOf([])).toMatch(/at least 1/)
  })

  it('rejects more than MAX_EVENTS events', () => {
    const events = Array.from({ length: MAX_EVENTS + 1 }, (_, i) => ({
      ...valid,
      id: `event-${i}`,
    }))
    expect(errorOf(events)).toMatch(/at most 20/)
  })

  it('rejects items that are not objects', () => {
    expect(errorOf(['text'])).toMatch(/events\[0\].*object/)
    expect(errorOf([null])).toMatch(/events\[0\].*object/)
  })

  it('rejects unknown fields', () => {
    expect(errorOf([{ ...valid, category: 'war' }])).toMatch(
      /unknown field "category"/,
    )
  })
})

describe('parseEvents: id, title, description', () => {
  it('rejects a missing or non-kebab-case id', () => {
    expect(errorOf([{ ...valid, id: undefined }])).toMatch(/id/)
    expect(errorOf([{ ...valid, id: 'Bell Tower' }])).toMatch(/kebab-case/)
    expect(errorOf([{ ...valid, id: 'bell_tower' }])).toMatch(/kebab-case/)
    expect(errorOf([{ ...valid, id: '-bell' }])).toMatch(/kebab-case/)
  })

  it('rejects duplicate ids', () => {
    expect(errorOf([valid, { ...valid }])).toMatch(/duplicate id "bell-tower"/)
  })

  it('rejects empty or blank title and description', () => {
    expect(errorOf([{ ...valid, title: '' }])).toMatch(/title/)
    expect(errorOf([{ ...valid, title: '   ' }])).toMatch(/title/)
    expect(errorOf([{ ...valid, description: '' }])).toMatch(/description/)
    expect(errorOf([{ ...valid, description: 5 }])).toMatch(/description/)
  })
})

describe('parseEvents: dates', () => {
  it('rejects year 0 and non-integer years', () => {
    expect(errorOf([{ ...valid, year: 0 }])).toMatch(/year.*0/)
    expect(errorOf([{ ...valid, year: 1384.5 }])).toMatch(/year.*integer/)
    expect(errorOf([{ ...valid, year: 2 ** 53 }])).toMatch(/year.*integer/)
    expect(errorOf([{ ...valid, year: '1384' }])).toMatch(/year.*integer/)
    expect(errorOf([{ ...valid, year: undefined }])).toMatch(/year/)
  })

  it('rejects endYear before year, endYear 0 and non-integer endYear', () => {
    expect(errorOf([{ ...valid, endYear: 1300 }])).toMatch(/endYear.*>=/)
    expect(errorOf([{ ...valid, year: -10, endYear: -20 }])).toMatch(
      /endYear.*>=/,
    )
    expect(errorOf([{ ...valid, year: -10, endYear: 0 }])).toMatch(/endYear/)
    expect(errorOf([{ ...valid, endYear: 1400.5 }])).toMatch(/endYear/)
  })

  it('rejects months outside 1-12 and non-integer months', () => {
    expect(errorOf([{ ...valid, month: 0 }])).toMatch(/month/)
    expect(errorOf([{ ...valid, month: 13 }])).toMatch(/month/)
    expect(errorOf([{ ...valid, month: 2.5 }])).toMatch(/month/)
  })

  it('rejects a day without a month', () => {
    expect(errorOf([{ ...valid, day: 5 }])).toMatch(/day.*requires month/)
  })

  it('rejects days beyond the length of the month', () => {
    expect(errorOf([{ ...valid, month: 2, day: 30 }])).toMatch(/day/)
    expect(errorOf([{ ...valid, month: 4, day: 31 }])).toMatch(/day/)
    expect(errorOf([{ ...valid, month: 1, day: 0 }])).toMatch(/day/)
    expect(errorOf([{ ...valid, month: 1, day: 1.5 }])).toMatch(/day/)
  })
})

describe('parseEvents: coordinates', () => {
  it('rejects coordinates outside the bounds', () => {
    expect(errorOf([{ ...valid, lat: 33.9 }])).toMatch(/lat.*bounds/)
    expect(errorOf([{ ...valid, lat: 35.1 }])).toMatch(/lat.*bounds/)
    expect(errorOf([{ ...valid, lng: 107.9 }])).toMatch(/lng.*bounds/)
    expect(errorOf([{ ...valid, lng: 109.1 }])).toMatch(/lng.*bounds/)
  })

  it('rejects non-finite or non-number coordinates', () => {
    expect(errorOf([{ ...valid, lat: NaN }])).toMatch(/lat/)
    expect(errorOf([{ ...valid, lng: Infinity }])).toMatch(/lng/)
    expect(errorOf([{ ...valid, lat: '34.5' }])).toMatch(/lat/)
    expect(errorOf([{ ...valid, lng: undefined }])).toMatch(/lng/)
  })
})

describe('parseEvents: error reporting', () => {
  it('reports every problem, with the event index and id', () => {
    const message = errorOf([
      { ...valid, year: 0 },
      { ...valid, id: 'second', lat: 10, month: 13 },
    ])
    expect(message).toMatch(/events\[0\] \(bell-tower\).*year/)
    expect(message).toMatch(/events\[1\] \(second\).*lat/)
    expect(message).toMatch(/events\[1\] \(second\).*month/)
  })
})
