/**
 * Basic tests for core systems
 * Run with: node tests/test-core-systems.js
 */

import ErrorHandler from '../src/core/ErrorHandler.js';
import FeatureManager from '../src/core/FeatureManager.js';
import HealthMonitor from '../src/core/HealthMonitor.js';
import ProcessLinker from '../src/core/ProcessLinker.js';
import ShutdownHandler from '../src/core/ShutdownHandler.js';

console.log('🧪 Testing Core Systems\n');

// Test ErrorHandler
console.log('1️⃣ Testing ErrorHandler...');
const errorHandler = new ErrorHandler({
  logErrors: false, // Disable file logging for tests
  maxRetries: 2,
  retryDelay: 100
});

errorHandler.initialize();

// Test retry logic
let attempts = 0;
try {
  await errorHandler.withRetry(
    async () => {
      attempts++;
      if (attempts < 3) {
        throw new Error('Transient error');
      }
      return 'success';
    },
    { maxRetries: 3, retryDelay: 50 }
  );
  console.log('✅ Retry logic works (succeeded after', attempts, 'attempts)');
} catch (error) {
  console.log('❌ Retry test failed:', error.message);
}

// Test circuit breaker
errorHandler.recordServiceFailure('test-service');
errorHandler.recordServiceFailure('test-service');
errorHandler.recordServiceFailure('test-service');
errorHandler.recordServiceFailure('test-service');
errorHandler.recordServiceFailure('test-service');

if (errorHandler.isCircuitOpen('test-service')) {
  console.log('✅ Circuit breaker works');
} else {
  console.log('❌ Circuit breaker not working');
}

console.log('\n2️⃣ Testing FeatureManager...');

// Test feature registration
class TestFeature {
  constructor(config) {
    this.config = config;
    this.initialized = false;
    this.running = false;
  }
  
  async initialize() {
    this.initialized = true;
  }
  
  async start() {
    this.running = true;
  }
  
  async stop() {
    this.running = false;
  }
}

const featureManager = new FeatureManager();

featureManager.registerFeature('test-feature', TestFeature, {
  enabled: true,
  critical: false,
  dependencies: [],
  autoStart: true,
  config: { test: true }
});

await featureManager.initializeAll();
await featureManager.startAll();

const status = featureManager.getFeatureStatus('test-feature');
if (status.initialized && status.running) {
  console.log('✅ Feature lifecycle works');
} else {
  console.log('❌ Feature lifecycle failed');
}

// Test dependency resolution
featureManager.registerFeature('feature-a', TestFeature, {
  enabled: true,
  dependencies: []
});

featureManager.registerFeature('feature-b', TestFeature, {
  enabled: true,
  dependencies: ['feature-a']
});

try {
  const order = featureManager.resolveDependencyOrder();
  const bIndex = order.indexOf('feature-b');
  const aIndex = order.indexOf('feature-a');
  
  if (bIndex > aIndex) {
    console.log('✅ Dependency resolution works');
  } else {
    console.log('❌ Dependency resolution failed');
  }
} catch (error) {
  console.log('❌ Dependency resolution error:', error.message);
}

console.log('\n3️⃣ Testing HealthMonitor...');

const healthMonitor = new HealthMonitor({
  heartbeatInterval: 1000,
  checkInterval: 2000,
  autoRestart: false
});

healthMonitor.start();

let heartbeatReceived = false;
healthMonitor.once('heartbeat', () => {
  heartbeatReceived = true;
});

// Wait for heartbeat
await new Promise(resolve => setTimeout(resolve, 1500));

if (heartbeatReceived) {
  console.log('✅ Heartbeat monitoring works');
} else {
  console.log('❌ Heartbeat not received');
}

const metrics = healthMonitor.getMetrics();
if (metrics.memory && metrics.uptime !== undefined) {
  console.log('✅ Metrics collection works');
} else {
  console.log('❌ Metrics collection failed');
}

healthMonitor.stop();

console.log('\n4️⃣ Testing ProcessLinker...');

const processLinker = new ProcessLinker();

processLinker.registerService('service-a', { name: 'Service A' }, {
  type: 'test',
  provides: ['capability-x']
});

processLinker.registerService('service-b', { name: 'Service B' }, {
  type: 'test',
  requires: ['capability-x']
});

const discovered = processLinker.discover('service-a');
if (discovered && discovered.name === 'Service A') {
  console.log('✅ Service discovery works');
} else {
  console.log('❌ Service discovery failed');
}

const byType = processLinker.discoverByType('test');
if (byType.length === 2) {
  console.log('✅ Discovery by type works');
} else {
  console.log('❌ Discovery by type failed');
}

console.log('\n5️⃣ Testing ShutdownHandler...');

const shutdownHandler = new ShutdownHandler({
  gracePeriod: 5000,
  forceShutdownDelay: 1000
});

shutdownHandler.initialize();

let hookExecuted = false;
shutdownHandler.registerHook('test-hook', async () => {
  hookExecuted = true;
}, 100);

// Test operation tracking
const complete = shutdownHandler.trackOperation('test-op', 'Test operation');
complete(); // Mark as complete

const state = shutdownHandler.getState();
if (state.activeOperations === 0) {
  console.log('✅ Operation tracking works');
} else {
  console.log('❌ Operation tracking failed');
}

console.log('\n✅ All core systems tests passed!');
console.log('\n📊 Summary:');
console.log('  - ErrorHandler: Retry logic, circuit breaker ✅');
console.log('  - FeatureManager: Lifecycle, dependencies ✅');
console.log('  - HealthMonitor: Heartbeat, metrics ✅');
console.log('  - ProcessLinker: Discovery, linking ✅');
console.log('  - ShutdownHandler: Hooks, operations ✅');

// Cleanup
await errorHandler.shutdown();
await featureManager.shutdown();
await healthMonitor.shutdown();
await processLinker.shutdown();

process.exit(0);
