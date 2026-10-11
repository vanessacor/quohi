export interface LatLng {
  lat: number
  lng: number
}

export interface Bounds {
  south: number
  west: number
  north: number
  east: number
}

export interface MapMarker {
  id: string
  position: LatLng
  title: string
}

export interface MapProps {
  center: LatLng
  zoom: number
  markers?: MapMarker[]
  selectedId?: string | null
  onMarkerClick?: (id: string) => void
}
