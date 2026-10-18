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

function manyEvents(count: number) {
  return Array.from({ length: count }, (_, i) => ({
    ...valid,
    id: `event-${i}`,
  }))
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

  it.each([1, 3, 5, 7, 8, 10, 12])('accepts day 31 in month %i', (month) => {
    expect(parseEvents([{ ...valid, month, day: 31 }], bounds)).toHaveLength(1)
  })

  it.each([4, 6, 9, 11])('accepts day 30 in month %i', (month) => {
    expect(parseEvents([{ ...valid, month, day: 30 }], bounds)).toHaveLength(1)
  })

  it('accepts coordinates on the bounds edge', () => {
    const event = { ...valid, lat: 34, lng: 109 }
    expect(parseEvents([event], bounds)).toHaveLength(1)
  })

  it('accepts a Wikidata QID id', () => {
    const event = { ...valid, id: 'Q130696' }
    expect(parseEvents([event], bounds)).toEqual([event])
  })

  it('accepts every optional field', () => {
    const event = {
      ...valid,
      locationName: "Xi'an Incident site",
      summary: 'An AI-generated summary.',
      image: {
        url: 'https://upload.wikimedia.org/wikipedia/commons/a/Page_of_Four.jpg',
        license: 'CC BY-SA 3.0',
        attribution: 'Photographer',
      },
      sources: {
        wikipedia: 'https://en.wikipedia.org/wiki/Xi%27an_Incident',
        wikidata: 'https://www.wikidata.org/wiki/Q130696',
      },
    }
    expect(parseEvents([event], bounds)).toEqual([event])
  })

  it('accepts an event without the optional fields', () => {
    expect(parseEvents([valid], bounds)).toEqual([valid])
  })

  it('accepts exactly MAX_EVENTS events', () => {
    expect(parseEvents(manyEvents(MAX_EVENTS), bounds)).toHaveLength(MAX_EVENTS)
  })
})

describe('parseEvents: invalid structure', () => {
  it('rejects non-array input', () => {
    expect(errorOf({})).toBe('Invalid events data: events must be an array')
    expect(errorOf(null)).toBe('Invalid events data: events must be an array')
  })

  it('rejects an empty array', () => {
    expect(errorOf([])).toContain('events must contain at least 1 event')
  })

  it('rejects more than MAX_EVENTS events', () => {
    expect(errorOf(manyEvents(MAX_EVENTS + 1))).toContain(
      'events must contain at most 20 events',
    )
  })

  it('rejects items that are not objects', () => {
    expect(errorOf(['text'])).toContain('events[0]: must be an object')
    expect(errorOf([null])).toContain('events[0]: must be an object')
    expect(errorOf([[valid]])).toContain('events[0]: must be an object')
  })

  it('rejects unknown fields', () => {
    expect(errorOf([{ ...valid, category: 'war' }])).toContain(
      'events[0] (bell-tower): unknown field "category"',
    )
  })

  it('rejects unknown fields inside image and sources', () => {
    const message = errorOf([
      { ...valid, image: { url: 'https://example.org/a.jpg', author: 'Me' } },
      { ...valid, id: 'second', sources: { blog: 'https://example.org' } },
    ])
    expect(message).toContain(
      'events[0] (bell-tower): unknown field "author" inside image',
    )
    expect(message).toContain(
      'events[1] (second): unknown field "blog" inside sources',
    )
  })

  it('rejects malformed optional fields', () => {
    const message = errorOf([
      { ...valid, locationName: '' },
      { ...valid, id: 'second', summary: 5 },
      { ...valid, id: 'third', image: 'https://example.org/a.jpg' },
      { ...valid, id: 'fourth', sources: { wikidata: 'wikidata.org/Q1' } },
      { ...valid, id: 'fifth', sources: {} },
    ])
    expect(message).toContain('locationName must be a non-empty string')
    expect(message).toContain('summary must be a non-empty string')
    expect(message).toContain('image must be an object')
    expect(message).toContain('sources.wikidata must be an http(s) URL')
    expect(message).toContain('sources must include "wikipedia" or "wikidata"')
  })
})

describe('parseEvents: id, title, description', () => {
  it('rejects a missing id', () => {
    expect(errorOf([{ ...valid, id: undefined }])).toContain(
      'events[0]: id must be a non-empty string',
    )
  })

  it.each([
    'Bell Tower',
    'bell_tower',
    '-bell',
    'bell-',
    'bell--tower',
    'Q1936a',
  ])('rejects the id "%s" that is neither kebab-case nor a QID', (id) => {
    expect(errorOf([{ ...valid, id }])).toContain(
      `id "${id}" must be kebab-case or a Wikidata QID`,
    )
  })

  it('rejects duplicate ids', () => {
    expect(errorOf([valid, { ...valid }])).toContain(
      'events[1] (bell-tower): duplicate id "bell-tower"',
    )
  })

  it('rejects duplicate Wikidata QID ids', () => {
    expect(
      errorOf([
        { ...valid, id: 'Q1936' },
        { ...valid, id: 'Q1936' },
      ]),
    ).toContain('events[1] (Q1936): duplicate id "Q1936"')
  })

  it('rejects empty, blank or non-string title and description', () => {
    expect(errorOf([{ ...valid, title: '' }])).toContain(
      'title must be a non-empty string',
    )
    expect(errorOf([{ ...valid, title: '   ' }])).toContain(
      'title must be a non-empty string',
    )
    expect(errorOf([{ ...valid, description: '' }])).toContain(
      'description must be a non-empty string',
    )
    expect(errorOf([{ ...valid, description: 5 }])).toContain(
      'description must be a non-empty string',
    )
  })
})

