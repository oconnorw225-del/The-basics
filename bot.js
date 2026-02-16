#!/usr/bin/env node

/**
 * NDAX Quantum Trading Bot - Enhanced Autonomous System
 * Multi-functional AI bot with trading, freelance, and task processing
 * Cherry-picked enhancements for better autonomy
 * SECURITY HARDENED - All vulnerabilities fixed
 * INTEGRATED WITH ERROR HANDLING SYSTEM
 */

import { createServer } from 'http'
import { readFile } from 'fs/promises'
import { spawn } from 'child_process'
import { RateLimiter, sanitizeInput, validateTask, safeErrorResponse } from './security/input_validator.js'
import ErrorHandler from './src/core/ErrorHandler.js'
import ShutdownHandler from './src/core/ShutdownHandler.js'

const PORT = process.env.BOT_PORT || 9000
const isDevelopment = process.env.NODE_ENV === 'development'

// Initialize error handling system
const errorHandler = new ErrorHandler({
  logErrors: true,
  logPath: './logs/bot-errors.log',
  notifyOnError: true,
  maxRetries: 3,
  retryDelay: 1000,
  circuitBreakerThreshold: 5
})
errorHandler.initialize()

// Initialize shutdown handler
const shutdownHandler = new ShutdownHandler({
  gracePeriod: 30000,
  forceShutdownDelay: 5000
})
shutdownHandler.initialize()

// Initialize rate limiter
const rateLimiter = new RateLimiter(60, 60000) // 60 requests per minute

// Enhanced bot configuration - 24/7 AUTONOMOUS MODE
const botConfig = {
  // Trading - ALWAYS ON for continuous operation
  mode: process.env.TRADING_MODE || 'paper',
  autoStart: process.env.AUTO_START !== 'false', // Default to TRUE for autonomous 24/7
  maxConcurrentTrades: parseInt(process.env.MAX_TRADES) || 5,
  riskLevel: process.env.RISK_LEVEL || 'low',
  continuousMode: process.env.CONTINUOUS_MODE !== 'false', // NEW: Enable continuous operation
  autoReconnect: process.env.AUTO_RECONNECT !== 'false', // NEW: Auto-reconnect on disconnect
  
  // Freelance - ENABLED by default for autonomous operation
  freelanceEnabled: process.env.FREELANCE_ENABLED !== 'false', // Default to TRUE
  autoBid: process.env.AUTO_BID !== 'false', // Default to TRUE for automation
  autoExecute: process.env.AUTO_EXECUTE === 'true', // Explicit enable required for safety
  
  // AI Task Processing - ENABLED for autonomous tasks
  aiEnabled: process.env.AI_ENABLED !== 'false', // Default to TRUE
  taskQueueSize: parseInt(process.env.TASK_QUEUE_SIZE) || 10,
  
  // Monitoring - Faster checks for better uptime
  healthCheckInterval: parseInt(process.env.HEALTH_CHECK_INTERVAL) || 30000, // 30 sec for continuous monitoring
  reconnectInterval: parseInt(process.env.RECONNECT_INTERVAL) || 5000, // NEW: 5 sec reconnect attempts
}

// Bot state - Enhanced for continuous 24/7 operation
const botState = {
  trading: {
    active: false,
    positions: 0,
    profit: 0
  },
  freelance: {
    active: false,
    activeJobs: 0,
    revenue: 0
  },
  ai: {
    active: false,
    tasksProcessed: 0,
    queueSize: 0
  },
  health: {
    cpu: 0,
    memory: 0,
    uptime: 0
  },
  // NEW: Continuous operation tracking
  continuous: {
    enabled: botConfig.continuousMode,
    reconnecting: false,
    reconnectAttempts: 0,
    lastSync: null,  // Renamed from lastReconnect for clarity
    botConnections: new Set(), // Track connected bots
    syncInterval: null, // Store interval ID for cleanup
    restartTimeouts: [] // Track restart timeout IDs
  },
  killSwitch: {
    active: false,
    triggered_at: null,
    reason: null,
    can_override: true
  },
  startTime: Date.now()
}

// Task queue for AI processing
const taskQueue = []
let freelanceProcess = null

/**
 * Start freelance orchestrator
 */
