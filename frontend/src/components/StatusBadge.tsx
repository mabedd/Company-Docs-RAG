interface StatusBadgeProps {
  online: boolean
  documentsIndexed: number | null
  loading?: boolean
}

export function StatusBadge({ online, documentsIndexed, loading }: StatusBadgeProps) {
  return (
    <div className={`status-badge ${online ? 'online' : 'offline'}`}>
      <span className="status-dot" aria-hidden />
      <span className="status-text">
        {loading ? 'Checking…' : online ? 'API online' : 'API offline'}
      </span>
      {online && documentsIndexed !== null && (
        <span className="status-count">{documentsIndexed} chunks indexed</span>
      )}
    </div>
  )
}
