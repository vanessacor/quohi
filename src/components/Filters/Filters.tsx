import styles from './Filters.module.css'

interface FiltersProps {
  readonly startText: string
  readonly endText: string
  readonly error: string | null
  readonly resultCount: number
  readonly totalCount: number
  readonly onChange: (startText: string, endText: string) => void
  readonly onReset: () => void
}

const ERROR_ID = 'filters-error'

export default function Filters({
  startText,
  endText,
  error,
  resultCount,
  totalCount,
  onChange,
  onReset,
}: FiltersProps) {
  const hasError = error !== null
  const isEmpty = !hasError && resultCount === 0

  return (
    <form
      className={styles.filters}
      aria-label="Filter events by year"
      onSubmit={(event) => event.preventDefault()}
    >
      <label className={styles.field}>
        <span className={styles.label}>From year</span>
        <input
          type="text"
          inputMode="numeric"
          autoComplete="off"
          className={styles.input}
          value={startText}
          placeholder="e.g. -221"
          aria-invalid={hasError}
          aria-describedby={hasError ? ERROR_ID : undefined}
          onChange={(event) => onChange(event.target.value, endText)}
        />
      </label>
      <label className={styles.field}>
        <span className={styles.label}>To year</span>
        <input
          type="text"
          inputMode="numeric"
          autoComplete="off"
          className={styles.input}
          value={endText}
          placeholder="e.g. 1900"
          aria-invalid={hasError}
          aria-describedby={hasError ? ERROR_ID : undefined}
          onChange={(event) => onChange(startText, event.target.value)}
        />
      </label>
      <p className={styles.hint}>Use negative years for BCE, e.g. -221.</p>
      {hasError && (
        <p id={ERROR_ID} className={styles.error} role="alert">
          {error} Showing all events.
        </p>
      )}
      <div className={styles.summary}>
        <p className={styles.count} aria-live="polite" aria-atomic="true">
          Showing {resultCount} of {totalCount} events
          {isEmpty && ' – no events in this range.'}
        </p>
        <button
          type="button"
          className={styles.reset}
          onClick={onReset}
          disabled={startText === '' && endText === ''}
        >
          Reset
        </button>
      </div>
    </form>
  )
}
