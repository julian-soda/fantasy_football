import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

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
  subtitle: {
    fontSize: '0.95rem',
    color: '#555',
    marginBottom: '1.5rem',
    lineHeight: 1.6,
  },
  instructionsBox: {
    background: '#f5f5f5',
    borderRadius: '8px',
    padding: '1rem 1.2rem',
    marginBottom: '1.5rem',
    fontSize: '0.88rem',
    color: '#444',
    lineHeight: 1.7,
  },
  instructionsTitle: {
    fontWeight: 700,
    marginBottom: '0.5rem',
    fontSize: '0.9rem',
  },
  label: {
    display: 'block',
    fontWeight: 600,
    marginBottom: '0.4rem',
    marginTop: '1.2rem',
  },
  input: {
    width: '100%',
    padding: '0.6rem 0.8rem',
    fontSize: '0.9rem',
    borderRadius: '6px',
    border: '1px solid #ccc',
    fontFamily: 'monospace',
    boxSizing: 'border-box',
  },
  hint: {
    fontSize: '0.8rem',
    color: '#888',
    marginTop: '0.25rem',
  },
  btn: {
    marginTop: '1.8rem',
    width: '100%',
    padding: '0.85rem',
    background: '#e8352a',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
  },
  btnDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed',
  },
  error: {
    color: '#c00',
    marginTop: '1rem',
    fontSize: '0.9rem',
  },
  backLink: {
    display: 'inline-block',
    marginBottom: '1rem',
    color: '#6001d2',
    textDecoration: 'none',
    fontSize: '0.9rem',
    cursor: 'pointer',
  },
}

export default function EspnLogin() {
  const navigate = useNavigate()
  const [espnS2, setEspnS2] = useState('')
  const [swid, setSwid] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!espnS2.trim() || !swid.trim()) {
      setError('Both fields are required')
      return
    }
    setLoading(true)
    setError('')
    try {
      const resp = await fetch('/auth/espn-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ espn_s2: espnS2.trim(), swid: swid.trim() }),
      })
      if (resp.ok) {
        navigate('/dashboard')
      } else {
        const data = await resp.json().catch(() => ({}))
        setError(data.detail || 'Login failed — please check your cookies and try again')
      }
    } catch {
      setError('Network error — please try again')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      <span style={styles.backLink} onClick={() => navigate('/')}>← Back</span>
      <h1 style={styles.title}>Login with ESPN</h1>
      <p style={styles.subtitle}>
        ESPN uses browser cookies instead of an OAuth login. Copy two cookie values
        from your browser and paste them below.
      </p>

      <div style={styles.instructionsBox}>
        <div style={styles.instructionsTitle}>How to find your ESPN cookies:</div>
        <ol style={{ margin: 0, paddingLeft: '1.2rem' }}>
          <li>Go to <strong>espn.com</strong> and log in to your account</li>
          <li>Open DevTools: press <strong>F12</strong> (Windows) or <strong>⌘⌥I</strong> (Mac)</li>
          <li>Click the <strong>Application</strong> tab (Chrome) or <strong>Storage</strong> tab (Firefox)</li>
          <li>Expand <strong>Cookies</strong> → click <strong>https://www.espn.com</strong></li>
          <li>Find <strong>espn_s2</strong> — copy the long value in the "Value" column</li>
          <li>Find <strong>SWID</strong> — copy the value (looks like <code>{'{GUID-FORMAT}'}</code>)</li>
        </ol>
      </div>

      <form onSubmit={handleSubmit}>
        <label style={styles.label}>espn_s2</label>
        <input
          style={styles.input}
          type="text"
          placeholder="Very long string starting with AEB..."
          value={espnS2}
          onChange={e => setEspnS2(e.target.value)}
          autoComplete="off"
          spellCheck={false}
        />

        <label style={styles.label}>SWID</label>
        <input
          style={styles.input}
          type="text"
          placeholder="{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}"
          value={swid}
          onChange={e => setSwid(e.target.value)}
          autoComplete="off"
          spellCheck={false}
        />
        <p style={styles.hint}>Include the curly braces.</p>

        {error && <p style={styles.error}>{error}</p>}

        <button
          type="submit"
          style={{ ...styles.btn, ...(loading ? styles.btnDisabled : {}) }}
          disabled={loading}
        >
          {loading ? 'Validating…' : 'Continue with ESPN'}
        </button>
      </form>
    </div>
  )
}
