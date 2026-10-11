import Map from './components/Map/Map'
import { city } from './config/city'

export default function App() {
  return <Map center={city.center} zoom={city.zoom} />
}
