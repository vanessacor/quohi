import { useState } from 'react'
import EventList from './components/EventList/EventList'
import Filters from './components/Filters/Filters'
import Map from './components/Map/Map'
import Sidebar from './components/Sidebar/Sidebar'
import { city } from './config/city'
import { events } from './data/events'
import { eventToMarker } from './utils/eventToMarker'
import { eventOverlapsRange, filterEventsByRange } from './utils/filterEvents'
import { parseYearRange } from './utils/parseYearRange'
import styles from './App.module.css'

export default function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [startText, setStartText] = useState('')
  const [endText, setEndText] = useState('')

  const { range, error } = parseYearRange(startText, endText)
  const visibleEvents = filterEventsByRange(events, range)
  const markers = visibleEvents.map(eventToMarker)
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

  function handleReset() {
    handleRangeChange('', '')
  }

  return (
    <div className={styles.app}>
      <Sidebar
        title="Historical Events"
        subtitle={city.name}
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen((isOpen) => !isOpen)}
      >
        <Filters
          startText={startText}
          endText={endText}
          error={error}
          resultCount={visibleEvents.length}
          totalCount={events.length}
          onChange={handleRangeChange}
          onReset={handleReset}
        />
        <EventList
          events={visibleEvents}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
      </Sidebar>
      <div className={styles.mapArea}>
        <Map
          center={city.center}
          zoom={city.zoom}
          markers={markers}
          selectedId={selectedId}
          onMarkerClick={setSelectedId}
        />
      </div>
    </div>
  )
}
