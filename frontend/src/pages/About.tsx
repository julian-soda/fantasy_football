const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: '720px',
    margin: '3rem auto',
    padding: '0 2rem',
    lineHeight: 1.7,
    color: '#222',
  },
  h1: { fontSize: '1.8rem', fontWeight: 700, marginBottom: '1rem' },
  h2: { fontSize: '1.2rem', fontWeight: 700, marginTop: '2rem', marginBottom: '0.5rem' },
  p: { marginBottom: '1rem' },
  formula: {
    background: '#f5f0ff',
    border: '1px solid #d8bfff',
    borderRadius: '8px',
    padding: '0.9rem 1.2rem',
    fontFamily: 'monospace',
    fontSize: '0.95rem',
    marginBottom: '1rem',
  },
}

export default function About() {
  return (
    <div style={styles.container}>
      <h1 style={styles.h1}>About FF Luck Calculator</h1>

      <p style={styles.p}>
        Fantasy football standings depend not just on how many points your team scores, but on
        <em> who you happen to face each week</em>. A team that scores 130 points in a week where
        the league average is 110 might still lose if their one opponent scores 140. The FF Luck
        Calculator answers the question: <strong>how much did your schedule luck affect your record?</strong>
      </p>

      <p style={styles.p}>
        The tool fetches live matchup data from your Yahoo Fantasy Sports league and simulates every
        possible re-ordering of your schedule — every other team as your weekly opponent — to see
        what record you <em>would</em> have ended up with under each scenario.
      </p>

      <h2 style={styles.h2}>Luck Index</h2>

      <p style={styles.p}>
        After running the simulation, the Luck Index is computed as:
      </p>
      <div style={styles.formula}>
        Luck Index = (% of schedules where you'd have done <em>worse</em>) − (% where you'd have done <em>better</em>)
      </div>

      <p style={styles.p}>
        The index ranges from <strong>−100</strong> (worst possible luck — every other schedule
        gives a better record) to <strong>+100</strong> (best possible luck — every other schedule
        gives a worse record). A score near 0 means your record fairly reflects your scoring
        performance.
      </p>

      <p style={styles.p}>
        <strong>Example:</strong> If 70% of all possible schedules would have left you with a worse
        record and only 10% with a better one, your Luck Index is +60 — you were quite lucky.
        Conversely, −60 means you were unlucky: most alternate schedules would have treated you
        better.
      </p>

      <h2 style={styles.h2}>Assessments</h2>
      <p style={styles.p}>
        The table uses the absolute value of the index to classify luck:
      </p>
      <ul>
        <li>0–10: Average</li>
        <li>10–25: Somewhat lucky / unlucky</li>
        <li>25–50: Pretty lucky / unlucky</li>
        <li>50–75: Very lucky / unlucky</li>
        <li>75+: Extremely lucky / unlucky</li>
      </ul>

      <div style={{ marginTop: '3rem', paddingTop: '1.5rem', borderTop: '1px solid #e5e7eb' }}>
        <a
          href="https://github.com/julian-soda/fantasy_football"
          target="_blank"
          rel="noreferrer"
          style={{ color: '#222', display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}
          aria-label="View source on GitHub"
        >
          <svg height="24" width="24" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38
              0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13
              -.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66
              .07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15
              -.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0
              1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82
              1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01
              1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
          </svg>
          View source on GitHub
        </a>
      </div>
    </div>
  )
}
