import { city } from '../config/city'
import type { HistoricalEvent } from '../types/event'
import { parseEvents } from '../utils/parseEvents'
import rawEvents from './events.json'

// Validated at load: invalid data fails loudly instead of rendering wrong markers.
export const events: readonly HistoricalEvent[] = parseEvents(
  rawEvents,
  city.bounds,
)
