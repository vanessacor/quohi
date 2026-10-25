import type { ReactNode } from 'react'
import styles from './Sidebar.module.css'

interface SidebarProps {
  readonly title: string
  readonly subtitle: string
  readonly isOpen: boolean
  // Mobile only: the open drawer fills the screen.
  readonly isFull: boolean
  readonly onToggle: () => void
  readonly children: ReactNode
}

const BODY_ID = 'sidebar-body'

export default function Sidebar({
  title,
  subtitle,
  isOpen,
  isFull,
  onToggle,
  children,
}: SidebarProps) {
  return (
    <div
      className={`${styles.sidebar} ${isOpen ? '' : styles.collapsed} ${isFull ? styles.full : ''}`}
    >
      <header className={styles.header}>
        <div className={styles.heading}>
          <h1 className={styles.title}>{title}</h1>
          <p className={styles.subtitle}>{subtitle}</p>
        </div>
        <button
          type="button"
          className={styles.toggle}
          onClick={onToggle}
          aria-expanded={isOpen}
          aria-controls={BODY_ID}
          aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          <span className={styles.chevron} aria-hidden="true">
            {isOpen ? '‹' : '›'}
          </span>
        </button>
      </header>
      <div id={BODY_ID} className={styles.body} hidden={!isOpen}>
        {children}
      </div>
    </div>
  )
}
