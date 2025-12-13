/**
 * Format currency values
 */
export const formatCurrency = (value, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(value)
}

/**
 * Format percentage values
 */
export const formatPercentage = (value, decimals = 2) => {
  return `${value.toFixed(decimals)}%`
}

/**
 * Format large numbers
 */
export const formatNumber = (value, decimals = 2) => {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(decimals)}M`
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(decimals)}K`
  }
  return value.toFixed(decimals)
}

/**
 * Format timestamp
 */
export const formatTimestamp = timestamp => {
  const date = new Date(timestamp)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Debounce function
 */
export const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Throttle function
 */
export const throttle = (func, limit) => {
  let inThrottle
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}
