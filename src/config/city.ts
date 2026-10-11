import type { Bounds, LatLng } from '../types/map'

export interface CityConfig {
  readonly name: string
  readonly center: LatLng
  readonly zoom: number
  readonly bounds: Bounds
}

export const city: CityConfig = {
  name: "Xi'an, China",
  center: { lat: 34.3416, lng: 108.9398 },
  zoom: 11,
  bounds: { south: 34.05, west: 108.6, north: 34.6, east: 109.45 },
}
