import { useState } from 'react'
import EventDetails from './components/EventDetails/EventDetails'
import Filters from './components/Filters/Filters'
import Map from './components/Map/Map'
import Sidebar from './components/Sidebar/Sidebar'
import { city } from './config/city'
import { MOBILE_QUERY } from './config/layout'
import { events } from './data/events'
import { useMediaQuery } from './hooks/useMediaQuery'
import { eventToMarker } from './utils/eventToMarker'
import { eventOverlapsRange, filterEventsByRange } from './utils/filterEvents'
import { parseYearRange } from './utils/parseYearRange'
import styles from './App.module.css'

export default function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const isMobile = useMediaQuery(MOBILE_QUERY)
  // The mobile drawer starts collapsed so the map is visible first.
  const [isSidebarOpen, setIsSidebarOpen] = useState(!isMobile)
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

  // The details live in the sidebar, so a collapsed sidebar or drawer opens
  // to show the selected event.
  function handleMarkerClick(id: string) {
    setSelectedId(id)
    setIsSidebarOpen(true)
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
        <EventDetails
          event={selectedEvent}
          onClose={() => setSelectedId(null)}
        />
      </Sidebar>
      <div className={styles.mapArea}>
        <Map
          center={city.center}
          zoom={city.zoom}
          markers={markers}
          selectedId={selectedId}
          onMarkerClick={handleMarkerClick}
        />
      </div>
    </div>
  )
}
