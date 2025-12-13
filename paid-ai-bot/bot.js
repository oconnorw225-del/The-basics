/**
 * Paid AI Bot - Main Server
 * Multi-provider AI task polling and distribution system
 * Integrates with Stripe for payment processing
 */

const express = require('express');
const { createServer } = require('http');
const { initializePayments, handleWebhook } = require('./payments');
const { processTask } = require('./huggingface');
const customQueue = require('./providers/customQueue');
const directClients = require('./providers/directClients');
const mturk = require('./providers/mturk');
const appen = require('./providers/appen');
const rapidapi = require('./providers/rapidapi');

const app = express();
const server = createServer(app);

// Configuration
const PORT = process.env.BOT_PORT || 9000;
const POLL_INTERVAL = parseInt(process.env.POLL_INTERVAL) || 30000; // 30 seconds default

// Middleware
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

// Simple API key authentication middleware
const authenticateApiKey = (req, res, next) => {
  // Skip auth for health check and webhook (webhook has its own verification)
  if (req.path === '/health' || req.path === '/webhook/stripe') {
    return next();
  }

  const apiKey = req.headers['x-api-key'] || req.query.api_key;
  const validApiKey = process.env.API_KEY;

  // If API_KEY is not configured, allow all requests (dev mode)
  if (!validApiKey) {
    console.warn('⚠️  API_KEY not configured - authentication disabled');
    return next();
  }

  if (!apiKey || apiKey !== validApiKey) {
    return res.status(401).json({ error: 'Unauthorized - Invalid API key' });
  }

  next();
};

// Apply authentication to all routes except health and webhook
app.use(authenticateApiKey);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    uptime: process.uptime(),
    providers: {
      customQueue: customQueue.isEnabled(),
      directClients: directClients.isEnabled(),
      mturk: mturk.isEnabled(),
      appen: appen.isEnabled(),
      rapidapi: rapidapi.isEnabled()
    },
    timestamp: new Date().toISOString()
  });
});

// Stripe webhook endpoint (raw body needed for signature verification)
app.post('/webhook/stripe', express.raw({ type: 'application/json', limit: '1mb' }), handleWebhook);