describe('parseEvents: year and endYear', () => {
  it('rejects year 0', () => {
    expect(errorOf([{ ...valid, year: 0 }])).toContain('year must not be 0')
  })

  it.each([1384.5, '1384', null, undefined])(
    'rejects the non-integer year %j',
    (year) => {
      expect(errorOf([{ ...valid, year }])).toContain('year must be an integer')
    },
  )

  it('rejects an unsafe integer year', () => {
    expect(errorOf([{ ...valid, year: 2 ** 53 }])).toContain(
      'year must be a safe integer',
    )
  })

  it('rejects endYear before year, in both eras', () => {
    expect(errorOf([{ ...valid, endYear: 1300 }])).toContain(
      'endYear must be >= year',
    )
    expect(errorOf([{ ...valid, year: -10, endYear: -20 }])).toContain(
      'endYear must be >= year',
    )
  })

  it('rejects endYear 0 and non-integer endYear', () => {
    expect(errorOf([{ ...valid, year: -10, endYear: 0 }])).toContain(
      'endYear must not be 0',
    )
    expect(errorOf([{ ...valid, endYear: 1400.5 }])).toContain(
      'endYear must be an integer',
    )
  })

  it('rejects endYear combined with month or day', () => {
    const message = 'endYear cannot be combined with month or day'
    expect(errorOf([{ ...valid, endYear: 1400, month: 3 }])).toContain(message)
    expect(errorOf([{ ...valid, endYear: 1400, month: 3, day: 5 }])).toContain(
      message,
    )
  })
})

describe('parseEvents: month and day', () => {
  it.each([0, 13, 2.5, '3', null])('rejects the month %j', (month) => {
    expect(errorOf([{ ...valid, month }])).toContain(
      'month must be an integer 1-12',
    )
  })

  it('rejects a day without a month', () => {
    expect(errorOf([{ ...valid, day: 5 }])).toContain('day requires month')
  })

  it('reports only the month error when the month is invalid', () => {
    const message = errorOf([{ ...valid, month: 13, day: 5 }])
    expect(message).toContain('month must be an integer 1-12')
    expect(message).not.toContain('day')
  })

  it('rejects day 30 and 31 in February and day 31 in 30-day months', () => {
    expect(errorOf([{ ...valid, month: 2, day: 30 }])).toContain(
      'day must be an integer 1-29 for month 2',
    )
    expect(errorOf([{ ...valid, month: 4, day: 31 }])).toContain(
      'day must be an integer 1-30 for month 4',
    )
  })

  it.each([4, 6, 9, 11])('rejects day 31 in month %i', (month) => {
    expect(errorOf([{ ...valid, month, day: 31 }])).toContain(
      `day must be an integer 1-30 for month ${month}`,
    )
  })

  it.each([0, 32, 1.5, '5', null])('rejects the day %j', (day) => {
    expect(errorOf([{ ...valid, month: 1, day }])).toContain(
      'day must be an integer 1-31 for month 1',
    )
  })
})

describe('parseEvents: coordinates', () => {
  it.each([
    ['lat', 33.9, 'lat 33.9 is outside bounds (34 to 35)'],
    ['lat', 35.1, 'lat 35.1 is outside bounds (34 to 35)'],
    ['lng', 107.9, 'lng 107.9 is outside bounds (108 to 109)'],
    ['lng', 109.1, 'lng 109.1 is outside bounds (108 to 109)'],
  ])('rejects %s %d outside the bounds', (field, value, message) => {
    expect(errorOf([{ ...valid, [field]: value }])).toContain(message)
  })

  it.each([
    ['lat', NaN],
    ['lng', Infinity],
    ['lat', '34.5'],
    ['lng', undefined],
    ['lat', null],
  ])('rejects the non-finite %s %j', (field, value) => {
    expect(errorOf([{ ...valid, [field]: value }])).toContain(
      `${field} must be a finite number`,
    )
  })
})

describe('parseEvents: error reporting', () => {
  it('reports every problem, with the event index and id', () => {
    const message = errorOf([
      { ...valid, year: 0 },
      { ...valid, id: 'second', lat: 10, month: 13 },
    ])
    expect(message).toContain('events[0] (bell-tower): year must not be 0')
    expect(message).toContain(
      'events[1] (second): month must be an integer 1-12',
    )
    expect(message).toContain(
      'events[1] (second): lat 10 is outside bounds (34 to 35)',
    )
  })

  it('reports unknown fields together with other problems in one event', () => {
    const message = errorOf([{ ...valid, category: 'war', year: 0 }])
    expect(message).toContain('unknown field "category"')
    expect(message).toContain('year must not be 0')
  })
})
