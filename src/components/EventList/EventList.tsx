import { useEffect, useRef } from 'react'
import type { HistoricalEvent } from '../../types/event'
import { formatEventDate } from '../../utils/formatEventDate'
import styles from './EventList.module.css'

interface EventListProps {
  readonly events: readonly HistoricalEvent[]
  readonly selectedId: string | null
  readonly onSelect: (id: string | null) => void
}

export default function EventList({
  events,
  selectedId,
  onSelect,
}: EventListProps) {
  const selectedItem = useRef<HTMLLIElement>(null)

  // A marker click can select an event that is scrolled out of view.
  useEffect(() => {
    selectedItem.current?.scrollIntoView({ block: 'nearest' })
  }, [selectedId])

  if (events.length === 0) {
    return null
  }

  return (
    <ul className={styles.list} aria-label="Events">
      {events.map((event) => {
        const isSelected = event.id === selectedId
        const detailsId = `event-details-${event.id}`

        return (
          <li
            key={event.id}
            ref={isSelected ? selectedItem : null}
            className={`${styles.item} ${isSelected ? styles.selected : ''}`}
          >
            <button
              type="button"
              className={styles.row}
              aria-expanded={isSelected}
              aria-controls={detailsId}
              onClick={() => onSelect(isSelected ? null : event.id)}
            >
              <span className={styles.title}>{event.title}</span>
              <span className={styles.date}>{formatEventDate(event)}</span>
            </button>
            {isSelected && (
              <div id={detailsId} className={styles.details}>
                <p className={styles.description}>{event.description}</p>
              </div>
            )}
          </li>
        )
      })}
    </ul>
  )
}
