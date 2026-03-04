import { Link } from 'react-router-dom'

const styles: Record<string, React.CSSProperties> = {
  nav: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0.75rem 2rem',
    borderBottom: '1px solid #e5e7eb',
    background: '#fff',
  },
  logo: {
    fontWeight: 700,
    fontSize: '1rem',
    color: '#6001d2',
    textDecoration: 'none',
  },
  link: {
    color: '#555',
    textDecoration: 'none',
    fontSize: '0.9rem',
  },
}

export default function Nav() {
  return (
    <nav style={styles.nav}>
      <Link to="/" style={styles.logo}>FF Luck Calculator</Link>
      <Link to="/about" style={styles.link}>About</Link>
    </nav>
  )
}
