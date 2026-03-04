import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface Props {
  scores: number[]
  leagueAvg: number[]
}

export default function WeeklyScoresChart({ scores, leagueAvg }: Props) {
  const data = scores.map((score, i) => ({
    week: i + 1,
    score: parseFloat(score.toFixed(2)),
    avg: parseFloat((leagueAvg[i] ?? 0).toFixed(2)),
  }))

  return (
    <ResponsiveContainer width="100%" height={220}>
      <ComposedChart data={data} margin={{ top: 12, right: 16, left: 0, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="week" label={{ value: 'Week', position: 'insideBottom', offset: -2, fontSize: 11 }} tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip
          formatter={(v: number, name: string) => [
            v.toFixed(2),
            name === 'score' ? 'Team score' : 'League avg',
          ]}
          labelFormatter={l => `Week ${l}`}
        />
        <Legend
          formatter={name => name === 'score' ? 'Team score' : 'League avg'}
          wrapperStyle={{ fontSize: 12 }}
        />
        <Bar dataKey="score" fill="#6366f1" fillOpacity={0.75} radius={[3, 3, 0, 0]} />
        <Line dataKey="avg" type="monotone" stroke="#d97706" strokeWidth={2} dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
