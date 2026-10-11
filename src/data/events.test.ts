import { describe, expect, it } from 'vitest'
import { events } from './events'

describe('events dataset', () => {
  it('loads and passes validation', () => {
    expect(events.length).toBeGreaterThanOrEqual(10)
    expect(events.length).toBeLessThanOrEqual(20)
  })

  it('has no two events at identical coordinates', () => {
    const positions = events.map((event) => `${event.lat},${event.lng}`)
    expect(new Set(positions).size).toBe(events.length)
  })
})
