import { useState } from 'react'
import SymptomForm from './components/SymptomForm'
import SymptomHistory from './components/SymptomHistory'
import SymptomSummary from './components/SymptomSummary'
import { getSummary, getSymptoms } from './api'
import './App.css'

function rangeProblem(start, end) {
  if (!start || !end) return 'Choose both a start date and an end date.'
  if (start > end) return 'The start date must not be after the end date.'
  return ''
}

export default function App() {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [hasSearched, setHasSearched] = useState(false)
  const [summary, setSummary] = useState(null)
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [summaryError, setSummaryError] = useState('')

  function clearResults() {
    setSummary(null)
    setSummaryError('')
    setEntries([])
    setHasSearched(false)
    setError('')
    setNotice('')
  }

  function changeStart(value) {
    setStartDate(value)
    clearResults()
  }

  function changeEnd(value) {
    setEndDate(value)
    clearResults()
  }

  async function loadRange(start, end) {
    setLoading(true)
    setError('')
    try {
      const rows = await getSymptoms(start, end)
      setEntries(rows)
      setHasSearched(true)
    } catch (err) {
      setEntries([])
      setHasSearched(false)
      setError(
        err instanceof TypeError
          ? 'Cannot reach the server. Check that the backend is running and try again.'
          : err.message,
      )
    } finally {
      setLoading(false)
    }
  }

  async function handleSearch(event) {
    event.preventDefault()
    if (loading) return
    setNotice('')
    const problem = rangeProblem(startDate, endDate)
    if (problem) {
      setEntries([])
      setHasSearched(false)
      setError(problem)
      return
    }
    await loadRange(startDate, endDate)
  }

  async function loadSummary(start, end) {
    setSummaryLoading(true)
    setSummaryError('')
    try {
      setSummary(await getSummary(start, end))
    } catch (err) {
      setSummary(null)
      setSummaryError(
        err instanceof TypeError
          ? 'Cannot reach the server. Check that the backend is running and try again.'
          : err.message,
      )
    } finally {
      setSummaryLoading(false)
    }
  }

  async function handleSummary() {
    if (summaryLoading) return
    setNotice('')
    const problem = rangeProblem(startDate, endDate)
    if (problem) {
      setSummary(null)
      setSummaryError(problem)
      return
    }
    await loadSummary(startDate, endDate)
  }

  async function handleSaved(saved) {
    if (rangeProblem(startDate, endDate)) return
    if (saved.date < startDate || saved.date > endDate) {
      setNotice('Entry saved outside the selected range.')
      return
    }
    setNotice('')
    await loadRange(startDate, endDate)
    if (summary) await loadSummary(startDate, endDate)
  }

  return (
    <main className="page">
      <header>
        <h1>HealthTrack</h1>
        <p className="subtitle">Daily symptom diary</p>
      </header>
      <div className="layout">
        <SymptomForm onSaved={handleSaved} onEdit={() => setNotice('')} />
        <SymptomHistory
          startDate={startDate}
          endDate={endDate}
          onStartChange={changeStart}
          onEndChange={changeEnd}
          onSubmit={handleSearch}
          onSummary={handleSummary}
          entries={entries}
          loading={loading}
          error={error}
          notice={notice}
          hasSearched={hasSearched}
        />
      </div>
      <div className="summary-area">
        <SymptomSummary
          summary={summary}
          loading={summaryLoading}
          error={summaryError}
        />
      </div>
    </main>
  )
}