/**
 * Main Integration Entry Point
 * Demonstrates integration of all core systems
 */

import FeatureManager from './FeatureManager.js';
import ErrorHandler from './ErrorHandler.js';
import HealthMonitor from './HealthMonitor.js';
import ProcessLinker from './ProcessLinker.js';
import ShutdownHandler from './ShutdownHandler.js';
import { readFile } from 'fs/promises';

// Load configuration
let config;
try {
  const configData = await readFile('./config/error-handling.json', 'utf8');
  config = JSON.parse(configData);
} catch (error) {
  console.error('Failed to load configuration:', error.message);
  config = {
    errorHandler: {},
    healthMonitor: {},
    shutdownHandler: {},
    features: {}
  };
}

// Initialize core systems
console.log('🚀 Initializing core systems...\n');

const errorHandler = new ErrorHandler(config.errorHandler);
const featureManager = new FeatureManager(config.features);
const healthMonitor = new HealthMonitor(config.healthMonitor);
const processLinker = new ProcessLinker();
const shutdownHandler = new ShutdownHandler(config.shutdownHandler);

// Initialize error handler first
errorHandler.initialize();

// Initialize shutdown handler
shutdownHandler.initialize();

// Setup system-wide error handling integration
featureManager.on('featureError', async ({ name, error }) => {
  await errorHandler.handleError('FEATURE_ERROR', error, { feature: name });
});

healthMonitor.on('unhealthy', async (metrics) => {
  await errorHandler.handleError(
    'SYSTEM_UNHEALTHY',
    new Error('System health check failed'),
    { metrics }
  );
});

healthMonitor.on('memoryLeak', async ({ current, history }) => {
  await errorHandler.handleError(
    'MEMORY_LEAK',
    new Error('Memory leak detected'),
    { current, history }
  );
});

// Setup shutdown hooks
shutdownHandler.registerHook('health-monitor', async () => {
  await healthMonitor.shutdown();
}, 100);

shutdownHandler.registerHook('feature-manager', async () => {
  await featureManager.shutdown();
}, 90);

shutdownHandler.registerHook('process-linker', async () => {
  await processLinker.shutdown();
}, 80);

shutdownHandler.registerHook('error-handler', async () => {
  await errorHandler.shutdown();
}, 70);

// Example feature classes
class DatabaseFeature {
  constructor(config) {
    this.config = config;
    this.connected = false;
  }

  async initialize() {
    console.log('📦 Initializing database...');
    // Simulate initialization
    await this.sleep(100);
  }

  async start() {
    console.log('🚀 Starting database connection...');
    this.connected = true;
    await this.sleep(100);
  }

