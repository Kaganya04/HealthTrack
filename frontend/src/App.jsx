import SymptomForm from './components/SymptomForm'
import './App.css'

export default function App() {
  return (
    <main className="page">
      <header>
        <h1>HealthTrack</h1>
        <p className="subtitle">Daily symptom diary</p>
      </header>
      <SymptomForm />
    </main>
  )
}