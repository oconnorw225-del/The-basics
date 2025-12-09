/**
 * Constants for the application
 */

export const TRADING_PAIRS = [
  'BTC/USD',
  'ETH/USD',
  'LTC/USD',
  'XRP/USD',
  'BCH/USD',
]

export const TRADING_MODES = {
  PAPER: 'paper',
  LIVE: 'live',
}

export const ORDER_TYPES = {
  MARKET: 'market',
  LIMIT: 'limit',
  STOP_LOSS: 'stop_loss',
}

export const TRADE_ACTIONS = {
  BUY: 'buy',
  SELL: 'sell',
}

export const SYSTEM_STATUS = {
  INITIALIZING: 'initializing',
  READY: 'ready',
  ACTIVE: 'active',
  ERROR: 'error',
  MAINTENANCE: 'maintenance',
}

export const API_ENDPOINTS = {
  HEALTH: '/health',
  STATUS: '/api/status',
  MARKET: '/api/market',
  TRADE: '/api/trade',
  QUANTUM: '/api/quantum',
}

export const REFRESH_INTERVALS = {
  DASHBOARD: 30000,
  MARKET_DATA: 5000,
  TRADES: 2000,
}
