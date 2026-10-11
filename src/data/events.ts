import { city } from '../config/city'
import { parseEvents } from '../utils/parseEvents'
import rawEvents from './events.json'

// Validated at load: invalid data fails loudly instead of rendering wrong markers.
export const events = parseEvents(rawEvents, city.bounds)
