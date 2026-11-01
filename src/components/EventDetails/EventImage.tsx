import { useState } from 'react'
import type { EventImage as EventImageData } from '../../types/event'
import styles from './EventDetails.module.css'

interface EventImageProps {
  readonly image: EventImageData
  readonly title: string
}

/** Renders only with attribution (ADR-009); hides itself if the load fails. */
export default function EventImage({ image, title }: EventImageProps) {
  const [failed, setFailed] = useState(false)

  if (!image.attribution || failed) return null

  const credit = [image.attribution, image.license].filter(Boolean).join(', ')

  return (
    <figure className={styles.figure}>
      <img
        className={styles.image}
        src={image.url}
        alt={title}
        loading="lazy"
        onError={() => setFailed(true)}
      />
      <figcaption className={styles.caption}>Photo: {credit}</figcaption>
    </figure>
  )
}
