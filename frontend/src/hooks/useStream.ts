import { useEffect, useRef, useState } from 'react'

export interface StreamEvent {
  type: 'progress' | 'complete' | 'error'
  // progress
  team?: string
  luck_index?: number
  pct_worse?: number
  pct_better?: number
  record?: string
  scores?: number[]
  // complete
  result_id?: string
  // error
  message?: string
}

export type StreamStatus = 'idle' | 'connecting' | 'streaming' | 'done' | 'error'

export function useStream(url: string | null) {
  const [events, setEvents] = useState<StreamEvent[]>([])
  const [status, setStatus] = useState<StreamStatus>('idle')
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const esRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!url) return
    setEvents([])
    setStatus('connecting')
    setErrorMsg(null)

    const es = new EventSource(url, { withCredentials: true })
    esRef.current = es

    es.onopen = () => setStatus('streaming')

    es.onmessage = (e: MessageEvent) => {
      const event: StreamEvent = JSON.parse(e.data)
      if (event.type === 'error') {
        setErrorMsg(event.message ?? 'Unknown error')
        setStatus('error')
        es.close()
        return
      }
      setEvents(prev => [...prev, event])
      if (event.type === 'complete') {
        setStatus('done')
        es.close()
      }
    }

    es.onerror = () => {
      setStatus('error')
      setErrorMsg('Connection lost')
      es.close()
    }

    return () => { es.close() }
  }, [url])

  return { events, status, errorMsg }
}
