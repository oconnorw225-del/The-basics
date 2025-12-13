/**
 * freeze-detector.js - Watchdog Timer and Deadlock Detection
 * 
 * Monitors system health, detects freezes and deadlocks, and triggers
 * auto-reload when necessary for The-basics system.
 */

const EventEmitter = require('events');
const os = require('os');
const v8 = require('v8');

class FreezeDetector extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.options = {
      heartbeatInterval: options.heartbeatInterval || 5000,        // 5 seconds
      freezeThreshold: options.freezeThreshold || 30000,           // 30 seconds
      memoryLeakThreshold: options.memoryLeakThreshold || 0.9,     // 90% of heap
      cpuThreshold: options.cpuThreshold || 0.95,                  // 95% CPU
      checkInterval: options.checkInterval || 10000,               // 10 seconds
      enableAutoReload: options.enableAutoReload !== false,
      healthCheckTimeout: options.healthCheckTimeout || 5000,
      ...options
    };
    
    this.lastHeartbeat = Date.now();
    this.isRunning = false;
    this.healthChecks = new Map();
    this.memoryHistory = [];
    this.maxMemoryHistorySize = 20;
    this.frozenComponents = new Set();
    
    this.heapStats = {
      initial: null,
      current: null,
      trend: 'stable'
    };
  }
  
  start() {
    if (this.isRunning) {
      console.log('[FreezeDetector] Already running');
      return;
    }
    
    this.isRunning = true;
    this.lastHeartbeat = Date.now();
    this.heapStats.initial = v8.getHeapStatistics();
    
    // Start watchdog timer
    this.watchdogTimer = setInterval(() => {
      this.checkHealth();
    }, this.options.checkInterval);
    
    // Start heartbeat
    this.heartbeatTimer = setInterval(() => {
      this.heartbeat();
    }, this.options.heartbeatInterval);
    
    // Start memory monitoring
    this.memoryTimer = setInterval(() => {
      this.checkMemory();
    }, 30000); // Check every 30 seconds
    
    console.log('[FreezeDetector] Started monitoring');
    this.emit('started');
  }
  
  stop() {
    this.isRunning = false;
    
    if (this.watchdogTimer) clearInterval(this.watchdogTimer);
    if (this.heartbeatTimer) clearInterval(this.heartbeatTimer);
    if (this.memoryTimer) clearInterval(this.memoryTimer);
    
    console.log('[FreezeDetector] Stopped monitoring');
    this.emit('stopped');
  }
  
  heartbeat() {
    this.lastHeartbeat = Date.now();
  }
  
  checkHealth() {
    const now = Date.now();
    const timeSinceHeartbeat = now - this.lastHeartbeat;
    
    // Check for freeze
    if (timeSinceHeartbeat > this.options.freezeThreshold) {
      this.handleFreeze(timeSinceHeartbeat);
      return;
    }
    
    // Check registered health checks
    this.runHealthChecks();
    
    // Check CPU usage
    this.checkCPU();
    
    // Emit health status
    this.emit('health', this.getHealthStatus());
  }
  
  handleFreeze(duration) {
    const freezeInfo = {
      duration,
      timestamp: new Date().toISOString(),
      memoryUsage: process.memoryUsage(),
      cpuUsage: process.cpuUsage(),
      uptime: process.uptime()
    };
    
    console.error('[FreezeDetector] System freeze detected!', freezeInfo);
    this.emit('freeze', freezeInfo);
    
    if (this.options.enableAutoReload) {
      console.log('[FreezeDetector] Triggering auto-reload...');
      this.emit('autoReload', freezeInfo);
      
      // Give a chance for cleanup
      setTimeout(() => {
        process.exit(2); // Exit code 2 for freeze
      }, 2000);
    }
  }
  
  checkMemory() {
    const heapStats = v8.getHeapStatistics();
    const memUsage = process.memoryUsage();
    
    this.heapStats.current = heapStats;
    
    const heapUsed = heapStats.used_heap_size;
    const heapLimit = heapStats.heap_size_limit;
    const heapPercent = heapUsed / heapLimit;
    
    // Track memory history
    this.memoryHistory.push({
      timestamp: Date.now(),
      heapUsed,
      heapPercent,
      rss: memUsage.rss
    });
    
    if (this.memoryHistory.length > this.maxMemoryHistorySize) {
      this.memoryHistory.shift();
    }
    
    // Detect memory leak
    if (heapPercent > this.options.memoryLeakThreshold) {
      this.handleMemoryLeak(heapStats, memUsage);
    }
    
    // Analyze memory trend
    this.analyzeMemoryTrend();
    
    this.emit('memoryCheck', {
      heapUsed,
      heapLimit,
      heapPercent,
      trend: this.heapStats.trend,
      rss: memUsage.rss
    });
  }
  
  analyzeMemoryTrend() {
    if (this.memoryHistory.length < 5) {
      this.heapStats.trend = 'unknown';
      return;
    }
    
    const recent = this.memoryHistory.slice(-5);
    const increases = recent.reduce((count, curr, idx) => {
      if (idx === 0) return count;
      return count + (curr.heapPercent > recent[idx - 1].heapPercent ? 1 : 0);
    }, 0);
    
    if (increases >= 4) {
      this.heapStats.trend = 'increasing';
      
      // Check if consistently increasing
      const firstPercent = recent[0].heapPercent;
      const lastPercent = recent[recent.length - 1].heapPercent;
      const increaseRate = (lastPercent - firstPercent) / firstPercent;
      
      if (increaseRate > 0.1) { // 10% increase
        console.warn('[FreezeDetector] Potential memory leak detected - consistent growth');
        this.emit('potentialMemoryLeak', {
          increaseRate,
          history: recent
        });
      }
    } else if (increases <= 1) {
      this.heapStats.trend = 'decreasing';
    } else {
      this.heapStats.trend = 'stable';
    }
  }
  
  handleMemoryLeak(heapStats, memUsage) {
    const leakInfo = {
      heapUsed: heapStats.used_heap_size,
      heapLimit: heapStats.heap_size_limit,
      heapPercent: heapStats.used_heap_size / heapStats.heap_size_limit,
      rss: memUsage.rss,
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
    };
    
    console.error('[FreezeDetector] Memory leak detected!', leakInfo);
    this.emit('memoryLeak', leakInfo);
    
    // Try to force garbage collection if available
    if (global.gc) {
      console.log('[FreezeDetector] Forcing garbage collection...');
      global.gc();
    }
    
    // If still over threshold after GC, consider reloading
    setTimeout(() => {
      const newStats = v8.getHeapStatistics();
      const newPercent = newStats.used_heap_size / newStats.heap_size_limit;
      
      if (newPercent > this.options.memoryLeakThreshold && this.options.enableAutoReload) {
        console.error('[FreezeDetector] Memory still critical after GC. Triggering reload...');
        this.emit('autoReload', leakInfo);
        process.exit(3); // Exit code 3 for memory leak
      }
    }, 5000);
  }
  
  checkCPU() {
    const cpus = os.cpus();
    const avgLoad = os.loadavg()[0] / cpus.length; // 1-minute average normalized
    
    if (avgLoad > this.options.cpuThreshold) {
      const cpuInfo = {
        avgLoad,
        threshold: this.options.cpuThreshold,
        cpuCount: cpus.length,
        timestamp: new Date().toISOString()
      };
      
      console.warn('[FreezeDetector] High CPU usage detected', cpuInfo);
      this.emit('highCPU', cpuInfo);
    }
  }
  
  /**
   * Register a health check function
   */
  registerHealthCheck(name, checkFn, timeout = null) {
    this.healthChecks.set(name, {
      fn: checkFn,
      timeout: timeout || this.options.healthCheckTimeout,
      lastCheck: null,
      lastStatus: null
    });
    
    console.log(`[FreezeDetector] Registered health check: ${name}`);
  }
  
  /**
   * Unregister a health check
   */
  unregisterHealthCheck(name) {
    this.healthChecks.delete(name);
    console.log(`[FreezeDetector] Unregistered health check: ${name}`);
  }
  
  /**
   * Run all registered health checks
   */
  async runHealthChecks() {
    for (const [name, check] of this.healthChecks.entries()) {
      try {
        // Create a timeout promise
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Health check timeout')), check.timeout);
        });
        
        // Race between health check and timeout
        const result = await Promise.race([
          Promise.resolve(check.fn()),
          timeoutPromise
        ]);
        
        check.lastCheck = Date.now();
        check.lastStatus = 'healthy';
        
        this.frozenComponents.delete(name);
        
      } catch (error) {
        check.lastCheck = Date.now();
        check.lastStatus = 'unhealthy';
        
        console.error(`[FreezeDetector] Health check failed: ${name}`, error.message);
        
        this.frozenComponents.add(name);
        this.emit('unhealthy', { name, error: error.message });
        
        // Check for deadlock
        if (this.frozenComponents.size > this.healthChecks.size / 2) {
          this.handleDeadlock();
        }
      }
    }
  }
  
  handleDeadlock() {
    const deadlockInfo = {
      frozenComponents: Array.from(this.frozenComponents),
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
    };
    
    console.error('[FreezeDetector] Deadlock detected!', deadlockInfo);
    this.emit('deadlock', deadlockInfo);
    
    if (this.options.enableAutoReload) {
      console.log('[FreezeDetector] Triggering auto-reload due to deadlock...');
      this.emit('autoReload', deadlockInfo);
      process.exit(4); // Exit code 4 for deadlock
    }
  }
  
  getHealthStatus() {
    const now = Date.now();
    const heapStats = v8.getHeapStatistics();
    
    return {
      healthy: this.frozenComponents.size === 0,
      uptime: process.uptime(),
      lastHeartbeat: this.lastHeartbeat,
      timeSinceHeartbeat: now - this.lastHeartbeat,
      frozenComponents: Array.from(this.frozenComponents),
      healthChecks: Array.from(this.healthChecks.entries()).map(([name, check]) => ({
        name,
        lastCheck: check.lastCheck,
        status: check.lastStatus
      })),
      memory: {
        heapUsed: heapStats.used_heap_size,
        heapLimit: heapStats.heap_size_limit,
        heapPercent: heapStats.used_heap_size / heapStats.heap_size_limit,
        trend: this.heapStats.trend
      }
    };
  }
  
  /**
   * Get statistics
   */
  getStats() {
    return {
      isRunning: this.isRunning,
      healthStatus: this.getHealthStatus(),
      memoryHistory: this.memoryHistory.slice(-10),
      heapStats: this.heapStats
    };
  }
}

// Singleton instance
let instance = null;

module.exports = {
  FreezeDetector,
  getInstance: (options) => {
    if (!instance) {
      instance = new FreezeDetector(options);
    }
    return instance;
  },
  createDetector: (options) => new FreezeDetector(options)
};
