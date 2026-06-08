import { useCallback, useEffect, useState } from 'react'
import { api } from '../api/client'
import type { HealthResponse } from '../api/types'

export function useHealth(pollMs = 30_000) {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      const data = await api.health()
      setHealth(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to reach API')
      setHealth(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
    const id = window.setInterval(() => void refresh(), pollMs)
    return () => window.clearInterval(id)
  }, [refresh, pollMs])

  return { health, loading, error, refresh }
}
