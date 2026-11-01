import type { EventSources, HistoricalEvent } from '../../types/event'
import { formatEventDate } from '../../utils/formatEventDate'
import EventImage from './EventImage'
import styles from './EventDetails.module.css'

interface EventDetailsProps {
  readonly event: HistoricalEvent | null
  readonly onClose: () => void
}

function SourceLinks({ sources }: { readonly sources?: EventSources }) {
  const links = [
    { label: 'Wikipedia', href: sources?.wikipedia },
    { label: 'Wikidata', href: sources?.wikidata },
  ].filter((link) => link.href)

  if (links.length === 0) return null

  return (
    <ul className={styles.sources} aria-label="Sources">
      {links.map(({ label, href }) => (
        <li key={label}>
          <a href={href} target="_blank" rel="noopener noreferrer">
            {label}
          </a>
        </li>
      ))}
    </ul>
  )
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
          {event.image && (
            <EventImage
              key={event.id}
              image={event.image}
              title={event.title}
            />
          )}
          <p className={styles.description}>
            {event.summary ?? event.description}
          </p>
          {event.summary && <p className={styles.note}>AI-generated summary</p>}
          <SourceLinks sources={event.sources} />
        </>
      ) : (
        <p className={styles.empty}>Select an event marker to see details.</p>
      )}
    </section>
  )
}
