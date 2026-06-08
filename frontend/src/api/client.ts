import type {
  ApiError,
  HealthResponse,
  IngestResponse,
  IngestTextRequest,
  QueryRequest,
  QueryResponse,
} from './types'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })

  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const body = (await response.json()) as ApiError
      if (body.detail) message = body.detail
    } catch {
      // ignore parse errors
    }
    throw new Error(message)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export const api = {
  health: () => request<HealthResponse>('/health'),

  query: (payload: QueryRequest) =>
    request<QueryResponse>('/query', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  ingestText: (payload: IngestTextRequest) =>
    request<IngestResponse>('/ingest/text', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  resetIndex: () =>
    request<{ status: string }>('/admin/reset', { method: 'POST' }),
}
