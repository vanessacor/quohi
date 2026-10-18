import styles from './Filters.module.css'

interface FiltersProps {
  readonly startText: string
  readonly endText: string
  readonly onChange: (startText: string, endText: string) => void
}

export default function Filters({
  startText,
  endText,
  onChange,
}: FiltersProps) {
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
          onChange={(event) => onChange(startText, event.target.value)}
        />
      </label>
      <p className={styles.hint}>Use negative years for BCE, e.g. -221.</p>
    </form>
  )
}
