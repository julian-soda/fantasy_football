import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

interface League {
  league_id: string
  name: string
  year: number
  num_teams: number
}

interface SessionInfo {
  provider: 'yahoo' | 'espn'
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: '560px',
    margin: '4rem auto',
    padding: '2rem',
    background: '#fff',
    borderRadius: '12px',
    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
  },
  title: {
    fontSize: '1.6rem',
    fontWeight: 700,
    marginBottom: '0.25rem',
  },
  label: {
    display: 'block',
    fontWeight: 600,
    marginBottom: '0.4rem',
    marginTop: '1.2rem',
  },
  select: {
    width: '100%',
    padding: '0.6rem 0.8rem',
    fontSize: '1rem',
    borderRadius: '6px',
    border: '1px solid #ccc',
    background: '#fff',
  },
  input: {
    width: '100%',
    padding: '0.6rem 0.8rem',
    fontSize: '1rem',
    borderRadius: '6px',
    border: '1px solid #ccc',
  },
  btn: {
    marginTop: '1.8rem',
    width: '100%',
    padding: '0.85rem',
    background: '#6001d2',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
  },
  logoutBtn: {
    float: 'right',
    background: 'none',
    border: 'none',
    color: '#888',
    cursor: 'pointer',
    fontSize: '0.9rem',
    textDecoration: 'underline',
  },
  error: {
    color: '#c00',
    marginTop: '1rem',
    fontSize: '0.9rem',
  },
  hint: {
    fontSize: '0.82rem',
    color: '#888',
    marginTop: '0.3rem',
  },
  providerBadge: {
    display: 'inline-block',
    fontSize: '0.75rem',
    fontWeight: 600,
    padding: '0.15rem 0.55rem',
    borderRadius: '999px',
    marginLeft: '0.6rem',
    verticalAlign: 'middle',
  },
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [leagues, setLeagues] = useState<League[]>([])
  const [selectedLeague, setSelectedLeague] = useState('')
  const [year, setYear] = useState(new Date().getFullYear() - 1)
  const [throughWeek, setThroughWeek] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [session, setSession] = useState<SessionInfo | null>(null)

  useEffect(() => {
    fetch('/api/leagues', { credentials: 'include' })
      .then(async r => {
        if (r.status === 401) { navigate('/'); return }
        if (!r.ok) throw new Error('Failed to load leagues')
        const data: League[] = await r.json()
        setLeagues(data)
        if (data.length > 0) {
          setSelectedLeague(data[0].league_id)
          setYear(data[0].year)
        }
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))

    fetch('/api/session', { credentials: 'include' })
      .then(async r => { if (r.ok) setSession(await r.json()) })
      .catch(() => {})
  }, [navigate])

  function handleLeagueChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const chosen = leagues.find(l => l.league_id === e.target.value)
    setSelectedLeague(e.target.value)
    if (chosen) setYear(chosen.year)
  }

  function handleCalculate() {
    if (!selectedLeague) { setError('Please select a league'); return }
    const params = new URLSearchParams({ league_id: selectedLeague, year: String(year) })
    if (throughWeek) params.set('through_week', throughWeek)
    navigate(`/calculate?${params}`)
  }

  async function handleLogout() {
    await fetch('/auth/logout', { method: 'POST', credentials: 'include' })
    navigate('/')
  }

  return (
    <div style={styles.container}>
      <button style={styles.logoutBtn} onClick={handleLogout}>Log out</button>
      <h1 style={styles.title}>
        FF Luck Calculator
        {session && (
          <span style={{
            ...styles.providerBadge,
            background: session.provider === 'espn' ? '#fde8e8' : '#ede8fb',
            color: session.provider === 'espn' ? '#c0392b' : '#6001d2',
          }}>
            {session.provider === 'espn' ? 'ESPN' : 'Yahoo'}
          </span>
        )}
      </h1>

      {loading && <p style={{ marginTop: '1rem', color: '#555' }}>Loading leagues…</p>}

      {!loading && (
        <>
          <label style={styles.label}>League</label>
          <select
            style={styles.select}
            value={selectedLeague}
            onChange={handleLeagueChange}
          >
            {leagues.map(l => (
              <option key={`${l.league_id}-${l.year}`} value={l.league_id}>
                {l.name} ({l.year})
              </option>
            ))}
          </select>

          <label style={styles.label}>Season year</label>
          <input
            style={styles.input}
            type="number"
            value={year}
            onChange={e => setYear(Number(e.target.value))}
            min={2012}
            max={new Date().getFullYear()}
          />

          <label style={styles.label}>Through week (optional)</label>
          <input
            style={styles.input}
            type="number"
            placeholder="e.g. 8 — leave blank for full season"
            value={throughWeek}
            onChange={e => setThroughWeek(e.target.value)}
            min={1}
            max={18}
          />
          <p style={styles.hint}>Leave blank to use all regular-season weeks.</p>

          {error && <p style={styles.error}>{error}</p>}

          <button style={styles.btn} onClick={handleCalculate}>
            Calculate Luck Index
          </button>
        </>
      )}
    </div>
  )
}