  async stop() {
    console.log('🛑 Closing database connection...');
    this.connected = false;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

class AIFeature {
  constructor(config) {
    this.config = config;
    this.running = false;
  }

  async initialize() {
    console.log('📦 Initializing AI orchestrator...');
    await this.sleep(100);
  }

  async start() {
    console.log('🚀 Starting AI processing...');
    this.running = true;
  }

  async stop() {
    console.log('🛑 Stopping AI processing...');
    this.running = false;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

class FreelanceFeature {
  constructor(config) {
    this.config = config;
    this.running = false;
  }

  async initialize() {
    console.log('📦 Initializing freelance engine...');
    await this.sleep(100);
  }

  async start() {
    console.log('🚀 Starting freelance operations...');
    this.running = true;
  }

  async stop() {
    console.log('🛑 Stopping freelance operations...');
    this.running = false;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

class DashboardFeature {
  constructor(config) {
    this.config = config;
    this.server = null;
  }

  async initialize() {
    console.log('📦 Initializing dashboard...');
    await this.sleep(100);
  }

  async start() {
    console.log('🚀 Starting dashboard server...');
    this.server = { listening: true };
  }

  async stop() {
    console.log('🛑 Stopping dashboard server...');
    if (this.server) {
      this.server.listening = false;
    }
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Register features
console.log('\n📦 Registering features...\n');

featureManager.registerFeature('database', DatabaseFeature, {
  enabled: config.features.database?.enabled ?? true,
  critical: config.features.database?.critical ?? true,
  dependencies: [],
  autoStart: true,
  config: {}
});

featureManager.registerFeature('ai', AIFeature, {
  enabled: config.features.ai?.enabled ?? true,
  critical: config.features.ai?.critical ?? true,
  dependencies: [],
  autoStart: true,
  config: {}
});

featureManager.registerFeature('freelance', FreelanceFeature, {
  enabled: config.features.freelance?.enabled ?? true,
  critical: config.features.freelance?.critical ?? false,
  dependencies: ['ai'],
  autoStart: true,
  config: {}
});

featureManager.registerFeature('dashboard', DashboardFeature, {
  enabled: config.features.dashboard?.enabled ?? true,
  critical: config.features.dashboard?.critical ?? false,
  dependencies: ['database'],
  autoStart: true,
  config: {}
});

// Start the system
async function startSystem() {
  try {
    console.log('\n🚀 Starting system...\n');

    // Initialize all features
    await featureManager.initializeAll();

    // Link all processes
    console.log('\n🔗 Linking processes...\n');
    await processLinker.link(featureManager.getAllFeatures());

    // Start health monitoring
    console.log('\n🏥 Starting health monitor...\n');
    healthMonitor.start();

    // Start all features
    await featureManager.startAll();

    console.log('\n✅ System started successfully!\n');

    // Display system status
    displayStatus();

    // Setup periodic status display
    setInterval(() => {
      console.log('\n' + '='.repeat(60));
      displayStatus();
    }, 30000); // Every 30 seconds

  } catch (error) {
    console.error('\n❌ Failed to start system:', error.message);
    await errorHandler.handleError('STARTUP_FAILED', error);
    process.exit(1);
  }
}

function displayStatus() {
  console.log('\n📊 System Status:');
  console.log('─'.repeat(60));

  // Feature status
  const health = featureManager.getSystemHealth();
  console.log(`\n🔧 Features: ${health.summary.running}/${health.summary.enabled} running`);
  Object.entries(health.features).forEach(([name, status]) => {
    const icon = status.running ? '✅' : status.enabled ? '⏸️' : '⏹️';
    const healthIcon = status.healthy ? '💚' : '💔';
    console.log(`  ${icon} ${healthIcon} ${name.padEnd(15)} - ${status.running ? 'Running' : 'Stopped'}`);
  });

  // Health monitor status
  const healthStatus = healthMonitor.getStatus();
  console.log(`\n🏥 Health Monitor:`);
  console.log(`  Status: ${healthStatus.healthy ? '✅ Healthy' : '⚠️ Unhealthy'}`);
  console.log(`  Uptime: ${Math.floor(healthStatus.uptime / 1000)}s`);
  console.log(`  Memory: ${healthStatus.metrics.memoryUsagePercent.toFixed(2)}%`);
  console.log(`  Event Loop Lag: ${healthStatus.metrics.eventLoop.lag}ms`);

  // Error handler stats
  const errorStats = errorHandler.getStats();
  console.log(`\n⚠️ Error Statistics:`);
  console.log(`  Total Errors: ${errorStats.totalErrors}`);
  console.log(`  Recovered: ${errorStats.recoveredErrors}`);
  console.log(`  Fatal: ${errorStats.fatalErrors}`);

  // Process linker status
  const services = processLinker.getAllServices();
  const connections = processLinker.getAllConnections();
  console.log(`\n🔗 Process Linker:`);
  console.log(`  Services: ${Object.keys(services).length}`);
  console.log(`  Connections: ${connections.length}`);

  console.log('\n' + '─'.repeat(60));
}

// Start the system
startSystem().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});

// Export for use in other modules
export {
  errorHandler,
  featureManager,
  healthMonitor,
  processLinker,
  shutdownHandler
};
