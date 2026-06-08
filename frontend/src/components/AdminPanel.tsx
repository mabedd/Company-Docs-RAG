import { useState } from 'react'
import { api } from '../api/client'

export function AdminPanel({ onIndexedChange }: { onIndexedChange: () => void }) {
  const [confirming, setConfirming] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleReset() {
    setLoading(true)
    setError(null)
    setMessage(null)

    try {
      await api.resetIndex()
      setMessage('Search index cleared. Re-ingest documents to rebuild the knowledge base.')
      setConfirming(false)
      onIndexedChange()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Reset failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-panel">
      <header className="panel-header">
        <div>
          <h2>Admin</h2>
          <p>Maintenance actions for the document index.</p>
        </div>
      </header>

      <div className="admin-card danger-zone">
        <h3>Reset index</h3>
        <p>
          Permanently removes all indexed chunks from ChromaDB. You will need to re-ingest documents
          before queries return grounded answers again.
        </p>

        {!confirming ? (
          <button type="button" className="danger-button" onClick={() => setConfirming(true)}>
            Reset index
          </button>
        ) : (
          <div className="confirm-row">
            <p className="confirm-text">This cannot be undone. Continue?</p>
            <div className="confirm-actions">
              <button type="button" onClick={() => setConfirming(false)} disabled={loading}>
                Cancel
              </button>
              <button type="button" className="danger-button" onClick={() => void handleReset()} disabled={loading}>
                {loading ? 'Resetting…' : 'Yes, reset'}
              </button>
            </div>
          </div>
        )}

        {error && <p className="form-error">{error}</p>}
        {message && <p className="form-success">{message}</p>}
      </div>
    </div>
  )
}
