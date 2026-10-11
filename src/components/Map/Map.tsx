import type { MapProps } from '../../types/map'
import LeafletMap from './leaflet/LeafletMap'
import styles from './Map.module.css'

export default function Map(props: MapProps) {
  return (
    <div className={styles.container}>
      <LeafletMap {...props} />
    </div>
  )
}