// Task submission endpoint
app.post('/api/tasks', async (req, res) => {
  try {
    const { task, provider, priority = 'normal' } = req.body;
    
    if (!task) {
      return res.status(400).json({ error: 'Task is required' });
    }

    // Route to appropriate provider
    let result;
    switch (provider) {
      case 'custom':
        result = await customQueue.submitTask(task, priority);
        break;
      case 'direct':
        result = await directClients.submitTask(task, priority);
        break;
      case 'mturk':
        result = await mturk.submitTask(task, priority);
        break;
      case 'appen':
        result = await appen.submitTask(task, priority);
        break;
      case 'rapidapi':
        result = await rapidapi.submitTask(task, priority);
        break;
      default:
        // Auto-select best available provider
        result = await selectBestProvider(task, priority);
    }

    res.json({ success: true, result });
  } catch (error) {
    console.error('Task submission error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get task status
app.get('/api/tasks/:taskId', async (req, res) => {
  try {
    const { taskId } = req.params;
    const status = await getTaskStatus(taskId);
    res.json(status);
  } catch (error) {
    console.error('Task status error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Provider status endpoint
app.get('/api/providers', (req, res) => {
  res.json({
    providers: [
      { name: 'customQueue', enabled: customQueue.isEnabled(), stats: customQueue.getStats() },
      { name: 'directClients', enabled: directClients.isEnabled(), stats: directClients.getStats() },
      { name: 'mturk', enabled: mturk.isEnabled(), stats: mturk.getStats() },
      { name: 'appen', enabled: appen.isEnabled(), stats: appen.getStats() },
      { name: 'rapidapi', enabled: rapidapi.isEnabled(), stats: rapidapi.getStats() }
    ]
  });
});

// Task processing queue
const taskQueue = [];
const processingTasks = new Map();

/**
 * Poll all enabled providers for new tasks
 */
async function pollProviders() {
  try {
    const providers = [
      { name: 'customQueue', module: customQueue },
      { name: 'directClients', module: directClients },
      { name: 'mturk', module: mturk },
      { name: 'appen', module: appen },
      { name: 'rapidapi', module: rapidapi }
    ];

    for (const provider of providers) {
      if (provider.module.isEnabled()) {
        try {
          const tasks = await provider.module.pollTasks();
          if (tasks && tasks.length > 0) {
            console.log(`[${provider.name}] Found ${tasks.length} new tasks`);
            tasks.forEach(task => {
              task.provider = provider.name;
              taskQueue.push(task);
            });
          }
        } catch (error) {
          console.error(`[${provider.name}] Poll error:`, error.message);
        }
      }
    }
  } catch (error) {
    console.error('Provider polling error:', error);
  }
}

/**
 * Process tasks from the queue
 */
async function processTaskQueue() {
  while (taskQueue.length > 0) {
    const task = taskQueue.shift();
    
    if (!task) continue;

    try {
      console.log(`Processing task ${task.id} from ${task.provider}`);
      processingTasks.set(task.id, { status: 'processing', startedAt: Date.now() });

      // Process with HuggingFace AI
      const result = await processTask(task);

      // Submit result back to provider
      const provider = getProviderModule(task.provider);
      await provider.submitResult(task.id, result);

      processingTasks.set(task.id, { 
        status: 'completed', 
        completedAt: Date.now(),
        result 
      });

      console.log(`Task ${task.id} completed successfully`);
    } catch (error) {
      console.error(`Task ${task.id} failed:`, error.message);
      processingTasks.set(task.id, { 
        status: 'failed', 
        failedAt: Date.now(),
        error: error.message 
      });
    }
  }
}

/**
 * Select best available provider for a task
 */
async function selectBestProvider(task, priority) {
  const providers = [
    customQueue,
    directClients,
    mturk,
    appen,
    rapidapi
  ].filter(p => p.isEnabled());

  if (providers.length === 0) {
    throw new Error('No providers available');
  }

  // Simple round-robin selection for now
  // Could be enhanced with load balancing, cost optimization, etc.
  const provider = providers[0];
  return await provider.submitTask(task, priority);
}

/**
 * Get task status
 */
async function getTaskStatus(taskId) {
  if (processingTasks.has(taskId)) {
    return processingTasks.get(taskId);
  }

  // Check all providers
  const providers = [customQueue, directClients, mturk, appen, rapidapi];
  for (const provider of providers) {
    if (provider.isEnabled()) {
      try {
        const status = await provider.getTaskStatus(taskId);
        if (status) return status;
      } catch (error) {
        // Continue checking other providers
      }
    }
  }

  return { status: 'not_found' };
}

/**
 * Get provider module by name
 */
function getProviderModule(name) {
  switch (name) {
    case 'customQueue': return customQueue;
    case 'directClients': return directClients;
    case 'mturk': return mturk;
    case 'appen': return appen;
    case 'rapidapi': return rapidapi;
    default: throw new Error(`Unknown provider: ${name}`);
  }
}

/**
 * Initialize the bot
 */
async function initialize() {
  try {
    console.log('Initializing Paid AI Bot...');

    // Initialize payment system
    await initializePayments();
    console.log('✓ Payment system initialized');

    // Initialize providers
    await Promise.all([
      customQueue.initialize(),
      directClients.initialize(),
      mturk.initialize(),
      appen.initialize(),
      rapidapi.initialize()
    ]);
    console.log('✓ Providers initialized');

    // Start polling
    setInterval(pollProviders, POLL_INTERVAL);
    setInterval(processTaskQueue, 5000); // Process queue every 5 seconds
    console.log(`✓ Polling started (interval: ${POLL_INTERVAL}ms)`);

    // Start server
    server.listen(PORT, () => {
      console.log(`\n🤖 Paid AI Bot running on port ${PORT}`);
      console.log(`📊 Dashboard: http://localhost:${PORT}/health`);
      console.log(`💳 Stripe webhook: http://localhost:${PORT}/webhook/stripe`);
    });
  } catch (error) {
    console.error('Initialization error:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('Shutting down gracefully...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

// Start the bot
if (require.main === module) {
  initialize();
}

module.exports = { app, server, initialize };
