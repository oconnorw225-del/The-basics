// API Service for NDAX integration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const apiService = {
  // Health check
  async health() {
    const response = await fetch(`${API_BASE_URL}/health`)
    return response.json()
  },

  // Get trading status
  async getTradingStatus() {
    const response = await fetch(`${API_BASE_URL}/api/status`)
    return response.json()
  },

  // Get market data
  async getMarketData(symbol) {
    const response = await fetch(`${API_BASE_URL}/api/market/${symbol}`)
    return response.json()
  },

  // Execute trade
  async executeTrade(tradeData) {
    const response = await fetch(`${API_BASE_URL}/api/trade`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(tradeData),
    })
    return response.json()
  },

  // Get quantum metrics
  async getQuantumMetrics() {
    const response = await fetch(`${API_BASE_URL}/api/quantum/metrics`)
    return response.json()
  },
}

export default apiService