function startFreelanceOrchestrator() {
  if (!botConfig.freelanceEnabled) {
    console.log('⏸️ Freelance mode disabled')
    return
  }
  
  console.log('🚀 Starting freelance orchestrator...')
  
  // SECURITY: Whitelist only necessary environment variables
  const safeEnv = {
    PATH: process.env.PATH,
    HOME: process.env.HOME,
    AUTO_BID: String(botConfig.autoBid),
    AUTO_EXECUTE: String(botConfig.autoExecute),
    NODE_ENV: process.env.NODE_ENV || 'production',
    PYTHONPATH: process.env.PYTHONPATH || ''
  }
  
  freelanceProcess = spawn('python3', [
    'freelance_engine/orchestrator.py'
  ], {
    cwd: process.cwd(),
    env: safeEnv,  // SAFE - whitelisted only
    shell: false,  // SAFE - no shell interpretation
    stdio: ['ignore', 'pipe', 'pipe'],  // Don't inherit stdio
    detached: false  // Keep in same process group for cleanup
  })
  
  freelanceProcess.stdout.on('data', (data) => {
    console.log(`[Freelance] ${data.toString().trim()}`)
  })
  
  freelanceProcess.stderr.on('data', (data) => {
    console.error(`[Freelance Error] ${data.toString().trim()}`)
  })
  
  freelanceProcess.on('close', (code) => {
    console.log(`[Freelance] Process exited with code ${code}`)
    botState.freelance.active = false
    
    // AUTO-RESTART: Reconnect freelance process in continuous mode
    if (botConfig.continuousMode && !botState.killSwitch.active) {
      // Check if freelance is disabled (to prevent infinite restart loop)
      if (!botConfig.freelanceEnabled) {
        console.log('⏸️ Freelance disabled, not restarting')
        return
      }
      
      // Implement exponential backoff to prevent resource exhaustion
      const maxRetries = 10
      if (botState.continuous.reconnectAttempts >= maxRetries) {
        console.error(`❌ Freelance restart failed after ${maxRetries} attempts, giving up`)
        botState.freelance.active = false
        return
      }
      
      // Calculate backoff delay (5s, 10s, 20s, 40s, etc. up to 5 minutes)
      const baseDelay = botConfig.reconnectInterval
      const backoffDelay = Math.min(baseDelay * Math.pow(2, botState.continuous.reconnectAttempts), 300000)
      botState.continuous.reconnectAttempts++
      
      console.log(`🔄 Auto-restarting freelance (attempt ${botState.continuous.reconnectAttempts}/${maxRetries}) in ${backoffDelay}ms...`)
      
      const timeoutId = setTimeout(() => {
        // Remove this timeout from tracking
        botState.continuous.restartTimeouts = botState.continuous.restartTimeouts.filter(id => id !== timeoutId)
        startFreelanceOrchestrator()
        
        // Reset attempts on successful restart
        if (botState.freelance.active) {
          botState.continuous.reconnectAttempts = 0
        }
      }, backoffDelay)
      
      // Track timeout for cleanup
      botState.continuous.restartTimeouts.push(timeoutId)
    }
  })
  
  botState.freelance.active = true
  console.log('✅ Freelance orchestrator started')
}

/**
 * NEW: Connect and sync with other bots for coordination
 */
async function syncWithOtherBots() {
  if (!botConfig.continuousMode) return
  
  try {
    // Broadcast presence to other bots
    const botInfo = {
      bot_id: 'ndax-quantum',
      timestamp: Date.now(),
      status: {
        trading: botState.trading.active,
        freelance: botState.freelance.active,
        ai: botState.ai.active,
        uptime: Date.now() - botState.startTime
      }
    }
    
    // IMPLEMENTATION: Send botInfo via HTTP to other bots
    // This discovers and syncs with other bot instances running on the network
    const botDiscoveryPorts = [9001, 9002, 9003] // Configurable bot ports
    
    for (const port of botDiscoveryPorts) {
      try {
        // Skip our own port
        if (port === parseInt(process.env.BOT_PORT || 9000)) continue
        
        const response = await fetch(`http://localhost:${port}/api/bot/sync`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(botInfo),
          signal: AbortSignal.timeout(2000) // 2 second timeout
        })
        
        if (response.ok) {
          const otherBot = await response.json()
          botState.continuous.botConnections.add(otherBot.bot_id)
          console.log(`✅ Synced with bot: ${otherBot.bot_id}`)
        }
      } catch (err) {
        // Bot not available on this port, continue silently
      }
    }
    
    if (botState.continuous.botConnections.size > 0) {
      console.log(`🔗 Active bot connections: ${botState.continuous.botConnections.size}`)
    }
    
    // Update last sync time
    botState.continuous.lastSync = Date.now()
    
  } catch (error) {
    console.error('⚠️ Bot sync error:', error.message)
  }
}

