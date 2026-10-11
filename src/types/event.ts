export interface HistoricalEvent {
  readonly id: string
  readonly title: string
  readonly year: number
  readonly month?: number
  readonly day?: number
  readonly endYear?: number
  readonly lat: number
  readonly lng: number
  readonly description: string
}
