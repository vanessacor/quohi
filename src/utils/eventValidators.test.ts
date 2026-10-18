import { describe, expect, it } from 'vitest'
import type { Bounds } from '../types/map'
import {
  findUnknownFields,
  isNonEmptyString,
  readCoordinates,
  readDate,
  readId,
  readImage,
  readOptionalText,
  readSources,
  readText,
} from './eventValidators'

const bounds: Bounds = { south: 34, west: 108, north: 35, east: 109 }

describe('isNonEmptyString', () => {
  it('accepts text and rejects blank or non-strings', () => {
    expect(isNonEmptyString('a')).toBe(true)
    expect(isNonEmptyString('')).toBe(false)
    expect(isNonEmptyString('  ')).toBe(false)
    expect(isNonEmptyString(5)).toBe(false)
  })
})

describe('findUnknownFields', () => {
  it('reports only fields outside the schema', () => {
    const problems: string[] = []
    findUnknownFields({ id: 'a', year: 1, category: 'war' }, problems)
    expect(problems).toEqual(['unknown field "category"'])
  })
})

describe('readId', () => {
  it('returns a valid, unseen id', () => {
    const problems: string[] = []
    expect(readId('bell-tower', new Set(), problems)).toBe('bell-tower')
    expect(problems).toEqual([])
  })

  it('returns a Wikidata QID id', () => {
    const problems: string[] = []
    expect(readId('Q1936', new Set(), problems)).toBe('Q1936')
    expect(readId('Q1', new Set(), problems)).toBe('Q1')
    expect(problems).toEqual([])
  })

  it('rejects missing, non-kebab-case and duplicate ids', () => {
    const seen = new Set<string>()
    const problems: string[] = []
    expect(readId(undefined, seen, problems)).toBeUndefined()
    expect(readId('Bell Tower', seen, problems)).toBeUndefined()
    readId('bell-tower', seen, problems)
    expect(readId('bell-tower', seen, problems)).toBeUndefined()
    expect(problems).toEqual([
      'id must be a non-empty string',
      'id "Bell Tower" must be kebab-case or a Wikidata QID',
      'duplicate id "bell-tower"',
    ])
  })

  it('rejects ids that are neither kebab-case nor a QID, including duplicates', () => {
    const seen = new Set<string>()
    const problems: string[] = []
    expect(readId('Q', seen, problems)).toBeUndefined()
    expect(readId('Q12a', seen, problems)).toBeUndefined()
    expect(readId('Q-123', seen, problems)).toBeUndefined()
    readId('Q1936', seen, problems)
    expect(readId('Q1936', seen, problems)).toBeUndefined()
    expect(problems).toEqual([
      'id "Q" must be kebab-case or a Wikidata QID',
      'id "Q12a" must be kebab-case or a Wikidata QID',
      'id "Q-123" must be kebab-case or a Wikidata QID',
      'duplicate id "Q1936"',
    ])
  })
})

describe('readText', () => {
  it('returns the text, or reports the field name', () => {
    const problems: string[] = []
    expect(readText('title', 'Hello', problems)).toBe('Hello')
    expect(readText('title', ' ', problems)).toBeUndefined()
    expect(problems).toEqual(['title must be a non-empty string'])
  })
})

describe('readOptionalText', () => {
  it('stays absent when the field is missing', () => {
    const problems: string[] = []
    expect(readOptionalText('summary', undefined, problems)).toBeUndefined()
    expect(problems).toEqual([])
  })

  it('returns present text and reports empty or non-string values', () => {
    const problems: string[] = []
    expect(readOptionalText('summary', 'Text', problems)).toBe('Text')
    expect(readOptionalText('summary', '  ', problems)).toBeUndefined()
    expect(readOptionalText('summary', 5, problems)).toBeUndefined()
    expect(readOptionalText('summary', null, problems)).toBeUndefined()
    expect(problems).toEqual([
      'summary must be a non-empty string',
      'summary must be a non-empty string',
      'summary must be a non-empty string',
    ])
  })
})

describe('readImage', () => {
  it('stays absent when the field is missing', () => {
    const problems: string[] = []
    expect(readImage(undefined, problems)).toBeUndefined()
    expect(problems).toEqual([])
  })

  it('returns a valid image, with and without the optional fields', () => {
    const problems: string[] = []
    expect(
      readImage({ url: 'https://upload.wikimedia.org/a.jpg' }, problems),
    ).toEqual({ url: 'https://upload.wikimedia.org/a.jpg' })
    expect(
      readImage(
        {
          url: 'http://example.org/pagoda.png',
          license: 'CC BY-SA 3.0',
          attribution: 'Author',
        },
        problems,
      ),
    ).toEqual({
      url: 'http://example.org/pagoda.png',
      license: 'CC BY-SA 3.0',
      attribution: 'Author',
    })
    expect(problems).toEqual([])
  })

  it('trims whitespace around the url', () => {
    const problems: string[] = []
    expect(
      readImage({ url: '  https://example.org/a.jpg  ' }, problems),
    ).toEqual({ url: 'https://example.org/a.jpg' })
    expect(problems).toEqual([])
  })

  it('requires an http(s) url', () => {
    const problems: string[] = []
    expect(readImage({}, problems)).toBeUndefined()
    expect(
      readImage({ url: 'ftp://example.org/a.jpg' }, problems),
    ).toBeUndefined()
    expect(readImage({ url: 'example.org/a.jpg' }, problems)).toBeUndefined()
    expect(readImage({ url: 'https://' }, problems)).toBeUndefined()
    expect(problems).toEqual([
      'image.url must be an http(s) URL',
      'image.url must be an http(s) URL',
      'image.url must be an http(s) URL',
      'image.url must be an http(s) URL',
    ])
  })

  it('rejects a non-object image and unknown fields inside it', () => {
    const problems: string[] = []
    expect(readImage('https://example.org/a.jpg', problems)).toBeUndefined()
    expect(
      readImage({ url: 'https://example.org/a.jpg', author: 'Me' }, problems),
    ).toBeUndefined()
    expect(problems).toEqual([
      'image must be an object',
      'unknown field "author" inside image',
    ])
  })

  it('reports empty or non-string license and attribution values', () => {
    const problems: string[] = []
    expect(
      readImage(
        { url: 'https://example.org/a.jpg', license: '', attribution: 7 },
        problems,
      ),
    ).toBeUndefined()
    expect(problems).toEqual([
      'image.license must be a non-empty string',
      'image.attribution must be a non-empty string',
    ])
  })
})

