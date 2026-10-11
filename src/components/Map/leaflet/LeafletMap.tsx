import 'leaflet/dist/leaflet.css'
import './setupLeafletIcons'
import { MapContainer, Marker, TileLayer } from 'react-leaflet'
import type { MapProps } from '../../../types/map'
import styles from './LeafletMap.module.css'

const TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
const ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

export default function LeafletMap({
  center,
  zoom,
  markers = [],
  selectedId = null,
  onMarkerClick,
}: MapProps) {
  return (
    <MapContainer
      center={[center.lat, center.lng]}
      zoom={zoom}
      className={styles.map}
    >
      <TileLayer url={TILE_URL} attribution={ATTRIBUTION} />
      {markers.map((marker) => (
        <Marker
          key={marker.id}
          position={[marker.position.lat, marker.position.lng]}
          title={marker.title}
          zIndexOffset={marker.id === selectedId ? 1000 : 0}
          eventHandlers={{ click: () => onMarkerClick?.(marker.id) }}
        />
      ))}
    </MapContainer>
  )
}
