import type { LatLng, MapMarker } from '../../types/map'
import LeafletMap from './leaflet/LeafletMap'
import styles from './Map.module.css'

export interface MapProps {
  center: LatLng
  zoom: number
  markers?: MapMarker[]
  selectedId?: string | null
  onMarkerClick?: (id: string) => void
}

export default function Map(props: MapProps) {
  return (
    <div className={styles.container}>
      <LeafletMap {...props} />
    </div>
  )
}