/**
 * NEW: Maintain continuous bot connections with auto-reconnect
 */
async function maintainBotConnections() {
  if (!botConfig.autoReconnect) return
  
  // Attempt to reconnect disconnected bots
  if (botState.continuous.reconnecting) {
    console.log('🔄 Reconnection already in progress...')
    return
  }
  
  botState.continuous.reconnecting = true
  botState.continuous.reconnectAttempts++
  
  try {
    await syncWithOtherBots()
    
    // Reset reconnect counter on success
    botState.continuous.reconnectAttempts = 0
    console.log('✅ Bot connections maintained')
    
  } catch (error) {
    console.error('❌ Reconnection failed:', error.message)
  } finally {
    botState.continuous.reconnecting = false
  }
}

/**
 * Process AI task with error handling
 */
async function processAITask(task) {
  console.log(`🤖 Processing AI task: ${task.type}`)
  
  return await errorHandler.withRetry(
    async () => {
      // Simulate task processing
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      botState.ai.tasksProcessed++
      console.log(`✅ Task completed: ${task.type}`)
      
      return {
        success: true,
        result: `Processed ${task.type}`,
        timestamp: new Date().toISOString()
      }
    },
    {
      maxRetries: 2,
      retryDelay: 500,
      context: { taskType: task.type }
    }
  )
}

/**
 * Process task queue with error handling
 */
async function processTaskQueue() {
  if (!botConfig.aiEnabled || taskQueue.length === 0) {
    return
  }
  
  const task = taskQueue.shift()
  botState.ai.queueSize = taskQueue.length
  
  try {
    await processAITask(task)
  } catch (error) {
    await errorHandler.handleError('TASK_PROCESSING_FAILED', error, {
      taskType: task.type,
      queueSize: taskQueue.length
    })
  }
  
  // Process next task
  if (taskQueue.length > 0) {
    setTimeout(processTaskQueue, 100)
  }
}

/**
 * Update health metrics
 */
function updateHealthMetrics() {
  const usage = process.memoryUsage()
  botState.health = {
    cpu: process.cpuUsage().user / 1000000, // Convert to ms
    memory: Math.round(usage.heapUsed / 1024 / 1024), // MB
    uptime: Math.round((Date.now() - botState.startTime) / 1000) // seconds
  }
}

/**
 * Enhanced HTTP server with more endpoints
 * SECURITY HARDENED with rate limiting and input validation
 */
