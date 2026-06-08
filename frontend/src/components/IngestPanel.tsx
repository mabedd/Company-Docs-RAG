import { useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { api } from '../api/client'

const SUPPORTED_EXTENSIONS = ['.txt']

export function IngestPanel({ onIndexedChange }: { onIndexedChange: () => void }) {
  const [sourceName, setSourceName] = useState('')
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function ingest(source: string, content: string) {
    if (!source.trim() || !content.trim()) {
      setError('Source name and document text are required.')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await api.ingestText({
        source_name: source.trim(),
        text: content.trim(),
        source_type: 'text',
      })
      setSuccess(`Indexed ${result.chunks_added} chunk${result.chunks_added === 1 ? '' : 's'} from "${source.trim()}".`)
      setSourceName('')
      setText('')
      onIndexedChange()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ingest failed')
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    void ingest(sourceName, text)
  }

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return

    const extension = file.name.includes('.') ? `.${file.name.split('.').pop()?.toLowerCase()}` : ''
    if (!SUPPORTED_EXTENSIONS.includes(extension)) {
      setError(`"${file.name}" is not supported yet. Upload .txt files or paste content below.`)
      event.target.value = ''
      return
    }

    const content = await file.text()
    setSourceName(file.name)
    setText(content)
    setError(null)
    setSuccess(`Loaded "${file.name}" — review and click Index document.`)
    event.target.value = ''
  }

  return (
    <div className="ingest-panel">
      <header className="panel-header">
        <div>
          <h2>Add documents</h2>
          <p>Paste text or upload a .txt file. Content is chunked and embedded into the search index.</p>
        </div>
      </header>

      <div className="upload-zone">
        <label className="upload-label">
          <input type="file" accept=".txt,text/plain" onChange={handleFileChange} disabled={loading} />
          <span className="upload-icon">↑</span>
          <span>Drop a .txt file or click to browse</span>
        </label>
      </div>

      <form className="ingest-form" onSubmit={handleSubmit}>
        <label>
          Source name
          <input
            type="text"
            value={sourceName}
            onChange={(e) => setSourceName(e.target.value)}
            placeholder="e.g. hr-policy.txt"
            disabled={loading}
          />
        </label>

        <label>
          Document text
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste policy text, meeting notes, or documentation…"
            rows={12}
            disabled={loading}
          />
        </label>

        {error && <p className="form-error">{error}</p>}
        {success && <p className="form-success">{success}</p>}

        <button type="submit" disabled={loading || !sourceName.trim() || !text.trim()}>
          {loading ? 'Indexing…' : 'Index document'}
        </button>
      </form>
    </div>
  )
}
