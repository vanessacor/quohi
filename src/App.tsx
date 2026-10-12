import { useState } from 'react'
import Map from './components/Map/Map'
import { city } from './config/city'
import { events } from './data/events'
import { eventToMarker } from './utils/eventToMarker'

const markers = events.map(eventToMarker)

export default function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null)

  return (
    <Map
      center={city.center}
      zoom={city.zoom}
      markers={markers}
      selectedId={selectedId}
      onMarkerClick={setSelectedId}
    />
  )
}
