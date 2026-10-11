import type { HistoricalEvent } from '../types/event'
import type { MapMarker } from '../types/map'

export function eventToMarker(event: HistoricalEvent): MapMarker {
  return {
    id: event.id,
    title: event.title,
    position: { lat: event.lat, lng: event.lng },
  }
}
