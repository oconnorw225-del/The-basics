/**
 * Health Monitor System
 * Detects freezes, memory leaks, and monitors system performance
 */

import { EventEmitter } from 'events'

class HealthMonitor extends EventEmitter {
  constructor(config = {}) {
    super()

    this.config = {
      heartbeatInterval: config.heartbeatInterval ?? 5000,
      memoryThreshold: config.memoryThreshold ?? 0.9,
      cpuThreshold: config.cpuThreshold ?? 0.8,
      checkInterval: config.checkInterval ?? 10000,
      autoRestart: config.autoRestart ?? true,
      maxRestarts: config.maxRestarts ?? 5,
      freezeTimeout: config.freezeTimeout ?? 30000,
      restartExitDelay: config.restartExitDelay ?? 1000,
    }

    this.state = {
      running: false,
      healthy: true,
      lastHeartbeat: Date.now(),
      restartCount: 0,
      startTime: Date.now(),
    }

    this.metrics = {
      cpu: { user: 0, system: 0 },
      memory: { heapUsed: 0, heapTotal: 0, external: 0, rss: 0 },
      eventLoop: { lag: 0 },
      uptime: 0,
    }

    this.baselineCpu = null
    this.baselineMemory = null
    this.memoryHistory = []
    this.maxMemoryHistorySize = 100

    this.intervals = {
      heartbeat: null,
      health: null,
      freeze: null,
    }

    this.frozenProcesses = new Set()
  }

  /**
   * Start health monitoring
   */
  start() {
    if (this.state.running) {
      console.log('⚠️ HealthMonitor already running')
      return
    }

    console.log('🏥 Starting health monitor...')
    this.state.running = true
    this.state.startTime = Date.now()

    // Start heartbeat monitoring
    this.startHeartbeat()

    // Start health checks
    this.startHealthChecks()

    // Start freeze detection
    this.startFreezeDetection()

    // Get baseline metrics
    this.updateBaseline()

    console.log('✅ HealthMonitor started')
    this.emit('started')
  }

  /**
   * Start heartbeat monitoring
   */
  startHeartbeat() {
    this.intervals.heartbeat = setInterval(() => {
      this.state.lastHeartbeat = Date.now()
      this.emit('heartbeat', { timestamp: this.state.lastHeartbeat })
    }, this.config.heartbeatInterval)
  }

  /**
   * Start health checks
   */
  startHealthChecks() {
    this.intervals.health = setInterval(() => {
      this.performHealthCheck()
    }, this.config.checkInterval)
  }

  /**
   * Start freeze detection
   */
  startFreezeDetection() {
    this.intervals.freeze = setInterval(() => {
      this.checkForFreeze()
    }, this.config.freezeTimeout)
  }

  /**
   * Perform comprehensive health check
   */
  async performHealthCheck() {
    try {
      // Update all metrics
      this.updateMetrics()

      // Check memory usage
      const memoryIssue = this.checkMemory()

      // Check CPU usage
      const cpuIssue = this.checkCPU()

      // Check event loop lag
      const eventLoopIssue = await this.checkEventLoop()

      // Determine overall health
      const wasHealthy = this.state.healthy
      this.state.healthy = !memoryIssue && !cpuIssue && !eventLoopIssue

      // Emit health check results
      this.emit('healthCheck', {
        healthy: this.state.healthy,
        metrics: this.getMetrics(),
        issues: {
          memory: memoryIssue,
          cpu: cpuIssue,
          eventLoop: eventLoopIssue,
        },
      })

      // Health state change
      if (wasHealthy && !this.state.healthy) {
        console.warn('⚠️ System became unhealthy')
        this.emit('unhealthy', this.getMetrics())

        if (this.config.autoRestart) {
          this.handleUnhealthyState()
        }
      } else if (!wasHealthy && this.state.healthy) {
        console.log('✅ System recovered')
        this.emit('recovered', this.getMetrics())
      }
    } catch (error) {
      console.error('❌ Health check error:', error)
      this.emit('error', error)
    }
  }

  /**
   * Update all metrics
   */
  updateMetrics() {
    // CPU metrics
    const cpuUsage = process.cpuUsage()
    this.metrics.cpu = cpuUsage

    // Memory metrics
    const memUsage = process.memoryUsage()
    this.metrics.memory = memUsage

    // Track memory history for leak detection
    this.memoryHistory.push({
      timestamp: Date.now(),
      heapUsed: memUsage.heapUsed,
      rss: memUsage.rss,
    })

    // Keep history size limited
    if (this.memoryHistory.length > this.maxMemoryHistorySize) {
      this.memoryHistory.shift()
    }

    // Uptime
    this.metrics.uptime = Date.now() - this.state.startTime
  }

  /**
   * Check memory usage
   */
  checkMemory() {
    const usage = this.metrics.memory
    const usagePercent = usage.heapUsed / usage.heapTotal

    if (usagePercent > this.config.memoryThreshold) {
      console.warn(`⚠️ High memory usage: ${(usagePercent * 100).toFixed(2)}%`)

      // Try garbage collection if available
      if (global.gc) {
        console.log('🗑️ Triggering garbage collection...')
        global.gc()
      }

      // Check for memory leak
      if (this.detectMemoryLeak()) {
        console.error('💧 Memory leak detected!')
        this.emit('memoryLeak', {
          current: usage.heapUsed,
          history: this.memoryHistory.slice(-10),
        })
        return 'memory_leak'
      }

      this.emit('highMemory', { usage: usagePercent })
      return 'high_memory'
    }

    return null
  }

