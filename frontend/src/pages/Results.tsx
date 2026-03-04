import { useEffect, useMemo, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import LuckTable, { TeamResult } from '../components/LuckTable'
import LuckBarChart from '../components/LuckBarChart'

interface ResultData {
  result_id: string
  league_id: string
  year: number
  through_week: number | null
  created_at: string
  teams: Record<string, TeamResult>
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: '900px',
    margin: '3rem auto',
    padding: '2rem',
  },
  header: {
    marginBottom: '1.5rem',
  },
  title: {
    fontSize: '1.8rem',
    fontWeight: 700,
    marginBottom: '0.4rem',
  },
  meta: { color: '#666', fontSize: '0.9rem', marginBottom: '0.8rem' },
  shareBox: {
    background: '#f5f0ff',
    border: '1px solid #d8bfff',
    borderRadius: '8px',
    padding: '0.8rem 1rem',
    marginBottom: '1.5rem',
    display: 'flex',
    alignItems: 'center',
    gap: '0.8rem',
    flexWrap: 'wrap' as const,
  },
  shareUrl: {
    fontFamily: 'monospace',
    fontSize: '0.85rem',
    color: '#444',
    wordBreak: 'break-all' as const,
    flex: 1,
  },
  copyBtn: {
    padding: '0.4rem 0.9rem',
    background: '#6001d2',
    color: '#fff',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '0.85rem',
    whiteSpace: 'nowrap' as const,
  },
  card: {
    background: '#fff',
    borderRadius: '12px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
    padding: '1.5rem',
  },
  homeLink: {
    display: 'inline-block',
    marginTop: '1.5rem',
    color: '#6001d2',
    textDecoration: 'none',
    fontSize: '0.9rem',
  },
  error: { color: '#c00', marginTop: '2rem' },
  loading: { color: '#555', marginTop: '2rem' },
}

export default function Results() {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<ResultData | null>(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!id) return
    fetch(`/api/results/${id}`)
      .then(async r => {
        if (!r.ok) throw new Error(r.status === 404 ? 'Result not found' : 'Failed to load results')
        return r.json() as Promise<ResultData>
      })
      .then(setData)
      .catch(e => setError(e.message))
  }, [id])

  function copyLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  const leagueAvgByWeek = useMemo(() => {
    if (!data) return []
    const allScores = Object.values(data.teams)
      .map(t => t.scores ?? [])
      .filter(s => s.length > 0)
    if (allScores.length === 0) return []
    const numWeeks = Math.max(...allScores.map(s => s.length))
    return Array.from({ length: numWeeks }, (_, i) => {
      const vals = allScores.map(s => s[i]).filter(v => v !== undefined)
      return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0
    })
  }, [data])

  if (error) return <p style={styles.error}>{error}</p>
  if (!data) return <p style={styles.loading}>Loading…</p>

  const metaParts = [`Season ${data.year}`]
  if (data.through_week) metaParts.push(`through week ${data.through_week}`)
  const created = new Date(data.created_at).toLocaleDateString()

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Luck Index Results</h1>
        <p style={styles.meta}>{metaParts.join(', ')} · Calculated {created}</p>

        <div style={styles.shareBox}>
          <span style={styles.meta} >Shareable link:</span>
          <span style={styles.shareUrl}>{window.location.href}</span>
          <button style={styles.copyBtn} onClick={copyLink}>
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
      </div>

      <div style={{ ...styles.card, marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem', color: '#444' }}>
          Luck Ranking
        </h2>
        <LuckBarChart teams={data.teams} />
      </div>

      <div style={styles.card}>
        <LuckTable teams={data.teams} leagueAvg={leagueAvgByWeek} />
      </div>

      <Link to="/" style={styles.homeLink}>Calculate another league</Link>
    </div>
  )
}
