import { StreamEvent } from '../hooks/useStream'

interface Props {
  events: StreamEvent[]
  totalTeams?: number
}

const styles: Record<string, React.CSSProperties> = {
  list: { listStyle: 'none', margin: '1rem 0' },
  item: {
    padding: '0.6rem 0',
    borderBottom: '1px solid #eee',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '1rem',
  },
  team: { fontWeight: 500 },
  record: { color: '#555', fontSize: '0.9rem' },
  index: {
    fontWeight: 700,
    fontVariantNumeric: 'tabular-nums',
    minWidth: '56px',
    textAlign: 'right',
  },
  spinner: {
    width: '18px',
    height: '18px',
    border: '2px solid #ddd',
    borderTop: '2px solid #6001d2',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  },
}

function luckColor(index: number) {
  if (index > 30) return '#1a7f37'
  if (index > 0) return '#4caf50'
  if (index > -30) return '#f57c00'
  return '#c62828'
}

export default function ProgressList({ events, totalTeams }: Props) {
  const progressEvents = events.filter(e => e.type === 'progress')

  return (
    <div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <p style={{ color: '#555', marginBottom: '0.5rem' }}>
        {progressEvents.length}
        {totalTeams ? ` / ${totalTeams}` : ''} teams processed
      </p>
      <ul style={styles.list}>
        {progressEvents.map((e, i) => (
          <li key={i} style={styles.item}>
            <span style={styles.team}>{e.team}</span>
            <span style={styles.record}>{e.record}</span>
            <span style={{ ...styles.index, color: luckColor(e.luck_index ?? 0) }}>
              {(e.luck_index ?? 0) > 0 ? '+' : ''}{e.luck_index?.toFixed(1)}
            </span>
          </li>
        ))}
        {progressEvents.length < (totalTeams ?? Infinity) && (
          <li style={{ padding: '0.6rem 0', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={styles.spinner} />
            <span style={{ color: '#888' }}>Simulating…</span>
          </li>
        )}
      </ul>
    </div>
  )
}
