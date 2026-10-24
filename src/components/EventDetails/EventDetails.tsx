import type { HistoricalEvent } from '../../types/event'
import { formatEventDate } from '../../utils/formatEventDate'
import styles from './EventDetails.module.css'

interface EventDetailsProps {
  readonly event: HistoricalEvent | null
  readonly onClose: () => void
}

export default function EventDetails({ event, onClose }: EventDetailsProps) {
  return (
    <section
      className={`${styles.details} ${event ? styles.selected : ''}`}
      aria-label="Event details"
      aria-live="polite"
    >
      {event ? (
        <>
          <div className={styles.header}>
            <h2 className={styles.title}>{event.title}</h2>
            <button
              type="button"
              className={styles.close}
              onClick={onClose}
              aria-label="Close event details"
            >
              ×
            </button>
          </div>
          <p className={styles.date}>{formatEventDate(event)}</p>
          <p className={styles.description}>{event.description}</p>
        </>
      ) : (
        <p className={styles.empty}>Select an event marker to see details.</p>
      )}
    </section>
  )
}
