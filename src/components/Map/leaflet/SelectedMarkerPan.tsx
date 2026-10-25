import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import type { MapMarker } from '../../../types/map'

interface SelectedMarkerPanProps {
  readonly markers: readonly MapMarker[]
  readonly selectedId: string | null
}

const PADDING: [number, number] = [60, 60]

// Moves the map only when the selected marker is outside the view, e.g. when a
// click hid it or the map was dragged away.
export default function SelectedMarkerPan({
  markers,
  selectedId,
}: SelectedMarkerPanProps) {
  const map = useMap()
  const position = markers.find((marker) => marker.id === selectedId)?.position
  const lat = position?.lat
  const lng = position?.lng

  useEffect(() => {
    if (lat !== undefined && lng !== undefined) {
      map.panInside([lat, lng], { padding: PADDING })
    }
  }, [map, lat, lng])

  return null
}
