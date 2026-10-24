import type { ReactNode } from 'react'
import styles from './Sidebar.module.css'

interface SidebarProps {
  readonly title: string
  readonly subtitle: string
  readonly children: ReactNode
}

export default function Sidebar({ title, subtitle, children }: SidebarProps) {
  return (
    <div className={styles.sidebar}>
      <header className={styles.header}>
        <h1 className={styles.title}>{title}</h1>
        <p className={styles.subtitle}>{subtitle}</p>
      </header>
      <div className={styles.body}>{children}</div>
    </div>
  )
}
