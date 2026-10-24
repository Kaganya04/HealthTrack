export default function SymptomHistory({
  startDate,
  endDate,
  onStartChange,
  onEndChange,
  onSubmit,
  onSummary,
  entries,
  loading,
  error,
  notice,
  hasSearched,
}) {
  let content
  if (loading) {
    content = <p role="status">Loading entries</p>
  } else if (error) {
    content = null
  } else if (!hasSearched) {
    content = <p className="hint">Choose a date range.</p>
  } else if (entries.length === 0) {
    content = <p role="status">No entries in this date range.</p>
  } else {
    content = (
      <ul className="entries">
        {entries.map(entry => (
          <li key={entry.id} className="entry">
            <div className="entry-head">
              <span className="entry-date">{entry.date}</span>
              <span className="entry-severity">Severity {entry.severity} out of 10</span>
            </div>
            <p className="entry-text">{entry.description}</p>
          </li>
        ))}
      </ul>
    )
  }

  return (
    <section className="card" aria-labelledby="history-title">
      <h2 id="history-title">Symptom history</h2>

      <form onSubmit={onSubmit} noValidate>
        <div className="date-row">
          <div>
            <label htmlFor="start-date">Start date</label>
            <input
              id="start-date"
              type="date"
              required
              value={startDate}
              disabled={loading}
              onChange={event => onStartChange(event.target.value)}
            />
          </div>
          <div>
            <label htmlFor="end-date">End date</label>
            <input
              id="end-date"
              type="date"
              required
              value={endDate}
              disabled={loading}
              onChange={event => onEndChange(event.target.value)}
            />
          </div>
        </div>
        <p className="hint">Both the start date and the end date are included.</p>
        <div className="button-row">
          <button type="submit" disabled={loading}>
            {loading ? 'Loading' : 'Show entries'}
          </button>
          <button
            type="button"
            className="secondary"
            disabled={loading}
            onClick={onSummary}
          >
            Show summary
          </button>
        </div>
      </form>

      <div className="results">
        {error && <div role="alert" className="message error">{error}</div>}
        {notice && <div role="status" className="message info">{notice}</div>}
        {content}
      </div>
    </section>
  )
}