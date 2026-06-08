import type { ReactNode } from 'react'
import { StatusBadge } from './StatusBadge'

export type Tab = 'ask' | 'ingest' | 'admin'

interface LayoutProps {
  activeTab: Tab
  onTabChange: (tab: Tab) => void
  healthOnline: boolean
  documentsIndexed: number | null
  healthLoading: boolean
  healthError: string | null
  onRefreshHealth: () => void
  children: ReactNode
}

const NAV: { id: Tab; label: string; description: string }[] = [
  { id: 'ask', label: 'Ask', description: 'Query indexed docs' },
  { id: 'ingest', label: 'Ingest', description: 'Add new content' },
  { id: 'admin', label: 'Admin', description: 'Index maintenance' },
]

export function Layout({
  activeTab,
  onTabChange,
  healthOnline,
  documentsIndexed,
  healthLoading,
  healthError,
  onRefreshHealth,
  children,
}: LayoutProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">CD</div>
          <div>
            <h1>Company Docs</h1>
            <p>Internal RAG</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          {NAV.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => onTabChange(item.id)}
            >
              <span className="nav-label">{item.label}</span>
              <span className="nav-description">{item.description}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <StatusBadge online={healthOnline} documentsIndexed={documentsIndexed} loading={healthLoading} />
          {healthError && (
            <button type="button" className="retry-link" onClick={onRefreshHealth}>
              Retry connection
            </button>
          )}
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  )
}
