export interface LatLng {
  readonly lat: number
  readonly lng: number
}

export interface Bounds {
  readonly south: number
  readonly west: number
  readonly north: number
  readonly east: number
}

export interface MapMarker {
  readonly id: string
  readonly position: LatLng
  readonly title: string
}

export interface MapProps {
  readonly center: LatLng
  readonly zoom: number
  readonly markers?: readonly MapMarker[]
  readonly selectedId?: string | null
  readonly onMarkerClick?: (id: string) => void
}
