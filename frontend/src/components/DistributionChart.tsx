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

interface Props {
  distribution: Record<string, number>
  actualRecord: string
}

function sortRecords(a: string, b: string) {
  const winsA = parseInt(a.split('-')[0], 10)
  const winsB = parseInt(b.split('-')[0], 10)
  return winsA - winsB
}

export default function DistributionChart({ distribution, actualRecord }: Props) {
  const data = Object.entries(distribution)
    .sort(([a], [b]) => sortRecords(a, b))
    .map(([record, pct]) => ({ record, pct }))

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 12, right: 16, left: 0, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="record" tick={{ fontSize: 11 }} />
        <YAxis
          tickFormatter={v => `${v}%`}
          tick={{ fontSize: 11 }}
          domain={[0, 'auto']}
        />
        <Tooltip formatter={(v: number) => [`${v.toFixed(1)}%`, 'Schedules']} />
        <ReferenceLine
          x={actualRecord}
          stroke="#d97706"
          strokeWidth={2}
          label={{ value: 'actual', position: 'insideTopRight', fontSize: 11, fill: '#d97706' }}
        />
        <Bar dataKey="pct" radius={[3, 3, 0, 0]}>
          {data.map(entry => (
            <Cell
              key={entry.record}
              fill={entry.record === actualRecord ? '#d97706' : '#6366f1'}
              fillOpacity={entry.record === actualRecord ? 1 : 0.65}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
