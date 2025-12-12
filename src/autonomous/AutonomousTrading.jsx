import { useState, useEffect } from 'react'
import '../styles/AutonomousTrading.css'

const MAX_TRADES_DISPLAY = 10

const AutonomousTrading = () => {
  const [isEnabled, setIsEnabled] = useState(false)
  const [tradingMode, setTradingMode] = useState('paper')
  const [activeTrades, setActiveTrades] = useState([])

  useEffect(() => {
    if (isEnabled) {
      // Simulate autonomous trading activity
      const interval = setInterval(() => {
        const newTrade = {
          id: Date.now(),
          pair: ['BTC/USD', 'ETH/USD', 'LTC/USD'][Math.floor(Math.random() * 3)],
          type: Math.random() > 0.5 ? 'BUY' : 'SELL',
          amount: (Math.random() * 10).toFixed(4),
          timestamp: new Date().toLocaleTimeString(),
        }
        setActiveTrades(prev => {
          const updated = [newTrade, ...prev]
          return updated.length > MAX_TRADES_DISPLAY
            ? updated.slice(0, MAX_TRADES_DISPLAY)
            : updated
        })
      }, 5000)

      return () => clearInterval(interval)
    }
  }, [isEnabled])

  return (
    <div className="autonomous-trading">
      <h2>Autonomous Trading System</h2>
      <div className="controls">
        <div className="mode-selector">
          <label>
            Trading Mode:
            <select
              value={tradingMode}
              onChange={e => setTradingMode(e.target.value)}
              disabled={isEnabled}
            >
              <option value="paper">Paper Trading</option>
              <option value="live">Live Trading</option>
            </select>
          </label>
        </div>
        <button
          className={isEnabled ? 'stop-button' : 'start-button'}
          onClick={() => setIsEnabled(!isEnabled)}
        >
          {isEnabled ? 'Stop Trading' : 'Start Trading'}
        </button>
      </div>
      <div className="trading-feed">
        <h3>Recent Trades ({tradingMode} mode)</h3>
        {activeTrades.length === 0 ? (
          <p>No trades yet. Start the autonomous trading system.</p>
        ) : (
          <ul>
            {activeTrades.map(trade => (
              <li key={trade.id} className={`trade-${trade.type.toLowerCase()}`}>
                <span className="trade-time">{trade.timestamp}</span>
                <span className="trade-type">{trade.type}</span>
                <span className="trade-pair">{trade.pair}</span>
                <span className="trade-amount">{trade.amount}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

export default AutonomousTrading
