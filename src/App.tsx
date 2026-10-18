import { useState } from 'react'
import EventPanel from './components/EventPanel/EventPanel'
import Filters from './components/Filters/Filters'
import Map from './components/Map/Map'
import { city } from './config/city'
import { events } from './data/events'
import { eventToMarker } from './utils/eventToMarker'
import styles from './App.module.css'

const markers = events.map(eventToMarker)

export default function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [startText, setStartText] = useState('')
  const [endText, setEndText] = useState('')
  const selectedEvent = events.find((event) => event.id === selectedId) ?? null

  return (
    <div className={styles.app}>
      <div className={styles.sidebar}>
        <Filters
          startText={startText}
          endText={endText}
          onChange={(start, end) => {
            setStartText(start)
            setEndText(end)
          }}
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
