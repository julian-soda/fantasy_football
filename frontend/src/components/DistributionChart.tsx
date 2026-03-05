import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Cell,
  ResponsiveContainer,
} from 'recharts'
import { useIsMobile } from '../hooks/useIsMobile'

interface Props {
  distribution: Record<string, number>
  actualRecord: string
}

function sortRecords(a: string, b: string) {
  const winsA = parseInt(a.split('-')[0], 10)
  const winsB = parseInt(b.split('-')[0], 10)
  return winsA - winsB
}

function formatRecord(record: string) {
  const parts = record.split('-')
  if (parts.length === 3 && parts[2] === '0') return `${parts[0]}-${parts[1]}`
  return record
}

export default function DistributionChart({ distribution, actualRecord }: Props) {
  const isMobile = useIsMobile()
  const data = Object.entries(distribution)
    .sort(([a], [b]) => sortRecords(a, b))
    .map(([record, pct]) => ({ record, label: formatRecord(record), pct }))

  const formattedActual = formatRecord(actualRecord)

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 12, right: 16, left: 0, bottom: isMobile ? 32 : 4 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" tick={isMobile ? { fontSize: 11, angle: -45, textAnchor: 'end' } : { fontSize: 11 }} interval={0} />
        <YAxis
          tickFormatter={v => `${v}%`}
          tick={{ fontSize: 11 }}
          domain={[0, 'auto']}
        />
        <Tooltip formatter={(v: number) => [`${v.toFixed(1)}%`, 'Schedules']} labelFormatter={l => `Record: ${l}`} />
        <ReferenceLine
          x={formattedActual}
          stroke="#d97706"
          strokeWidth={2}
          label={{ value: 'actual', position: 'insideTopRight', fontSize: 11, fill: '#d97706' }}
        />
        <Bar dataKey="pct" radius={[3, 3, 0, 0]}>
          {data.map(entry => (
            <Cell
              key={entry.record}
              fill={entry.label === formattedActual ? '#d97706' : '#6366f1'}
              fillOpacity={entry.label === formattedActual ? 1 : 0.65}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
