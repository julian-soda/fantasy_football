import { useState } from 'react'

export interface TeamResult {
  luck_index: number
  pct_worse: number
  pct_better: number
  record: string
  scores?: number[]
}

interface Props {
  teams: Record<string, TeamResult>
}

type SortKey = 'luck_index' | 'pct_worse' | 'pct_better' | 'team'

const styles: Record<string, React.CSSProperties> = {
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '0.95rem',
  },
  th: {
    textAlign: 'left',
    padding: '0.6rem 0.8rem',
    borderBottom: '2px solid #ddd',
    cursor: 'pointer',
    userSelect: 'none',
    whiteSpace: 'nowrap',
    fontWeight: 600,
  },
  td: {
    padding: '0.55rem 0.8rem',
    borderBottom: '1px solid #eee',
  },
  number: {
    textAlign: 'right' as const,
    fontVariantNumeric: 'tabular-nums',
  },
}

function luckColor(index: number) {
  if (index > 30) return '#1a7f37'
  if (index > 0) return '#4caf50'
  if (index > -30) return '#f57c00'
  return '#c62828'
}

function luckLabel(index: number) {
  const abs = Math.abs(index)
  const dir = index >= 0 ? 'lucky' : 'unlucky'
  if (abs < 10) return 'Average'
  if (abs < 25) return `Somewhat ${dir}`
  if (abs < 50) return `Pretty ${dir}`
  if (abs < 75) return `Very ${dir}`
  return `Extremely ${dir}`
}

export default function LuckTable({ teams }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>('luck_index')
  const [sortAsc, setSortAsc] = useState(false)

  function handleSort(key: SortKey) {
    if (key === sortKey) {
      setSortAsc(a => !a)
    } else {
      setSortKey(key)
      setSortAsc(key === 'team')
    }
  }

  const rows = Object.entries(teams).sort(([nameA, a], [nameB, b]) => {
    let diff = 0
    if (sortKey === 'team') diff = nameA.localeCompare(nameB)
    else diff = (a[sortKey] as number) - (b[sortKey] as number)
    return sortAsc ? diff : -diff
  })

  function arrow(key: SortKey) {
    if (key !== sortKey) return ' ↕'
    return sortAsc ? ' ↑' : ' ↓'
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={{ ...styles.th, width: '2rem' }}>#</th>
            <th style={styles.th} onClick={() => handleSort('team')}>
              Team{arrow('team')}
            </th>
            <th style={{ ...styles.th, ...styles.number }}>Record</th>
            <th style={{ ...styles.th, ...styles.number }} onClick={() => handleSort('luck_index')}>
              Luck Index{arrow('luck_index')}
            </th>
            <th style={{ ...styles.th, ...styles.number }} onClick={() => handleSort('pct_worse')}>
              % Worse{arrow('pct_worse')}
            </th>
            <th style={{ ...styles.th, ...styles.number }} onClick={() => handleSort('pct_better')}>
              % Better{arrow('pct_better')}
            </th>
            <th style={styles.th}>Assessment</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([name, data], i) => (
            <tr key={name}>
              <td style={styles.td}>{i + 1}</td>
              <td style={styles.td}>{name}</td>
              <td style={{ ...styles.td, ...styles.number }}>{data.record}</td>
              <td style={{
                ...styles.td,
                ...styles.number,
                fontWeight: 700,
                color: luckColor(data.luck_index),
              }}>
                {data.luck_index > 0 ? '+' : ''}{data.luck_index.toFixed(2)}
              </td>
              <td style={{ ...styles.td, ...styles.number }}>
                {data.pct_worse.toFixed(1)}%
              </td>
              <td style={{ ...styles.td, ...styles.number }}>
                {data.pct_better.toFixed(1)}%
              </td>
              <td style={styles.td}>{luckLabel(data.luck_index)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
