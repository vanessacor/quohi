export interface EventImage {
  readonly url: string
  readonly license?: string
  readonly attribution?: string
}

export interface EventSources {
  readonly wikipedia?: string
  readonly wikidata?: string
}

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
  readonly locationName?: string
  readonly summary?: string
  readonly image?: EventImage
  readonly sources?: EventSources
}
