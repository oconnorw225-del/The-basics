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

/**
 * Format relative time (e.g., "5 minutes ago", "2 hours ago")
 * Note: Uses 30-day month approximation for simplicity
 */
export const formatRelativeTime = timestamp => {
  const now = Date.now()
  const date = timestamp instanceof Date ? timestamp.getTime() : timestamp
  const diffInSeconds = Math.floor((now - date) / 1000)

  // Handle future timestamps
  if (diffInSeconds < 0) {
    return 'in the future'
  }

  if (diffInSeconds < 60) {
    return diffInSeconds <= 1 ? 'just now' : `${diffInSeconds} seconds ago`
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60)
  if (diffInMinutes < 60) {
    return diffInMinutes === 1 ? '1 minute ago' : `${diffInMinutes} minutes ago`
  }

  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) {
    return diffInHours === 1 ? '1 hour ago' : `${diffInHours} hours ago`
  }

  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 30) {
    return diffInDays === 1 ? '1 day ago' : `${diffInDays} days ago`
  }

  const diffInMonths = Math.floor(diffInDays / 30)
  if (diffInMonths < 12) {
    return diffInMonths === 1 ? '1 month ago' : `${diffInMonths} months ago`
  }

  const diffInYears = Math.floor(diffInMonths / 12)
  return diffInYears === 1 ? '1 year ago' : `${diffInYears} years ago`
}
