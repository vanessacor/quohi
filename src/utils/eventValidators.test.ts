import { describe, expect, it } from 'vitest'
import type { Bounds } from '../types/map'
import {
  findUnknownFields,
  isNonEmptyString,
  readCoordinates,
  readDate,
  readId,
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

  it('rejects missing, non-kebab-case and duplicate ids', () => {
    const seen = new Set<string>()
    const problems: string[] = []
    expect(readId(undefined, seen, problems)).toBeUndefined()
    expect(readId('Bell Tower', seen, problems)).toBeUndefined()
    readId('bell-tower', seen, problems)
    expect(readId('bell-tower', seen, problems)).toBeUndefined()
    expect(problems).toEqual([
      'id must be a non-empty string',
      'id "Bell Tower" must be kebab-case',
      'duplicate id "bell-tower"',
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
