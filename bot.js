#!/usr/bin/env node

/**
 * NDAX Quantum Trading Bot - Enhanced Autonomous System
 * Multi-functional AI bot with trading, freelance, and task processing
 * Cherry-picked enhancements for better autonomy
 */

import { createServer } from 'http'
import { readFile } from 'fs/promises'
import { spawn } from 'child_process'

const PORT = process.env.BOT_PORT || 9000

// Enhanced bot configuration
const botConfig = {
  // Trading
  mode: process.env.TRADING_MODE || 'paper',
  autoStart: process.env.AUTO_START === 'true',
  maxConcurrentTrades: parseInt(process.env.MAX_TRADES) || 5,
  riskLevel: process.env.RISK_LEVEL || 'low',
  
  // Freelance
  freelanceEnabled: process.env.FREELANCE_ENABLED === 'true',
  autoBid: process.env.AUTO_BID === 'true',
  autoExecute: process.env.AUTO_EXECUTE === 'false', // Safety: off by default
  
  // AI Task Processing
  aiEnabled: process.env.AI_ENABLED === 'true',
  taskQueueSize: parseInt(process.env.TASK_QUEUE_SIZE) || 10,
  
  // Monitoring
  healthCheckInterval: parseInt(process.env.HEALTH_CHECK_INTERVAL) || 60000, // 1 min
}

// Bot state
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
  
  freelanceProcess = spawn('python3', [
    'freelance_engine/orchestrator.py'
  ], {
    cwd: process.cwd(),
    env: {
      ...process.env,
      AUTO_BID: botConfig.autoBid,
      AUTO_EXECUTE: botConfig.autoExecute
    }
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
  })
  
  botState.freelance.active = true
  console.log('✅ Freelance orchestrator started')
}

/**
 * Process AI task
 */
async function processAITask(task) {
  console.log(`🤖 Processing AI task: ${task.type}`)
  
  // Simulate task processing
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  botState.ai.tasksProcessed++
  console.log(`✅ Task completed: ${task.type}`)
  
  return {
    success: true,
    result: `Processed ${task.type}`,
    timestamp: new Date().toISOString()
  }
}

/**
 * Process task queue
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
    console.error(`❌ Task failed: ${error.message}`)
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
 */
const server = createServer(async (req, res) => {
  res.setHeader('Content-Type', 'application/json')
  res.setHeader('Access-Control-Allow-Origin', '*')
  
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
    // Add task to queue
    let body = ''
    req.on('data', chunk => body += chunk)
    req.on('end', () => {
      try {
        const task = JSON.parse(body)
        
        if (taskQueue.length >= botConfig.taskQueueSize) {
          res.writeHead(429)
          res.end(JSON.stringify({ error: 'Task queue full' }))
          return
        }
        
        taskQueue.push(task)
        botState.ai.queueSize = taskQueue.length
        
        // Start processing if AI enabled
        if (botConfig.aiEnabled) {
          processTaskQueue()
        }
        
        res.writeHead(200)
        res.end(JSON.stringify({ 
          success: true, 
          queueSize: taskQueue.length,
          taskId: task.id || Date.now()
        }))
      } catch (error) {
        res.writeHead(400)
        res.end(JSON.stringify({ error: 'Invalid task format' }))
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
  else {
    res.writeHead(404)
    res.end(JSON.stringify({ error: 'Not found' }))
  }
})

// Start bot
console.log('🤖 NDAX Enhanced Autonomous Bot starting...')
console.log(`Trading Mode: ${botConfig.mode}`)
console.log(`Auto-start: ${botConfig.autoStart}`)
console.log(`Freelance: ${botConfig.freelanceEnabled ? 'Enabled' : 'Disabled'}`)
console.log(`AI Processing: ${botConfig.aiEnabled ? 'Enabled' : 'Disabled'}`)

server.listen(PORT, () => {
  console.log(`✅ Bot running on port ${PORT}`)
  console.log(`📊 Status: http://localhost:${PORT}/status`)
  console.log(`💚 Health: http://localhost:${PORT}/health`)
  console.log(`🔧 Freelance: http://localhost:${PORT}/freelance/status`)
  
  // Start freelance if enabled
  if (botConfig.freelanceEnabled) {
    startFreelanceOrchestrator()
  }
  
  // Start health monitoring
  setInterval(updateHealthMetrics, botConfig.healthCheckInterval)
})

// Graceful shutdown
process.on('SIGTERM', shutdown)
process.on('SIGINT', shutdown)

function shutdown() {
  console.log('🛑 Bot shutting down...')
  
  // Stop freelance orchestrator
  if (freelanceProcess) {
    console.log('🛑 Stopping freelance orchestrator...')
    freelanceProcess.kill()
  }
  
  server.close(() => {
    console.log('✅ Bot stopped gracefully')
    process.exit(0)
  })
}
