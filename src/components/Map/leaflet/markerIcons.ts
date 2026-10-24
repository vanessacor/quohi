import { divIcon } from 'leaflet'
import styles from './markerIcons.module.css'

export const defaultIcon = divIcon({
  className: styles.marker,
  iconSize: [18, 18],
})

export const selectedIcon = divIcon({
  className: `${styles.marker} ${styles.selected}`,
  iconSize: [26, 26],
})
