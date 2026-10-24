import { useEffect } from 'react'
import { useMap } from 'react-leaflet'

// Leaflet only re-measures its container on window resize, so a layout change
// (e.g. the sidebar collapsing) leaves gray tile strips unless we tell it.
export default function MapResizer() {
  const map = useMap()

  useEffect(() => {
    const observer = new ResizeObserver(() => map.invalidateSize())
    observer.observe(map.getContainer())
    return () => observer.disconnect()
  }, [map])

  return null
}