  /**
   * Detect memory leaks by analyzing growth trend
   */
  detectMemoryLeak() {
    if (this.memoryHistory.length < 10) {
      return false
    }

    // Get last 10 readings
    const recent = this.memoryHistory.slice(-10)

    // Check if memory is consistently growing
    let growthCount = 0
    for (let i = 1; i < recent.length; i++) {
      if (recent[i].heapUsed > recent[i - 1].heapUsed) {
        growthCount++
      }
    }

    // If 8 out of 10 readings show growth, likely a leak
    const isLeaking = growthCount >= 8

    // Check growth rate
    const firstReading = recent[0].heapUsed
    const lastReading = recent[recent.length - 1].heapUsed
    const growthPercent = ((lastReading - firstReading) / firstReading) * 100

    // Alert if growing more than 20% in recent history
    return isLeaking && growthPercent > 20
  }

  /**
   * Check CPU usage
   */
  checkCPU() {
    if (!this.baselineCpu) {
      return null
    }

    const current = this.metrics.cpu
    const userDelta = (current.user - this.baselineCpu.user) / 1000000 // Convert to ms
    const systemDelta = (current.system - this.baselineCpu.system) / 1000000
    const totalCpu = userDelta + systemDelta
    const elapsedTime = this.config.checkInterval

    // Calculate CPU usage percentage
    const cpuPercent = totalCpu / elapsedTime

    if (cpuPercent > this.config.cpuThreshold) {
      console.warn(`⚠️ High CPU usage: ${(cpuPercent * 100).toFixed(2)}%`)
      this.emit('highCPU', { usage: cpuPercent })
      return 'high_cpu'
    }

    return null
  }

  /**
   * Check event loop lag
   */
  async checkEventLoop() {
    const start = Date.now()

    return new Promise(resolve => {
      setImmediate(() => {
        const lag = Date.now() - start
        this.metrics.eventLoop.lag = lag

        // Event loop lag > 100ms is concerning
        if (lag > 100) {
          console.warn(`⚠️ Event loop lag: ${lag}ms`)
          this.emit('eventLoopLag', { lag })
          resolve('event_loop_lag')
        } else {
          resolve(null)
        }
      })
    })
  }

  /**
   * Check for system freeze
   */
  checkForFreeze() {
    const now = Date.now()
    const timeSinceHeartbeat = now - this.state.lastHeartbeat

    if (timeSinceHeartbeat > this.config.freezeTimeout) {
      console.error(`💥 System freeze detected! No heartbeat for ${timeSinceHeartbeat}ms`)

      this.emit('freeze', {
        timeSinceHeartbeat,
        lastHeartbeat: this.state.lastHeartbeat,
      })

      if (this.config.autoRestart) {
        this.handleFreeze()
      }
    }
  }

  /**
   * Handle system freeze
   */
  handleFreeze() {
    console.error('🔄 Attempting to recover from freeze...')

    if (this.state.restartCount < this.config.maxRestarts) {
      this.state.restartCount++
      console.log(`Restart attempt ${this.state.restartCount}/${this.config.maxRestarts}`)

      this.emit('restarting', {
        reason: 'freeze',
        attempt: this.state.restartCount,
      })

      // Give other systems time to cleanup
      setTimeout(() => {
        process.exit(1)
      }, this.config.restartExitDelay)
    } else {
      console.error('❌ Max restart attempts reached, manual intervention required')
      this.emit('maxRestartsReached', { reason: 'freeze' })
    }
  }

  /**
   * Handle unhealthy state
   */
  handleUnhealthyState() {
    console.warn('🔄 System unhealthy, considering restart...')

    if (this.state.restartCount < this.config.maxRestarts) {
      this.state.restartCount++
      console.log(`Restart attempt ${this.state.restartCount}/${this.config.maxRestarts}`)

      this.emit('restarting', {
        reason: 'unhealthy',
        attempt: this.state.restartCount,
      })

      setTimeout(() => {
        process.exit(1)
      }, this.config.restartExitDelay)
    } else {
      console.error('❌ Max restart attempts reached')
      this.emit('maxRestartsReached', { reason: 'unhealthy' })
    }
  }

  /**
   * Update baseline metrics
   */
  updateBaseline() {
    this.baselineCpu = process.cpuUsage()
    this.baselineMemory = process.memoryUsage()
  }

  /**
   * Get current metrics
   */
  getMetrics() {
    return {
      ...this.metrics,
      memoryUsagePercent: (this.metrics.memory.heapUsed / this.metrics.memory.heapTotal) * 100,
      uptime: this.metrics.uptime,
      healthy: this.state.healthy,
      restartCount: this.state.restartCount,
    }
  }

  /**
   * Get health status
   */
  getStatus() {
    return {
      running: this.state.running,
      healthy: this.state.healthy,
      uptime: Date.now() - this.state.startTime,
      restartCount: this.state.restartCount,
      lastHeartbeat: this.state.lastHeartbeat,
      metrics: this.getMetrics(),
    }
  }

  /**
   * Reset restart counter
   */
  resetRestartCounter() {
    this.state.restartCount = 0
    console.log('🔄 Restart counter reset')
  }

  /**
   * Stop health monitoring
   */
  stop() {
    if (!this.state.running) {
      console.log('⚠️ HealthMonitor not running')
      return
    }

    console.log('🛑 Stopping health monitor...')

    // Clear all intervals
    if (this.intervals.heartbeat) clearInterval(this.intervals.heartbeat)
    if (this.intervals.health) clearInterval(this.intervals.health)
    if (this.intervals.freeze) clearInterval(this.intervals.freeze)

    this.state.running = false
    this.emit('stopped')

    console.log('✅ HealthMonitor stopped')
  }

  /**
   * Graceful shutdown
   */
  async shutdown() {
    console.log('🛑 HealthMonitor shutting down...')

    this.stop()
    this.removeAllListeners()

    console.log('✅ HealthMonitor shut down')
  }
}

export default HealthMonitor
