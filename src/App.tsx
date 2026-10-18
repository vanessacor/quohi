import { useState } from 'react'
import EventPanel from './components/EventPanel/EventPanel'
import Filters from './components/Filters/Filters'
import Map from './components/Map/Map'
import { city } from './config/city'
import { events } from './data/events'
import { eventToMarker } from './utils/eventToMarker'
import { eventOverlapsRange, filterEventsByRange } from './utils/filterEvents'
import { parseYearRange } from './utils/parseYearRange'
import styles from './App.module.css'

export default function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [startText, setStartText] = useState('')
  const [endText, setEndText] = useState('')

  const { range } = parseYearRange(startText, endText)
  const markers = filterEventsByRange(events, range).map(eventToMarker)
  const selectedEvent = events.find((event) => event.id === selectedId) ?? null

  function handleRangeChange(nextStart: string, nextEnd: string) {
    setStartText(nextStart)
    setEndText(nextEnd)
    // Clear the selection now if the new range hides the selected event, so it
    // does not silently reappear when the range is widened again.
    const nextRange = parseYearRange(nextStart, nextEnd).range
    if (selectedEvent && !eventOverlapsRange(selectedEvent, nextRange)) {
      setSelectedId(null)
    }
  }

  return (
    <div className={styles.app}>
      <div className={styles.sidebar}>
        <Filters
          startText={startText}
          endText={endText}
          onChange={handleRangeChange}
        />
        <EventPanel event={selectedEvent} onClose={() => setSelectedId(null)} />
      </div>
      <Map
        center={city.center}
        zoom={city.zoom}
        markers={markers}
        selectedId={selectedId}
        onMarkerClick={setSelectedId}
      />
    </div>
  )
}
