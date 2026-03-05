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
import { TeamResult } from './LuckTable'

interface Props {
  teams: Record<string, TeamResult>
}

function luckColor(index: number) {
  if (index > 30) return '#1a7f37'
  if (index > 0) return '#4caf50'
  if (index > -30) return '#f57c00'
  return '#c62828'
}

export default function LuckBarChart({ teams }: Props) {
  const data = Object.entries(teams)
    .sort(([, a], [, b]) => b.luck_index - a.luck_index)
    .map(([name, d]) => ({ name, luck_index: d.luck_index }))

  return (
    <ResponsiveContainer width="100%" height={Math.max(250, data.length * 36)}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 8, right: 40, left: 8, bottom: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
        <XAxis
          type="number"
          tickFormatter={v => (v > 0 ? `+${v}` : `${v}`)}
          domain={[-100, 100]}
          tick={{ fontSize: 12 }}
        />
        <YAxis
          type="category"
          dataKey="name"
          width={160}
          tick={{ fontSize: 13 }}
        />
        <Tooltip
          formatter={(value: number) => [
            (value > 0 ? '+' : '') + value.toFixed(2),
            'Luck Index',
          ]}
        />
        <ReferenceLine x={0} stroke="#999" />
        <Bar dataKey="luck_index" radius={[0, 4, 4, 0]}>
          {data.map(entry => (
            <Cell key={entry.name} fill={luckColor(entry.luck_index)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
