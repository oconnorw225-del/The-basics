/**
 * Comprehensive Error Handler System
 * Handles all types of errors, crashes, and provides recovery strategies
 */

import { EventEmitter } from 'events';
import { appendFile } from 'fs/promises';
import { mkdir } from 'fs/promises';
import { dirname } from 'path';

class ErrorHandler extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      logErrors: config.logErrors ?? true,
      logPath: config.logPath ?? './logs/errors.log',
      notifyOnError: config.notifyOnError ?? true,
      notifyWebhook: config.notifyWebhook ?? '',
      maxRetries: config.maxRetries ?? 3,
      retryDelay: config.retryDelay ?? 1000,
      circuitBreakerThreshold: config.circuitBreakerThreshold ?? 5,
      fatalErrorExitDelay: config.fatalErrorExitDelay ?? 1000
    };

    // Circuit breaker state for external services
    this.circuitBreakers = new Map();
    
    // Error statistics
    this.stats = {
      totalErrors: 0,
      uncaughtExceptions: 0,
      unhandledRejections: 0,
      apiErrors: 0,
      databaseErrors: 0,
      recoveredErrors: 0,
      fatalErrors: 0
    };

    // Active retry operations
    this.retryOperations = new Map();
    
    this.initialized = false;
  }

  /**
   * Initialize error handlers
   */
  initialize() {
    if (this.initialized) {
      return;
    }

    // Handle uncaught exceptions
    process.on('uncaughtException', (error) => {
      this.handleUncaughtException(error);
    });

    // Handle unhandled promise rejections
    process.on('unhandledRejection', (reason, promise) => {
      this.handleUnhandledRejection(reason, promise);
    });

    // Handle warnings
    process.on('warning', (warning) => {
      this.handleWarning(warning);
    });

    this.initialized = true;
    this.emit('initialized');
    console.log('✅ ErrorHandler initialized');
  }

  /**
   * Handle uncaught exceptions
   */
  async handleUncaughtException(error) {
    this.stats.uncaughtExceptions++;
    this.stats.totalErrors++;
    this.stats.fatalErrors++;

    await this.logError('UNCAUGHT_EXCEPTION', error, {
      fatal: true,
      stack: error.stack
    });

    this.emit('uncaughtException', error);

    // Give time for cleanup before exit
    console.error('💥 FATAL: Uncaught exception:', error);
    console.error(`Process will exit in ${this.config.fatalErrorExitDelay}ms...`);
    
    setTimeout(() => {
      process.exit(1);
    }, this.config.fatalErrorExitDelay);
  }

  /**
   * Handle unhandled promise rejections
   */
  async handleUnhandledRejection(reason, promise) {
    this.stats.unhandledRejections++;
    this.stats.totalErrors++;

    const error = reason instanceof Error ? reason : new Error(String(reason));
    
    await this.logError('UNHANDLED_REJECTION', error, {
      promise: promise.toString(),
      reason: String(reason)
    });

    this.emit('unhandledRejection', { reason, promise });
    
    console.error('⚠️ Unhandled promise rejection:', reason);
  }

  /**
   * Handle warnings
   */
  async handleWarning(warning) {
    await this.logError('WARNING', warning, {
      name: warning.name,
      message: warning.message
    });

    this.emit('warning', warning);
  }

  /**
   * Handle API errors with retry logic
   */
  async handleApiError(error, context = {}) {
    this.stats.apiErrors++;
    this.stats.totalErrors++;

    const serviceName = context.service || 'unknown';
    
    await this.logError('API_ERROR', error, context);

    // Check circuit breaker
    if (this.isCircuitOpen(serviceName)) {
      console.warn(`⚡ Circuit breaker OPEN for ${serviceName}`);
      throw new Error(`Service ${serviceName} is temporarily unavailable`);
    }

    // Record failure
    this.recordServiceFailure(serviceName);

    this.emit('apiError', { error, context });
    
    return error;
  }

  /**
   * Handle database errors
   */
  async handleDatabaseError(error, context = {}) {
    this.stats.databaseErrors++;
    this.stats.totalErrors++;

    await this.logError('DATABASE_ERROR', error, context);

    this.emit('databaseError', { error, context });
    
    return error;
  }

  /**
   * Handle file system errors
   */
  async handleFileSystemError(error, context = {}) {
    this.stats.totalErrors++;

    await this.logError('FILESYSTEM_ERROR', error, context);

    this.emit('fileSystemError', { error, context });
    
    return error;
  }

  /**
   * Handle configuration errors
   */
  async handleConfigError(error, context = {}) {
    this.stats.totalErrors++;

    await this.logError('CONFIG_ERROR', error, context);

    this.emit('configError', { error, context });
    
    return error;
  }

  /**
   * Generic error handler with recovery strategies
   */
  async handleError(type, error, context = {}) {
    this.stats.totalErrors++;

    await this.logError(type, error, context);

    this.emit('error', { type, error, context });
    
    return error;
  }

  /**
   * Execute operation with retry logic and exponential backoff
   */
  async withRetry(operation, options = {}) {
    const {
      maxRetries = this.config.maxRetries,
      retryDelay = this.config.retryDelay,
      onRetry = null,
      context = {}
    } = options;

    let lastError;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const result = await operation();
        
        if (attempt > 0) {
          this.stats.recoveredErrors++;
          console.log(`✅ Operation succeeded after ${attempt} retries`);
        }
        
        return result;
      } catch (error) {
        lastError = error;
        
        if (attempt < maxRetries) {
          const delay = retryDelay * Math.pow(2, attempt);
          console.warn(`⚠️ Attempt ${attempt + 1} failed, retrying in ${delay}ms...`);
          
          if (onRetry) {
            await onRetry(error, attempt);
          }
          
          await this.sleep(delay);
        }
      }
    }

    // All retries exhausted
    await this.handleError('RETRY_EXHAUSTED', lastError, {
      ...context,
      attempts: maxRetries + 1
    });
    
    throw lastError;
  }

  /**
   * Circuit breaker pattern for external services
   */
  isCircuitOpen(serviceName) {
    const breaker = this.circuitBreakers.get(serviceName);
    
    if (!breaker) {
      return false;
    }

    // Check if circuit should reset
    if (breaker.state === 'open' && Date.now() - breaker.openedAt > 60000) {
      breaker.state = 'half-open';
      breaker.failures = 0;
      console.log(`🔄 Circuit breaker for ${serviceName} entering HALF-OPEN state`);
    }

    return breaker.state === 'open';
  }

  /**
   * Record service failure for circuit breaker
   */
  recordServiceFailure(serviceName) {
    if (!this.circuitBreakers.has(serviceName)) {
      this.circuitBreakers.set(serviceName, {
        failures: 0,
        state: 'closed',
        openedAt: null
      });
    }

    const breaker = this.circuitBreakers.get(serviceName);
    breaker.failures++;

    if (breaker.failures >= this.config.circuitBreakerThreshold) {
      breaker.state = 'open';
      breaker.openedAt = Date.now();
      console.error(`⚡ Circuit breaker OPENED for ${serviceName} (${breaker.failures} failures)`);
      this.emit('circuitBreakerOpened', { serviceName, failures: breaker.failures });
    }
  }

  /**
   * Record service success for circuit breaker
   */
  recordServiceSuccess(serviceName) {
    const breaker = this.circuitBreakers.get(serviceName);
    
    if (breaker) {
      if (breaker.state === 'half-open') {
        breaker.state = 'closed';
        breaker.failures = 0;
        console.log(`✅ Circuit breaker CLOSED for ${serviceName}`);
        this.emit('circuitBreakerClosed', { serviceName });
      } else if (breaker.state === 'closed') {
        breaker.failures = Math.max(0, breaker.failures - 1);
      }
    }
  }

  /**
   * Log error to file and emit notification
   */
  async logError(type, error, context = {}) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      type,
      message: error.message || String(error),
      stack: error.stack,
      context,
      stats: { ...this.stats }
    };

    if (this.config.logErrors) {
      try {
        await mkdir(dirname(this.config.logPath), { recursive: true });
        await appendFile(
          this.config.logPath,
          JSON.stringify(logEntry, null, 2) + '\n',
          'utf8'
        );
      } catch (err) {
        console.error('Failed to write error log:', err);
      }
    }

    // Emit for external notification systems
    if (this.config.notifyOnError) {
      this.emit('errorLogged', logEntry);
    }

    return logEntry;
  }

  /**
   * Get error statistics
   */
  getStats() {
    return { ...this.stats };
  }

  /**
   * Reset error statistics
   */
  resetStats() {
    Object.keys(this.stats).forEach(key => {
      this.stats[key] = 0;
    });
  }

  /**
   * Get circuit breaker status
   */
  getCircuitBreakerStatus() {
    const status = {};
    
    this.circuitBreakers.forEach((breaker, serviceName) => {
      status[serviceName] = {
        state: breaker.state,
        failures: breaker.failures,
        openedAt: breaker.openedAt
      };
    });

    return status;
  }

  /**
   * Helper: sleep for specified milliseconds
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Clean shutdown
   */
  async shutdown() {
    console.log('🛑 ErrorHandler shutting down...');
    
    // Wait for any pending log writes
    await this.sleep(100);
    
    this.removeAllListeners();
    this.initialized = false;
    
    console.log('✅ ErrorHandler shut down');
  }
}

export default ErrorHandler;
