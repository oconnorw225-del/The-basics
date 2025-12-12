/**
 * Input Validation and Sanitization Utilities
 * Protects against injection attacks and malformed input
 */

/**
 * Sanitize string input based on type
 * @param {string} input - Input to sanitize
 * @param {string} type - Type of sanitization
 * @returns {string} Sanitized input
 */
export function sanitizeInput(input, type = 'string') {
  if (typeof input !== 'string') {
    return ''
  }
  
  switch (type) {
    case 'alphanumeric':
      return input.replace(/[^a-zA-Z0-9_-]/g, '')
    
    case 'numeric':
      return input.replace(/[^0-9]/g, '')
    
    case 'email':
      // Basic email sanitization
      return input.toLowerCase().replace(/[^a-z0-9@._-]/g, '')
    
    case 'url':
      // Allow only safe URL characters
      return input.replace(/[^a-zA-Z0-9:/.?&=_-]/g, '')
    
    case 'path':
      // Remove path traversal attempts
      return input
        .replace(/\.\./g, '')
        .replace(/[^a-zA-Z0-9/_.-]/g, '')
    
    default:
      // Remove control characters and potential XSS
      return input
        .replace(/[\x00-\x1F\x7F]/g, '')
        .replace(/<script[^>]*>.*?<\/script>/gi, '')
        .replace(/javascript:/gi, '')
        .replace(/on\w+\s*=/gi, '')
  }
}

/**
 * Validate JSON payload size and structure
 * @param {string} body - JSON string
 * @param {number} maxSize - Maximum size in bytes
 * @returns {object} Parsed JSON or null
 */
export function validateJSON(body, maxSize = 10000) {
  if (!body || body.length > maxSize) {
    return { error: 'Payload too large or empty', valid: false }
  }
  
  try {
    const parsed = JSON.parse(body)
    return { data: parsed, valid: true }
  } catch (error) {
    return { error: 'Invalid JSON', valid: false }
  }
}

/**
 * Validate task object structure
 * @param {object} task - Task object to validate
 * @returns {object} Validation result
 */
export function validateTask(task) {
  if (!task || typeof task !== 'object') {
    return { valid: false, error: 'Task must be an object' }
  }
  
  // Required fields
  if (!task.type || typeof task.type !== 'string') {
    return { valid: false, error: 'Task type is required' }
  }
  
  // Sanitize task type
  const sanitizedType = sanitizeInput(task.type, 'alphanumeric')
  
  if (!sanitizedType) {
    return { valid: false, error: 'Invalid task type' }
  }
  
  // Whitelist allowed task types
  const allowedTypes = [
    'code_review', 'data_processing', 'api_call', 
    'file_operation', 'calculation', 'validation'
  ]
  
  if (!allowedTypes.includes(sanitizedType)) {
    return { valid: false, error: 'Unknown task type' }
  }
  
  return {
    valid: true,
    sanitized: {
      ...task,
      type: sanitizedType,
      id: task.id || Date.now().toString()
    }
  }
}

/**
 * Simple rate limiter
 */
export class RateLimiter {
  constructor(maxRequests = 60, windowMs = 60000) {
    this.maxRequests = maxRequests
    this.windowMs = windowMs
    this.requests = new Map()
  }
  
  /**
   * Check if request should be allowed
   * @param {string} identifier - Client identifier (IP, user ID, etc.)
   * @returns {boolean} True if allowed
   */
  check(identifier) {
    const now = Date.now()
    const requests = this.requests.get(identifier) || []
    
    // Remove old requests outside the window
    const recent = requests.filter(time => now - time < this.windowMs)
    
    // Check if limit exceeded
    if (recent.length >= this.maxRequests) {
      return false
    }
    
    // Add new request
    recent.push(now)
    this.requests.set(identifier, recent)
    
    // Cleanup old entries periodically
    if (Math.random() < 0.01) {
      this.cleanup()
    }
    
    return true
  }
  
  /**
   * Clean up old entries
   */
  cleanup() {
    const now = Date.now()
    for (const [key, requests] of this.requests.entries()) {
      const recent = requests.filter(time => now - time < this.windowMs)
      if (recent.length === 0) {
        this.requests.delete(key)
      } else {
        this.requests.set(key, recent)
      }
    }
  }
  
  /**
   * Get remaining requests for identifier
   * @param {string} identifier - Client identifier
   * @returns {number} Remaining requests
   */
  remaining(identifier) {
    const now = Date.now()
    const requests = this.requests.get(identifier) || []
    const recent = requests.filter(time => now - time < this.windowMs)
    return Math.max(0, this.maxRequests - recent.length)
  }
}

/**
 * Validate environment variables
 * @param {Array<string>} required - Required environment variables
 * @throws {Error} If required variables are missing
 */
export function validateEnvironment(required = []) {
  const missing = required.filter(key => !process.env[key])
  
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`)
  }
  
  // Check for dangerous default values
  const dangerous = ['test', 'demo', 'changeme', 'password', 'secret', '12345']
  
  for (const key of required) {
    const value = process.env[key]
    if (dangerous.some(d => value.toLowerCase().includes(d))) {
      console.warn(`⚠️ Warning: Environment variable ${key} may contain unsafe default value`)
    }
  }
}

/**
 * Safe error response - hides details in production
 * @param {Error} error - Error object
 * @param {boolean} isDevelopment - Development mode flag
 * @returns {object} Safe error response
 */
export function safeErrorResponse(error, isDevelopment = false) {
  if (isDevelopment) {
    return {
      error: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    }
  }
  
  // Production: generic error
  return {
    error: 'Internal server error',
    timestamp: new Date().toISOString()
  }
}

export default {
  sanitizeInput,
  validateJSON,
  validateTask,
  RateLimiter,
  validateEnvironment,
  safeErrorResponse
}
