import { divIcon } from 'leaflet'
import styles from './markerIcons.module.css'

// A rotated square has a diagonal of side * sqrt(2); the icon box is that wide
// and tall, so the teardrop tip sits at the bottom center, on the anchor.
function pinIcon(side: number, className: string) {
  const size = Math.ceil(side * Math.SQRT2)
  return divIcon({
    className,
    html: `<span class="${styles.pin}"></span>`,
    iconSize: [size, size],
    iconAnchor: [Math.floor(size / 2), size],
  })
}

export const defaultIcon = pinIcon(20, styles.marker)

export const selectedIcon = pinIcon(26, `${styles.marker} ${styles.selected}`)