describe('readSources', () => {
  it('stays absent when the field is missing', () => {
    const problems: string[] = []
    expect(readSources(undefined, problems)).toBeUndefined()
    expect(problems).toEqual([])
  })

  it('returns the links that are present', () => {
    const problems: string[] = []
    expect(
      readSources(
        {
          wikipedia: 'https://en.wikipedia.org/wiki/Xi%27an_Incident',
          wikidata: 'https://www.wikidata.org/wiki/Q130696',
        },
        problems,
      ),
    ).toEqual({
      wikipedia: 'https://en.wikipedia.org/wiki/Xi%27an_Incident',
      wikidata: 'https://www.wikidata.org/wiki/Q130696',
    })
    expect(
      readSources({ wikidata: 'https://www.wikidata.org/wiki/Q1' }, problems),
    ).toEqual({ wikidata: 'https://www.wikidata.org/wiki/Q1' })
    expect(problems).toEqual([])
  })

  it('rejects an empty sources object', () => {
    const problems: string[] = []
    expect(readSources({}, problems)).toBeUndefined()
    expect(problems).toEqual(['sources must include "wikipedia" or "wikidata"'])
  })

  it('rejects a non-object sources value', () => {
    const problems: string[] = []
    expect(readSources('https://example.org', problems)).toBeUndefined()
    expect(readSources(null, problems)).toBeUndefined()
    expect(problems).toEqual([
      'sources must be an object',
      'sources must be an object',
    ])
  })

  it('rejects unknown fields and non-http(s) links inside sources', () => {
    const problems: string[] = []
    expect(
      readSources(
        { wiki: 'https://example.org', wikidata: 'www.wikidata.org/wiki/Q1' },
        problems,
      ),
    ).toBeUndefined()
    expect(problems).toEqual([
      'unknown field "wiki" inside sources',
      'sources.wikidata must be an http(s) URL',
    ])
  })
})

describe('readDate', () => {
  it('returns only the fields that are present', () => {
    const problems: string[] = []
    expect(readDate({ year: -246, endYear: -208 }, problems)).toEqual({
      year: -246,
      endYear: -208,
    })
    expect(readDate({ year: 1936, month: 12, day: 12 }, problems)).toEqual({
      year: 1936,
      month: 12,
      day: 12,
    })
    expect(problems).toEqual([])
  })

  it('returns undefined when year is invalid but still checks the other fields', () => {
    const problems: string[] = []
    expect(readDate({ year: 0, month: 13 }, problems)).toBeUndefined()
    expect(problems).toEqual([
      'year must not be 0',
      'month must be an integer 1-12',
    ])
  })

  it('rejects endYear combined with month or day, and unsafe integers', () => {
    const problems: string[] = []
    readDate({ year: 10, endYear: 20, month: 3 }, problems)
    readDate({ year: 10, endYear: 20, month: 3, day: 4 }, problems)
    readDate({ year: 2 ** 53 }, problems)
    expect(problems).toEqual([
      'endYear cannot be combined with month or day',
      'endYear cannot be combined with month or day',
      'year must be a safe integer',
    ])
  })

  it('validates endYear, day without month, and day length', () => {
    const problems: string[] = []
    readDate({ year: 10, endYear: 5 }, problems)
    readDate({ year: 10, day: 3 }, problems)
    readDate({ year: 10, month: 2, day: 30 }, problems)
    expect(problems).toEqual([
      'endYear must be >= year',
      'day requires month',
      'day must be an integer 1-29 for month 2',
    ])
  })
})

describe('readCoordinates', () => {
  it('returns lat and lng inside the bounds', () => {
    const problems: string[] = []
    expect(
      readCoordinates({ lat: 34.5, lng: 108.5 }, bounds, problems),
    ).toEqual({ lat: 34.5, lng: 108.5 })
    expect(problems).toEqual([])
  })

  it('reports each invalid coordinate', () => {
    const problems: string[] = []
    expect(
      readCoordinates({ lat: 40, lng: 'x' }, bounds, problems),
    ).toBeUndefined()
    expect(problems).toEqual([
      'lat 40 is outside bounds (34 to 35)',
      'lng must be a finite number',
    ])
  })
})