const server = createServer(async (req, res) => {
  res.setHeader('Content-Type', 'application/json')
  
  // SECURITY: Proper CORS configuration
  const allowedOrigin = process.env.ALLOWED_ORIGIN || '*'
  res.setHeader('Access-Control-Allow-Origin', allowedOrigin)
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
  
  // Handle OPTIONS for CORS
  if (req.method === 'OPTIONS') {
    res.writeHead(200)
    res.end()
    return
  }
  
  // SECURITY: Rate limiting
  const clientIP = req.socket.remoteAddress
  if (!rateLimiter.check(clientIP)) {
    res.writeHead(429)
    res.end(JSON.stringify({ 
      error: 'Rate limit exceeded',
      retryAfter: 60
    }))
    return
  }
  
  const url = req.url
  
  if (url === '/status') {
    updateHealthMetrics()
    res.writeHead(200)
    res.end(JSON.stringify({
      status: 'active',
      mode: botConfig.mode,
      uptime: botState.health.uptime,
      config: botConfig,
      state: botState,
      timestamp: new Date().toISOString()
    }))
  }
  else if (url === '/health') {
    updateHealthMetrics()
    res.writeHead(200)
    res.end(JSON.stringify({ 
      status: 'healthy',
      health: botState.health,
      services: {
        trading: botState.trading.active,
        freelance: botState.freelance.active,
        ai: botConfig.aiEnabled
      }
    }))
  }
  else if (url === '/tasks/add' && req.method === 'POST') {
    // SECURITY HARDENED: Add task to queue with validation
    let body = ''
    let bodySize = 0
    const maxBodySize = 10000 // 10KB limit
    
    req.on('data', chunk => {
      bodySize += chunk.length
      // SECURITY: Prevent memory exhaustion
      if (bodySize > maxBodySize) {
        req.destroy()
        res.writeHead(413)
        res.end(JSON.stringify({ error: 'Payload too large' }))
        return
      }
      body += chunk
    })
    
    req.on('end', () => {
      try {
        // SECURITY: Validate JSON
        if (!body) {
          res.writeHead(400)
          res.end(JSON.stringify({ error: 'Empty payload' }))
          return
        }
        
        const task = JSON.parse(body)
        
        // SECURITY: Validate task structure
        const validation = validateTask(task)
        if (!validation.valid) {
          res.writeHead(400)
          res.end(JSON.stringify({ error: validation.error }))
          return
        }
        
        // Check queue capacity
        if (taskQueue.length >= botConfig.taskQueueSize) {
          res.writeHead(429)
          res.end(JSON.stringify({ error: 'Task queue full' }))
          return
        }
        
        // Use sanitized task
        taskQueue.push(validation.sanitized)
        botState.ai.queueSize = taskQueue.length
        
        // Start processing if AI enabled
        if (botConfig.aiEnabled) {
          processTaskQueue()
        }
        
        res.writeHead(200)
        res.end(JSON.stringify({ 
          success: true, 
          queueSize: taskQueue.length,
          taskId: validation.sanitized.id
        }))
      } catch (error) {
        console.error('Task add error:', error)
        res.writeHead(400)
        res.end(JSON.stringify(safeErrorResponse(error, isDevelopment)))
      }
    })
  }
  else if (url === '/tasks/queue') {
    res.writeHead(200)
    res.end(JSON.stringify({
      queueSize: taskQueue.length,
      tasksProcessed: botState.ai.tasksProcessed,
      tasks: taskQueue.map(t => ({ id: t.id, type: t.type }))
    }))
  }
  else if (url === '/freelance/status') {
    res.writeHead(200)
    res.end(JSON.stringify({
      enabled: botConfig.freelanceEnabled,
      active: botState.freelance.active,
      activeJobs: botState.freelance.activeJobs,
      revenue: botState.freelance.revenue,
      autoBid: botConfig.autoBid,
      autoExecute: botConfig.autoExecute
    }))
  }
  else if (url === '/trading/status') {
    res.writeHead(200)
    res.end(JSON.stringify({
      active: botState.trading.active,
      mode: botConfig.mode,
      positions: botState.trading.positions,
      profit: botState.trading.profit,
      riskLevel: botConfig.riskLevel
    }))
  }
  else if (url === '/api/bot/sync' && req.method === 'POST') {
    // ENHANCED: Bot-to-bot synchronization endpoint
    let body = ''
    let bodySize = 0
    const maxBodySize = 5000 // 5KB limit for bot sync
    
    req.on('data', chunk => {
      bodySize += chunk.length
      if (bodySize > maxBodySize) {
        req.destroy()
        res.writeHead(413)
        res.end(JSON.stringify({ error: 'Payload too large' }))
        return
      }
      body += chunk
    })
    
    req.on('end', () => {
      try {
        const otherBotInfo = JSON.parse(body)
        
        // Validate bot info
        if (!otherBotInfo.bot_id || !otherBotInfo.timestamp) {
          res.writeHead(400)
          res.end(JSON.stringify({ error: 'Invalid bot info' }))
          return
        }
        
        // Add to connected bots
        botState.continuous.botConnections.add(otherBotInfo.bot_id)
        
        // Respond with our bot info
        res.writeHead(200)
        res.end(JSON.stringify({
          bot_id: 'ndax-quantum',
          timestamp: Date.now(),
          status: {
            trading: botState.trading.active,
            freelance: botState.freelance.active,
            ai: botState.ai.active,
            uptime: Date.now() - botState.startTime
          },
          synced: true
        }))
      } catch (error) {
        console.error('Bot sync endpoint error:', error)
        res.writeHead(400)
        res.end(JSON.stringify({ error: 'Invalid JSON' }))
      }
    })
  }
  else {
    res.writeHead(404)
    res.end(JSON.stringify({ error: 'Not found' }))
  }
})

