import { describe, expect, it } from 'vitest'
import { events } from '../data/events'
import { formatEventDate } from './formatEventDate'

describe('formatEventDate', () => {
  it('formats a CE year with no extra suffix', () => {
    expect(formatEventDate({ year: 1949 })).toBe('1949')
  })

  it('formats a BCE year with a BCE suffix', () => {
    expect(formatEventDate({ year: -350 })).toBe('350 BCE')
  })

  it('formats year 1 BCE without producing a year zero', () => {
    expect(formatEventDate({ year: -1 })).toBe('1 BCE')
    expect(formatEventDate({ year: 1 })).toBe('1')
  })

  it('formats year and month precision', () => {
    expect(formatEventDate({ year: 618, month: 6 })).toBe('June 618')
    expect(formatEventDate({ year: -221, month: 6 })).toBe('June 221 BCE')
  })

  it('formats a full date as day, month name and year', () => {
    expect(formatEventDate({ year: 618, month: 6, day: 18 })).toBe(
      '18 June 618',
    )
    expect(formatEventDate({ year: -246, month: 1, day: 1 })).toBe(
      '1 January 246 BCE',
    )
  })

  it('formats a BCE span with a shared BCE suffix', () => {
    expect(formatEventDate({ year: -4700, endYear: -3600 })).toBe(
      '4700 – 3600 BCE',
    )
  })

  it('formats a CE span without suffixes', () => {
    expect(formatEventDate({ year: 1936, endYear: 1945 })).toBe('1936 – 1945')
  })

  it('formats an era-crossing span endpoint by endpoint', () => {
    expect(formatEventDate({ year: -10, endYear: 5 })).toBe('10 BCE – 5')
  })

  it('formats real events from the dataset', () => {
    const span = events.find((e) => e.id === 'qin-shi-huang-mausoleum-built')
    const fullDate = events.find((e) => e.id === 'tang-dynasty-founded')
    expect(span && formatEventDate(span)).toBe('246 – 208 BCE')
    expect(fullDate && formatEventDate(fullDate)).toBe('18 June 618')
  })
})
