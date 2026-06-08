import { useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api/client'
import type { QueryResponse } from '../api/types'
import { CitationCard } from './CitationCard'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  response?: QueryResponse
}

const STARTER_QUESTIONS = [
  'How many vacation days do employees receive?',
  'Is MFA required on production systems?',
  'What is the remote work policy?',
]

export function ChatPanel({ onIndexedChange }: { onIndexedChange: () => void }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const listRef = useRef<HTMLDivElement>(null)

  async function ask(question: string) {
    const trimmed = question.trim()
    if (!trimmed || loading) return

    setError(null)
    setLoading(true)
    setInput('')

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: trimmed,
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      const response = await api.query({ question: trimmed })
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.answer,
        response,
      }
      setMessages((prev) => [...prev, assistantMessage])
      onIndexedChange()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed')
    } finally {
      setLoading(false)
      requestAnimationFrame(() => {
        listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' })
      })
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    void ask(input)
  }

  return (
    <div className="chat-panel">
      <header className="panel-header">
        <div>
          <h2>Ask your documents</h2>
          <p>Grounded answers with source citations from your indexed knowledge base.</p>
        </div>
      </header>

      <div className="chat-messages" ref={listRef}>
        {messages.length === 0 ? (
          <div className="chat-empty">
            <p>Start with a question about your company docs.</p>
            <div className="starter-grid">
              {STARTER_QUESTIONS.map((question) => (
                <button
                  key={question}
                  type="button"
                  className="starter-chip"
                  onClick={() => void ask(question)}
                  disabled={loading}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <article key={message.id} className={`message message-${message.role}`}>
              <div className="message-label">{message.role === 'user' ? 'You' : 'Assistant'}</div>
              <div className="message-body">{message.content}</div>
              {message.response && (
                <div className="message-meta">
                  <span className={`grounded-badge ${message.response.grounded ? 'grounded' : 'ungrounded'}`}>
                    {message.response.grounded ? 'Grounded in sources' : 'Low confidence'}
                  </span>
                  {message.response.citations.length > 0 && (
                    <div className="citations-list">
                      {message.response.citations.map((citation, index) => (
                        <CitationCard key={`${citation.source_name}-${citation.chunk_index}`} citation={citation} index={index} />
                      ))}
                    </div>
                  )}
                </div>
              )}
            </article>
          ))
        )}
        {loading && (
          <div className="message message-assistant loading-message">
            <div className="message-label">Assistant</div>
            <div className="typing-indicator">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
      </div>

      {error && <p className="form-error">{error}</p>}

      <form className="chat-form" onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about HR policy, security, engineering docs…"
          rows={3}
          disabled={loading}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              void ask(input)
            }
          }}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? 'Searching…' : 'Ask'}
        </button>
      </form>
    </div>
  )
}
