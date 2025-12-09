import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import QuantumEngine from './quantum/QuantumEngine'
import AutonomousTrading from './autonomous/AutonomousTrading'
import './styles/App.css'

function App() {
  const [systemStatus, setSystemStatus] = useState('initializing')

  useEffect(() => {
    // Initialize system
    const initializeSystem = async () => {
      try {
        setSystemStatus('ready')
      } catch (error) {
        console.error('System initialization error:', error)
        setSystemStatus('error')
      }
    }

    initializeSystem()
  }, [])

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>NDAX Quantum Trading Engine</h1>
          <div className="status-indicator" data-status={systemStatus}>
            Status: {systemStatus}
          </div>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/quantum" element={<QuantumEngine />} />
            <Route path="/autonomous" element={<AutonomousTrading />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
