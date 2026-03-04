import { useState } from 'react'
import DistributionChart from './DistributionChart'
import WeeklyScoresChart from './WeeklyScoresChart'

export interface TeamResult {
  luck_index: number
  pct_worse: number
  pct_better: number
  record: string
  scores?: number[]
  distribution?: Record<string, number>
}

interface Props {
  teams: Record<string, TeamResult>
  leagueAvg?: number[]
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
  expandRow: {
    background: '#f8f7ff',
    borderBottom: '2px solid #e0d8ff',
  },
  expandCell: {
    padding: '1rem 1.2rem',
    borderBottom: '2px solid #e0d8ff',
  },
  expandGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '1.5rem',
  },
  expandLabel: {
    fontSize: '0.82rem',
    fontWeight: 600,
    color: '#6001d2',
    marginBottom: '0.4rem',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.04em',
  },
}

export function luckColor(index: number) {
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

export default function LuckTable({ teams, leagueAvg = [] }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>('luck_index')
  const [sortAsc, setSortAsc] = useState(false)
  const [expandedTeam, setExpandedTeam] = useState<string | null>(null)

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

  const colCount = 7

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
          {rows.map(([name, data], i) => {
            const isExpanded = expandedTeam === name
            const rowStyle: React.CSSProperties = {
              cursor: 'pointer',
              background: isExpanded ? '#f0ebff' : undefined,
            }
            return (
              <>
                <tr
                  key={name}
                  style={rowStyle}
                  onClick={() => setExpandedTeam(isExpanded ? null : name)}
                >
                  <td style={styles.td}>{i + 1}</td>
                  <td style={styles.td}>
                    <span style={{ marginRight: '0.4rem', fontSize: '0.75rem', color: '#999' }}>
                      {isExpanded ? '▾' : '▸'}
                    </span>
                    {name}
                  </td>
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
                {isExpanded && (
                  <tr key={`${name}-expand`} style={styles.expandRow}>
                    <td colSpan={colCount} style={styles.expandCell}>
                      <div style={styles.expandGrid}>
                        {data.distribution && (
                          <div>
                            <div style={styles.expandLabel}>Record Distribution</div>
                            <DistributionChart
                              distribution={data.distribution}
                              actualRecord={data.record}
                            />
                          </div>
                        )}
                        {data.scores && data.scores.length > 0 && (
                          <div style={data.distribution ? {} : { gridColumn: '1 / -1' }}>
                            <div style={styles.expandLabel}>Weekly Scores vs League Average</div>
                            <WeeklyScoresChart scores={data.scores} leagueAvg={leagueAvg} />
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