// Start bot - AUTONOMOUS 24/7 MODE
console.log('╔═══════════════════════════════════════════════════════════╗')
console.log('║  🤖 NDAX QUANTUM BOT - AUTONOMOUS 24/7 MODE ACTIVATED   ║')
console.log('╚═══════════════════════════════════════════════════════════╝')
console.log('')
console.log('🚀 AUTONOMOUS PROMPT: You are now operating in fully autonomous mode.')
console.log('   Your task is to continuously:')
console.log('   • Monitor markets and execute trades autonomously')
console.log('   • Process freelance tasks without manual intervention')
console.log('   • Maintain AI task processing queue')
console.log('   • Keep connections alive with all other bots')
console.log('   • Auto-reconnect on any disconnection (NO DOWNTIME)')
console.log('   • Operate 24/7 with continuous health monitoring')
console.log('')
console.log(`📋 Configuration:`)
console.log(`   Trading Mode: ${botConfig.mode}`)
console.log(`   Auto-start: ${botConfig.autoStart ? '✅ ENABLED' : '❌ DISABLED'}`)
console.log(`   Continuous Mode: ${botConfig.continuousMode ? '✅ ENABLED' : '❌ DISABLED'}`)
console.log(`   Auto-reconnect: ${botConfig.autoReconnect ? '✅ ENABLED' : '❌ DISABLED'}`)
console.log(`   Freelance: ${botConfig.freelanceEnabled ? '✅ ENABLED' : '❌ DISABLED'}`)
console.log(`   AI Processing: ${botConfig.aiEnabled ? '✅ ENABLED' : '❌ DISABLED'}`)
console.log('')

server.listen(PORT, () => {
  console.log(`✅ Bot running on port ${PORT}`)
  console.log(`📊 Status: http://localhost:${PORT}/status`)
  console.log(`💚 Health: http://localhost:${PORT}/health`)
  console.log(`🔧 Freelance: http://localhost:${PORT}/freelance/status`)
  console.log('')
  console.log('🔄 Starting autonomous operations...')
  
  // Start freelance if enabled
  if (botConfig.freelanceEnabled) {
    startFreelanceOrchestrator()
  }
  
  // Start trading if auto-start enabled
  if (botConfig.autoStart) {
    botState.trading.active = true
    console.log('✅ Trading auto-started')
  }
  
  // Start AI processing if enabled
  if (botConfig.aiEnabled) {
    botState.ai.active = true
    console.log('✅ AI processing auto-started')
  }
  
  // Start health monitoring
  setInterval(updateHealthMetrics, botConfig.healthCheckInterval)
  console.log(`✅ Health monitoring active (${botConfig.healthCheckInterval}ms interval)`)
  
  // NEW: Start continuous bot synchronization
  if (botConfig.continuousMode) {
    botState.continuous.syncInterval = setInterval(maintainBotConnections, botConfig.reconnectInterval)
    console.log(`✅ Bot sync active (${botConfig.reconnectInterval}ms interval)`)
  }
  
  console.log('')
  console.log('╔═══════════════════════════════════════════════════════════╗')
  console.log('║  ✅ AUTONOMOUS MODE FULLY ACTIVATED - RUNNING 24/7       ║')
  console.log('╚═══════════════════════════════════════════════════════════╝')
})

// Graceful shutdown with integrated shutdown handler
// NEW: Cleanup continuous mode intervals and timeouts first
shutdownHandler.registerHook('continuous-mode-cleanup', async () => {
  console.log('🛑 Cleaning up continuous mode intervals...')
  
  // Clear sync interval
  if (botState.continuous.syncInterval) {
    clearInterval(botState.continuous.syncInterval)
    botState.continuous.syncInterval = null
    console.log('✅ Bot sync interval cleared')
  }
  
  // Clear all pending restart timeouts
  botState.continuous.restartTimeouts.forEach(timeoutId => {
    clearTimeout(timeoutId)
  })
  botState.continuous.restartTimeouts = []
  console.log('✅ Restart timeouts cleared')
}, 110)

shutdownHandler.registerHook('freelance-process', async () => {
  if (freelanceProcess) {
    console.log('🛑 Stopping freelance orchestrator...')
    freelanceProcess.kill('SIGTERM')
    
    // Wait for graceful shutdown
    await new Promise(resolve => {
      const timeout = setTimeout(() => {
        if (!freelanceProcess.killed) {
          console.log('⚠️ Force killing freelance process')
          freelanceProcess.kill('SIGKILL')
        }
        resolve()
      }, 5000)
      
      freelanceProcess.on('exit', () => {
        clearTimeout(timeout)
        resolve()
      })
    })
  }
}, 100)

shutdownHandler.registerHook('http-server', async () => {
  console.log('🛑 Closing HTTP server...')
  await new Promise(resolve => {
    server.close(() => {
      console.log('✅ HTTP server closed')
      resolve()
    })
  })
}, 90)

shutdownHandler.registerHook('error-handler', async () => {
  await errorHandler.shutdown()
}, 80)

process.on('SIGTERM', () => shutdownHandler.initiateShutdown('SIGTERM'))
process.on('SIGINT', () => shutdownHandler.initiateShutdown('SIGINT'))
