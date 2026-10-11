export interface HistoricalEvent {
  id: string
  title: string
  year: number
  month?: number
  day?: number
  endYear?: number
  lat: number
  lng: number
  description: string
}
