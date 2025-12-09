import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/Dashboard.css'

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    totalTrades: 0,
    activeStrategies: 0,
    profitLoss: 0,
    systemHealth: 100
  })
  const navigate = useNavigate()

  const fetchMetrics = useCallback(async () => {
    try {
      // Placeholder for actual API call
      setMetrics({
        totalTrades: 127,
        activeStrategies: 5,
        profitLoss: 2450.75,
        systemHealth: 98
      })
    } catch (error) {
      console.error('Error fetching metrics:', error)
    }
  }, [])

  useEffect(() => {
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 30000) // Update every 30s

    return () => clearInterval(interval)
  }, [fetchMetrics])

  return (
    <div className="dashboard">
      <h2>Trading Dashboard</h2>
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Trades</h3>
          <p className="metric-value">{metrics.totalTrades}</p>
        </div>
        <div className="metric-card">
          <h3>Active Strategies</h3>
          <p className="metric-value">{metrics.activeStrategies}</p>
        </div>
        <div className="metric-card">
          <h3>Profit/Loss</h3>
          <p className={`metric-value ${metrics.profitLoss >= 0 ? 'positive' : 'negative'}`}>
            ${metrics.profitLoss.toFixed(2)}
          </p>
        </div>
        <div className="metric-card">
          <h3>System Health</h3>
          <p className="metric-value">{metrics.systemHealth}%</p>
        </div>
      </div>
      <div className="action-buttons">
        <button onClick={() => navigate('/quantum')}>Quantum Engine</button>
        <button onClick={() => navigate('/autonomous')}>Autonomous Trading</button>
      </div>
    </div>
  )
}

export default Dashboard
