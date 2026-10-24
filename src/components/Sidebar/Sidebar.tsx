import type { ReactNode } from 'react'
import styles from './Sidebar.module.css'

interface SidebarProps {
  readonly title: string
  readonly subtitle: string
  readonly isOpen: boolean
  readonly onToggle: () => void
  readonly children: ReactNode
}

const BODY_ID = 'sidebar-body'

export default function Sidebar({
  title,
  subtitle,
  isOpen,
  onToggle,
  children,
}: SidebarProps) {
  return (
    <div className={`${styles.sidebar} ${isOpen ? '' : styles.collapsed}`}>
      <header className={styles.header}>
        <div className={styles.heading} hidden={!isOpen}>
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
          {isOpen ? '‹' : '›'}
        </button>
      </header>
      <div id={BODY_ID} className={styles.body} hidden={!isOpen}>
        {children}
      </div>
    </div>
  )
}
