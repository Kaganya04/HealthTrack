export default function SymptomSummary({ summary, loading, error }) {
  if (!loading && !error && !summary) return null

  let content
  if (loading) {
    content = <p role="status">Loading summary</p>
  } else if (error) {
    content = <div role="alert" className="message error">{error}</div>
  } else if (summary.entry_count === 0) {
    content = <p role="status">No entries in this date range.</p>
  } else {
    const rows = Object.entries(summary.symptom_frequency)
    content = (
      <>
        <dl className="stats">
          <div>
            <dt>Entries</dt>
            <dd>{summary.entry_count}</dd>
          </div>
          <div>
            <dt>Average severity</dt>
            <dd>{summary.average_severity.toFixed(2)} out of 10</dd>
          </div>
          <div>
            <dt>Different descriptions</dt>
            <dd>{summary.unique_symptom_count}</dd>
          </div>
        </dl>
        <h3>How often each description was logged</h3>
        <ul className="frequency">
          {rows.map(([label, count]) => (
            <li key={label}>
              <span className="frequency-label">{label}</span>
              <span className="frequency-count">{count}</span>
            </li>
          ))}
        </ul>
        <p className="hint">
          Descriptions that differ only in capital letters or spacing are counted
          together. This is a count of what was written, not medical advice.
        </p>
      </>
    )
  }

  return (
    <section className="card" aria-labelledby="summary-title">
      <h2 id="summary-title">Summary</h2>
      {content}
    </section>
  )
}