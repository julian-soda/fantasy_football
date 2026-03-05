import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useStream } from '../hooks/useStream'
import ProgressList from '../components/ProgressList'

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: '640px',
    margin: '3rem auto',
    padding: '2rem',
    background: '#fff',
    borderRadius: '12px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
  },
  title: { fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.5rem' },
  meta: { color: '#666', fontSize: '0.9rem', marginBottom: '1.5rem' },
  error: {
    background: '#fff0f0',
    border: '1px solid #f5c6cb',
    borderRadius: '6px',
    padding: '1rem',
    color: '#c00',
    marginTop: '1rem',
  },
  backBtn: {
    marginTop: '1.5rem',
    display: 'inline-block',
    padding: '0.5rem 1.2rem',
    border: '1px solid #ccc',
    borderRadius: '6px',
    cursor: 'pointer',
    background: '#fff',
    fontSize: '0.9rem',
  },
}

export default function Calculate() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [streamUrl, setStreamUrl] = useState<string | null>(null)

  const leagueId = searchParams.get('league_id') ?? ''
  const year = searchParams.get('year') ?? ''
  const throughWeek = searchParams.get('through_week')

  const { events, status, errorMsg } = useStream(streamUrl)

  useEffect(() => {
    if (!leagueId || !year) { navigate('/dashboard'); return }
    const params = new URLSearchParams({ league_id: leagueId, year })
    if (throughWeek) params.set('through_week', throughWeek)
    fetch(`/api/results/lookup?${params}`, { credentials: 'include' })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data?.result_id) {
          navigate(`/results/${data.result_id}`, { replace: true })
        } else {
          setStreamUrl(`/api/calculate?${params}`)
        }
      })
      .catch(() => setStreamUrl(`/api/calculate?${params}`))
  }, [leagueId, year, throughWeek, navigate])

  // Navigate to results page when the stream completes
  useEffect(() => {
    const completeEvent = events.find(e => e.type === 'complete')
    if (completeEvent?.result_id) {
      navigate(`/results/${completeEvent.result_id}`)
    }
  }, [events, navigate])

  const metaParts = [`Year: ${year}`]
  if (throughWeek) metaParts.push(`Through week ${throughWeek}`)

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Calculating Luck Index…</h1>
      <p style={styles.meta}>{metaParts.join(' · ')}</p>
      <p style={{ color: '#555', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
        {status === 'connecting' && 'Fetching league data from Yahoo…'}
        {status === 'streaming' && 'Running simulations — this takes 2–3 minutes.'}
        {status === 'done' && 'Done! Redirecting…'}
        {status === 'error' && 'Something went wrong.'}
      </p>

      <ProgressList events={events} />

      {errorMsg && (
        <div style={styles.error}>
          <strong>Error:</strong> {errorMsg}
          <br />
          <button style={{ ...styles.backBtn, marginTop: '0.8rem' }} onClick={() => navigate('/dashboard')}>
            Back to dashboard
          </button>
        </div>
      )}

      {status === 'idle' || status === 'connecting' ? null : (
        <button style={styles.backBtn} onClick={() => navigate('/dashboard')}>
          Back to dashboard
        </button>
      )}
    </div>
  )
}
