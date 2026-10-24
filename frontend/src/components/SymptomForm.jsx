import { useState } from 'react'
import { saveSymptom } from '../api'

export default function SymptomForm({ onSaved, onEdit }) {
  const [date, setDate] = useState('')
  const [description, setDescription] = useState('')
  const [severity, setSeverity] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

    function clearMessages() {
    setError('')
    setSuccess('')
    if (onEdit) onEdit()
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (saving) return
    clearMessages()

    const cleanDescription = description.trim()
    const rating = Number(severity)

    if (!date) {
      setError('Choose a date.')
      return
    }
    if (!cleanDescription) {
      setError('Describe the symptom. The description cannot be empty.')
      return
    }
    if (severity === '' || !Number.isInteger(rating) || rating < 1 || rating > 10) {
      setError('Severity must be a whole number from 1 to 10.')
      return
    }

    setSaving(true)
    try {
      const saved = await saveSymptom({
        date,
        description: cleanDescription,
        severity: rating,
      })
      setSuccess('Entry saved')
      setDescription('')
      setSeverity('')
      if (onSaved) onSaved(saved)
    } catch (err) {
      setError(
        err instanceof TypeError
          ? 'Cannot reach the server. Check that the backend is running and try again.'
          : err.message,
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit} noValidate>
      <h2>Log a symptom</h2>

      {error && <div role="alert" className="message error">{error}</div>}
      {success && <div role="status" className="message success">{success}</div>}

      <label htmlFor="symptom-date">Date</label>
      <input
        id="symptom-date"
        type="date"
        required
        value={date}
        onChange={event => { setDate(event.target.value); clearMessages() }}
      />
            <p className="hint">Only one entry is allowed for each date.</p>

      <label htmlFor="symptom-description">Symptom description</label>
      <textarea
        id="symptom-description"
        required
        maxLength={1000}
        rows={4}
        value={description}
        onChange={event => { setDescription(event.target.value); clearMessages() }}
      />
      <p className="hint">Spaces around the text are removed. Up to 1,000 characters.</p>

      <label htmlFor="symptom-severity">Severity (1 to 10)</label>
      <input
        id="symptom-severity"
        type="number"
        required
        min="1"
        max="10"
        step="1"
        value={severity}
        onChange={event => { setSeverity(event.target.value); clearMessages() }}
      />
      <p className="hint">1 is lowest and 10 is highest.</p>

      <button type="submit" disabled={saving}>
        {saving ? 'Saving' : 'Save entry'}
      </button>
    </form>
  )
}