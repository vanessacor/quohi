import { describe, expect, it } from 'vitest'
import type { HistoricalEvent } from '../types/event'
import { eventToMarker } from './eventToMarker'

const event: HistoricalEvent = {
  id: 'bell-tower',
  title: 'Bell Tower built',
  year: 1384,
  lat: 34.261,
  lng: 108.9427,
  description: 'A tower.',
}

describe('eventToMarker', () => {
  it('maps id, title and coordinates to a map marker', () => {
    expect(eventToMarker(event)).toEqual({
      id: 'bell-tower',
      title: 'Bell Tower built',
      position: { lat: 34.261, lng: 108.9427 },
    })
  })

  it('does not carry event-only fields into the marker', () => {
    const marker = eventToMarker({ ...event, month: 3, endYear: 1400 })
    expect(Object.keys(marker).sort()).toEqual(['id', 'position', 'title'])
  })
})
