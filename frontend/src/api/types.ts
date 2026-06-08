export interface HealthResponse {
  status: string
  documents_indexed: number
}

export interface IngestTextRequest {
  source_name: string
  text: string
  source_type?: string
}

export interface IngestResponse {
  chunks_added: number
}

export interface QueryRequest {
  question: string
}

export interface Citation {
  source_type: string
  source_name: string
  chunk_index: number
  excerpt: string
  score: number
}

export interface QueryResponse {
  answer: string
  grounded: boolean
  citations: Citation[]
}

export interface ApiError {
  detail: string
}
