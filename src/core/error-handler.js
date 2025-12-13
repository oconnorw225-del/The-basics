/**
 * error-handler.js - Global Error Handler and Crash Recovery
 * 
 * Provides comprehensive error handling, crash recovery, and auto-restart capabilities
 * for The-basics trading and AI platform system.
 */

const fs = require('fs');
const path = require('path');
const { EventEmitter } = require('events');

class ErrorHandler extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.options = {
      logDir: options.logDir || path.join(process.cwd(), '.unified-system', 'logs'),
      maxLogSize: options.maxLogSize || 10 * 1024 * 1024, // 10MB
      maxLogFiles: options.maxLogFiles || 5,
      enableAutoRestart: options.enableAutoRestart !== false,
      restartDelay: options.restartDelay || 5000,
      criticalErrorThreshold: options.criticalErrorThreshold || 5,
      alertWebhook: options.alertWebhook || null,
      ...options
    };
    
    this.errorCount = 0;
    this.criticalErrorCount = 0;
    this.lastRestart = null;
    this.isShuttingDown = false;
    
    this.init();
  }
  
  init() {
    // Ensure log directory exists
    if (!fs.existsSync(this.options.logDir)) {
      fs.mkdirSync(this.options.logDir, { recursive: true });
    }
    
    // Setup global error handlers
    this.setupGlobalHandlers();
    
    // Setup log rotation
    this.setupLogRotation();
    
    console.log('[ErrorHandler] Initialized with auto-restart:', this.options.enableAutoRestart);
  }
  
  setupGlobalHandlers() {
    // Uncaught exceptions
    process.on('uncaughtException', (error) => {
      this.handleCriticalError('uncaughtException', error);
    });
    
    // Unhandled promise rejections
    process.on('unhandledRejection', (reason, promise) => {
      this.handleCriticalError('unhandledRejection', reason);
    });
    
    // SIGTERM - graceful shutdown
    process.on('SIGTERM', () => {
      this.handleShutdown('SIGTERM');
    });
    
    // SIGINT - Ctrl+C
    process.on('SIGINT', () => {
      this.handleShutdown('SIGINT');
    });
    
    // Warning events
    process.on('warning', (warning) => {
      this.logWarning(warning);
    });
  }
  
  handleCriticalError(type, error) {
    this.criticalErrorCount++;
    
    const errorInfo = {
      type,
      message: error?.message || String(error),
      stack: error?.stack,
      timestamp: new Date().toISOString(),
      processUptime: process.uptime(),
      memoryUsage: process.memoryUsage(),
      pid: process.pid
    };
    
    // Log the error
    this.logError(errorInfo);
    
    // Emit event for listeners
    this.emit('criticalError', errorInfo);
    
    // Send alert if configured
    if (this.options.alertWebhook) {
      this.sendAlert(errorInfo).catch(console.error);
    }
    
    // Check if we should restart
    if (this.shouldRestart()) {
      this.scheduleRestart(errorInfo);
    } else {
      console.error('[ErrorHandler] Critical error threshold exceeded. Exiting...');
      process.exit(1);
    }
  }
  
  handleShutdown(signal) {
    if (this.isShuttingDown) return;
    
    this.isShuttingDown = true;
    console.log(`[ErrorHandler] Received ${signal}. Starting graceful shutdown...`);
    
    this.emit('shutdown', signal);
    
    // Give processes time to clean up
    setTimeout(() => {
      console.log('[ErrorHandler] Shutdown complete.');
      process.exit(0);
    }, 3000);
  }
  
  shouldRestart() {
    if (!this.options.enableAutoRestart) return false;
    if (this.criticalErrorCount >= this.options.criticalErrorThreshold) return false;
    
    // Prevent restart loops - check if last restart was recent
    if (this.lastRestart) {
      const timeSinceRestart = Date.now() - this.lastRestart;
      if (timeSinceRestart < 30000) { // 30 seconds
        console.error('[ErrorHandler] Recent restart detected. Not restarting to prevent loop.');
        return false;
      }
    }
    
    return true;
  }
  
  scheduleRestart(errorInfo) {
    console.log(`[ErrorHandler] Scheduling restart in ${this.options.restartDelay}ms...`);
    
    this.emit('beforeRestart', errorInfo);
    
    setTimeout(() => {
      this.lastRestart = Date.now();
      console.log('[ErrorHandler] Restarting process...');
      
      // Spawn new process
      const { spawn } = require('child_process');
      const child = spawn(process.argv[0], process.argv.slice(1), {
        detached: true,
        stdio: 'inherit'
      });
      
      child.unref();
      process.exit(0);
    }, this.options.restartDelay);
  }
  
  logError(errorInfo) {
    const logFile = path.join(this.options.logDir, 'errors.log');
    const logEntry = JSON.stringify(errorInfo, null, 2) + '\n---\n';
    
    try {
      fs.appendFileSync(logFile, logEntry);
      console.error('[ErrorHandler] Error logged:', errorInfo.type, errorInfo.message);
    } catch (err) {
      console.error('[ErrorHandler] Failed to write error log:', err);
    }
  }
  
  logWarning(warning) {
    const logFile = path.join(this.options.logDir, 'warnings.log');
    const logEntry = `[${new Date().toISOString()}] ${warning.name}: ${warning.message}\n`;
    
    try {
      fs.appendFileSync(logFile, logEntry);
    } catch (err) {
      console.error('[ErrorHandler] Failed to write warning log:', err);
    }
  }
  
  setupLogRotation() {
    // Rotate logs if they exceed max size
    const rotateLog = (logFile) => {
      try {
        if (!fs.existsSync(logFile)) return;
        
        const stats = fs.statSync(logFile);
        if (stats.size > this.options.maxLogSize) {
          // Rotate existing logs
          for (let i = this.options.maxLogFiles - 1; i > 0; i--) {
            const oldFile = `${logFile}.${i}`;
            const newFile = `${logFile}.${i + 1}`;
            if (fs.existsSync(oldFile)) {
              fs.renameSync(oldFile, newFile);
            }
          }
          
          // Move current log to .1
          fs.renameSync(logFile, `${logFile}.1`);
          console.log(`[ErrorHandler] Rotated log file: ${path.basename(logFile)}`);
        }
      } catch (err) {
        console.error('[ErrorHandler] Log rotation failed:', err);
      }
    };
    
    // Check log rotation every hour
    setInterval(() => {
      rotateLog(path.join(this.options.logDir, 'errors.log'));
      rotateLog(path.join(this.options.logDir, 'warnings.log'));
    }, 3600000);
  }
  
  async sendAlert(errorInfo) {
    if (!this.options.alertWebhook) return;
    
    try {
      const response = await fetch(this.options.alertWebhook, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: `🚨 Critical Error in The-basics System`,
          attachments: [{
            color: 'danger',
            fields: [
              { title: 'Type', value: errorInfo.type, short: true },
              { title: 'Time', value: errorInfo.timestamp, short: true },
              { title: 'Message', value: errorInfo.message, short: false },
              { title: 'PID', value: String(errorInfo.pid), short: true },
              { title: 'Uptime', value: `${Math.floor(errorInfo.processUptime)}s`, short: true }
            ]
          }]
        })
      });
      
      if (!response.ok) {
        console.error('[ErrorHandler] Alert webhook failed:', response.statusText);
      }
    } catch (err) {
      console.error('[ErrorHandler] Failed to send alert:', err);
    }
  }
  
  /**
   * Graceful degradation - disable non-critical features
   */
  degradeGracefully(features = []) {
    console.log('[ErrorHandler] Entering graceful degradation mode...');
    console.log('[ErrorHandler] Disabling features:', features);
    
    this.emit('degradation', features);
    
    // Log degradation
    const logFile = path.join(this.options.logDir, 'degradation.log');
    const logEntry = `[${new Date().toISOString()}] Degraded features: ${features.join(', ')}\n`;
    fs.appendFileSync(logFile, logEntry);
  }
  
  /**
   * Manual error reporting
   */
  reportError(context, error, severity = 'error') {
    this.errorCount++;
    
    const errorInfo = {
      context,
      severity,
      message: error?.message || String(error),
      stack: error?.stack,
      timestamp: new Date().toISOString()
    };
    
    if (severity === 'critical') {
      this.handleCriticalError(context, error);
    } else {
      this.logError(errorInfo);
      this.emit('error', errorInfo);
    }
  }
  
  /**
   * Get error statistics
   */
  getStats() {
    return {
      totalErrors: this.errorCount,
      criticalErrors: this.criticalErrorCount,
      lastRestart: this.lastRestart,
      uptime: process.uptime(),
      memoryUsage: process.memoryUsage()
    };
  }
}

// Singleton instance
let instance = null;

module.exports = {
  ErrorHandler,
  getInstance: (options) => {
    if (!instance) {
      instance = new ErrorHandler(options);
    }
    return instance;
  },
  createHandler: (options) => new ErrorHandler(options)
};
