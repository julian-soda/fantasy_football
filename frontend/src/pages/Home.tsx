import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem',
    textAlign: 'center',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: 700,
    marginBottom: '1rem',
  },
  subtitle: {
    fontSize: '1.1rem',
    color: '#555',
    maxWidth: '480px',
    lineHeight: 1.6,
    marginBottom: '2.5rem',
  },
  btnRow: {
    display: 'flex',
    gap: '1rem',
    flexWrap: 'wrap' as const,
    justifyContent: 'center',
  },
  yahooBtn: {
    display: 'inline-block',
    padding: '0.85rem 2rem',
    background: '#6001d2',
    color: '#fff',
    borderRadius: '8px',
    textDecoration: 'none',
    fontSize: '1rem',
    fontWeight: 600,
    border: 'none',
    cursor: 'pointer',
  },
  espnBtn: {
    display: 'inline-block',
    padding: '0.85rem 2rem',
    background: '#e8352a',
    color: '#fff',
    borderRadius: '8px',
    textDecoration: 'none',
    fontSize: '1rem',
    fontWeight: 600,
    border: 'none',
    cursor: 'pointer',
  },
  explainer: {
    marginTop: '3rem',
    fontSize: '0.85rem',
    color: '#888',
    maxWidth: '400px',
    lineHeight: 1.5,
  },
}

export default function Home() {
  const navigate = useNavigate()

  // If the user lands here with a session cookie already set (e.g. after OAuth
  // callback redirect), send them straight to the dashboard.
  useEffect(() => {
    fetch('/api/leagues', { credentials: 'include' })
      .then(r => { if (r.ok) navigate('/dashboard') })
      .catch(() => {})
  }, [navigate])

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>FF Luck Calculator</h1>
      <p style={styles.subtitle}>
        Find out how lucky (or unlucky) your fantasy football season really was.
        We simulate every possible schedule permutation and show you where you
        actually stand.
      </p>
      <div style={styles.btnRow}>
        <a href="/auth/login" style={styles.yahooBtn}>
          Login with Yahoo
        </a>
        <a href="/espn-login" style={styles.espnBtn}>
          Login with ESPN
        </a>
      </div>
      <p style={styles.explainer}>
        We only read your league data — we never write or modify anything.
        Your credentials are never stored in the browser.
        ESPN login requires copying cookies from your browser.
      </p>
    </div>
  )
}
