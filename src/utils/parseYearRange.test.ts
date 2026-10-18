import { describe, expect, it } from 'vitest'
import { parseYearRange } from './parseYearRange'

const OPEN = { start: null, end: null }

describe('parseYearRange', () => {
  it('treats both empty fields as an open range', () => {
    expect(parseYearRange('', '')).toEqual({ range: OPEN, error: null })
  })

  it('treats whitespace-only fields as empty', () => {
    expect(parseYearRange('  ', '\t')).toEqual({ range: OPEN, error: null })
  })

  it('accepts a start with no end, and an end with no start', () => {
    expect(parseYearRange('1700', '')).toEqual({
      range: { start: 1700, end: null },
      error: null,
    })
    expect(parseYearRange('', '1750')).toEqual({
      range: { start: null, end: 1750 },
      error: null,
    })
  })

  it('accepts a CE range and trims whitespace', () => {
    expect(parseYearRange(' 1700 ', '1750 ')).toEqual({
      range: { start: 1700, end: 1750 },
      error: null,
    })
  })

  it('accepts negative years for BCE', () => {
    expect(parseYearRange('-221', '-206')).toEqual({
      range: { start: -221, end: -206 },
      error: null,
    })
  })

  it('accepts a range from BCE to CE', () => {
    expect(parseYearRange('-10', '10')).toEqual({
      range: { start: -10, end: 10 },
      error: null,
    })
  })

  it('accepts start equal to end', () => {
    expect(parseYearRange('618', '618')).toEqual({
      range: { start: 618, end: 618 },
      error: null,
    })
  })

  it.each(['abc', '1.5', '1e3', '12a', '+5', '--5', '5-', '0x10'])(
    'rejects %j as not a whole number',
    (text) => {
      const start = parseYearRange(text, '')
      expect(start.range).toEqual(OPEN)
      expect(start.error).toMatch(/^Start year must be a whole number/)
      const end = parseYearRange('', text)
      expect(end.range).toEqual(OPEN)
      expect(end.error).toMatch(/^End year must be a whole number/)
    },
  )

  it('rejects a lone minus sign while the user is still typing', () => {
    const result = parseYearRange('-', '')
    expect(result.range).toEqual(OPEN)
    expect(result.error).not.toBeNull()
  })

  it.each(['0', '-0', '00'])(
    'rejects %j because there is no year 0',
    (text) => {
      const result = parseYearRange(text, '')
      expect(result.range).toEqual(OPEN)
      expect(result.error).toMatch(/cannot be 0/)
    },
  )

  it('rejects a start after the end and falls back to an open range', () => {
    const result = parseYearRange('1750', '1700')
    expect(result.range).toEqual(OPEN)
    expect(result.error).toMatch(/not be after/)
  })

  it('compares BCE years numerically when checking order', () => {
    expect(parseYearRange('-200', '-300').error).not.toBeNull()
    expect(parseYearRange('-300', '-200').error).toBeNull()
  })

  it('reports the start error first when both fields are invalid', () => {
    expect(parseYearRange('x', 'y').error).toMatch(/^Start/)
  })
})
