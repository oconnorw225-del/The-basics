/**
 * Validate email address
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate trade amount
 */
export const isValidTradeAmount = (amount, min = 0, max = Infinity) => {
  const numAmount = parseFloat(amount)
  return !isNaN(numAmount) && numAmount >= min && numAmount <= max
}

/**
 * Validate API key format
 */
export const isValidApiKey = (key) => {
  return typeof key === 'string' && key.length >= 32
}

/**
 * Sanitize input
 */
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input
  return input.replace(/[<>]/g, '')
}

/**
 * Validate trading pair
 */
export const isValidTradingPair = (pair) => {
  const pairRegex = /^[A-Z]{2,6}\/[A-Z]{2,6}$/
  return pairRegex.test(pair)
}
