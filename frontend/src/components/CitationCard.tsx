import type { Citation } from '../api/types'

interface CitationCardProps {
  citation: Citation
  index: number
}

export function CitationCard({ citation, index }: CitationCardProps) {
  const scorePercent = Math.round(citation.score * 100)

  return (
    <details className="citation-card">
      <summary>
        <span className="citation-index">[{index + 1}]</span>
        <span className="citation-source">{citation.source_name}</span>
        <span className="citation-meta">
          {citation.source_type} · chunk {citation.chunk_index} · {scorePercent}% match
        </span>
      </summary>
      <p className="citation-excerpt">{citation.excerpt}</p>
    </details>
  )
}
