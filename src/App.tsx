import { useState } from 'react'
import EventPanel from './components/EventPanel/EventPanel'
import Map from './components/Map/Map'
import { city } from './config/city'
import { events } from './data/events'
import { eventToMarker } from './utils/eventToMarker'
import styles from './App.module.css'

const markers = events.map(eventToMarker)

export default function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const selectedEvent = events.find((event) => event.id === selectedId) ?? null

  return (
    <div className={styles.app}>
      <EventPanel event={selectedEvent} onClose={() => setSelectedId(null)} />
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
