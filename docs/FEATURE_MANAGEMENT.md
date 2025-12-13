# Feature Management Guide

## Overview

The Feature Management System provides centralized control over all application features, including:
- Dynamic feature enable/disable
- Dependency resolution
- Lifecycle management (initialize, start, stop)
- Health monitoring per feature
- Safe shutdown

## Quick Start

```javascript
import FeatureManager from './core/FeatureManager.js';
import config from '../config/error-handling.json' assert { type: 'json' };

const featureManager = new FeatureManager(config.features);

// Register features
featureManager.registerFeature('trading', TradingEngine, {
  enabled: true,
  critical: false,
  dependencies: ['database'],
  autoStart: true,
  config: { /* trading config */ }
});

// Initialize and start all
await featureManager.initializeAll();
await featureManager.startAll();
```

## Registering Features

### Basic Registration

```javascript
featureManager.registerFeature('my-feature', MyFeatureClass, {
  enabled: true,        // Feature enabled by default
  critical: false,      // Non-critical (system continues if it fails)
  dependencies: [],     // No dependencies
  autoStart: true,      // Start automatically with system
  config: {}           // Feature-specific configuration
});
```

### Feature Class Requirements

Your feature class should implement these optional methods:

```javascript
class MyFeature {
  constructor(config) {
    this.config = config;
  }

  // Optional: Called during initialization
  async initialize() {
    console.log('Initializing...');
    // Setup resources, connect to services, etc.
  }

  // Optional: Called during startup
  async start() {
    console.log('Starting...');
    // Start processing, open connections, etc.
  }

  // Optional: Called during shutdown
  async stop() {
    console.log('Stopping...');
    // Stop processing, close connections, etc.
  }
}
```

## Feature Configuration

### Critical vs Non-Critical Features

**Critical Features:**
- System startup fails if critical feature fails to initialize
- System health is unhealthy if critical feature is unhealthy
- Examples: database, authentication, core API

```javascript
featureManager.registerFeature('database', DatabaseManager, {
  critical: true  // System depends on this
});
```

**Non-Critical Features:**
- System continues if non-critical feature fails
- Errors are logged but don't stop startup
- Examples: analytics, reporting, notifications

```javascript
featureManager.registerFeature('analytics', AnalyticsService, {
  critical: false  // Nice to have, not essential
});
```

### Dependencies

Features can depend on other features:

```javascript
// Database must start before trading
featureManager.registerFeature('database', DatabaseManager, {
  dependencies: []
});

featureManager.registerFeature('trading', TradingEngine, {
  dependencies: ['database']
});

// FeatureManager ensures database starts before trading
```

**Dependency Resolution:**
- Automatic startup order based on dependencies
- Circular dependency detection
- Missing dependency detection

### Auto-Start

Control which features start automatically:

```javascript
featureManager.registerFeature('debug-tools', DebugTools, {
  autoStart: false  // Don't start automatically
});

// Manually start later
await featureManager.startFeature('debug-tools');
```

## Lifecycle Management

### Initialize All Features

```javascript
// Initializes all enabled features in dependency order
await featureManager.initializeAll();
```

**What happens:**
1. Resolves dependency order
2. Initializes each enabled feature
3. Calls `initialize()` method if present
4. Tracks initialization status
5. Fails fast if critical feature fails

### Start All Features

```javascript
// Starts all initialized features with autoStart=true
await featureManager.startAll();
```

**What happens:**
1. Uses previously resolved dependency order
2. Skips disabled or non-initialized features
3. Skips features with autoStart=false
4. Calls `start()` method if present
5. Fails fast if critical feature fails

### Individual Feature Control

```javascript
// Initialize a single feature
await featureManager.initializeFeature('my-feature');

// Start a single feature
await featureManager.startFeature('my-feature');

// Stop a single feature
await featureManager.stopFeature('my-feature');
```

### Stop All Features

```javascript
// Stops all running features in reverse order
await featureManager.stopAll();
```

## Dynamic Feature Control

### Enable Feature at Runtime

```javascript
// Enable and optionally auto-start
await featureManager.enableFeature('trading');
```

**What happens:**
- Feature is marked as enabled
- If system is running and autoStart=true, feature starts immediately
- Emits 'featureEnabled' event

### Disable Feature at Runtime

```javascript
// Disable and stop if running
await featureManager.disableFeature('trading');
```

**What happens:**
- Feature is stopped if currently running
- Feature is marked as disabled
- Won't start on next system restart
- Emits 'featureDisabled' event

## Feature Status

### Get Feature Status

```javascript
const status = featureManager.getFeatureStatus('trading');
console.log(status);
// {
//   enabled: true,
//   initialized: true,
//   running: true,
//   healthy: true,
//   error: null,
//   startedAt: "2025-12-13T21:30:47.256Z",
//   metrics: {}
// }
```

### Get All Features

```javascript
const features = featureManager.getAllFeatures();
console.log(features);
// {
//   trading: {
//     name: 'trading',
//     FeatureClass: [Function: TradingEngine],
//     enabled: true,
//     critical: false,
//     dependencies: ['database'],
//     config: {...},
//     status: {...}
//   },
//   ...
// }
```

### Get System Health

```javascript
const health = featureManager.getSystemHealth();
console.log(health);
// {
//   healthy: true,
//   features: {
//     trading: { enabled: true, running: true, healthy: true, ... },
//     ...
//   },
//   summary: {
//     total: 6,
//     enabled: 5,
//     running: 4,
//     healthy: 4,
//     unhealthy: 0
//   }
// }
```

## Health Monitoring

### Update Feature Health

Features can report their health status:

```javascript
class MyFeature {
  async start() {
    setInterval(() => {
      const healthy = this.checkHealth();
      featureManager.updateFeatureHealth('my-feature', healthy, {
        connections: this.activeConnections,
        queueSize: this.queue.length
      });
    }, 5000);
  }

  checkHealth() {
    return this.activeConnections > 0 && this.queue.length < 1000;
  }
}
```

### Health Events

```javascript
featureManager.on('featureUnhealthy', ({ name, metrics }) => {
  console.warn(`Feature ${name} is unhealthy`, metrics);
  // Alert operations team
});

featureManager.on('featureRecovered', ({ name, metrics }) => {
  console.log(`Feature ${name} recovered`, metrics);
});
```

## Events

### Available Events

```javascript
// Feature registered
featureManager.on('featureRegistered', ({ name, config }) => {});

// Feature initialized
featureManager.on('featureInitialized', ({ name }) => {});

// Feature started
featureManager.on('featureStarted', ({ name }) => {});

// Feature stopped
featureManager.on('featureStopped', ({ name }) => {});

// Feature enabled
featureManager.on('featureEnabled', ({ name }) => {});

// Feature disabled
featureManager.on('featureDisabled', ({ name }) => {});

// Feature unhealthy
featureManager.on('featureUnhealthy', ({ name, metrics }) => {});

// Feature recovered
featureManager.on('featureRecovered', ({ name, metrics }) => {});

// All initialized
featureManager.on('allInitialized', () => {});

// All started
featureManager.on('allStarted', () => {});

// All stopped
featureManager.on('allStopped', () => {});
```

## Example Features

### Database Feature

```javascript
class DatabaseFeature {
  constructor(config) {
    this.config = config;
    this.connection = null;
  }

  async initialize() {
    console.log('📦 Initializing database...');
    // Validate config
    if (!this.config.connectionString) {
      throw new Error('Database connection string required');
    }
  }

  async start() {
    console.log('🚀 Starting database...');
    this.connection = await connectToDatabase(this.config.connectionString);
  }

  async stop() {
    console.log('🛑 Stopping database...');
    if (this.connection) {
      await this.connection.close();
    }
  }
}

featureManager.registerFeature('database', DatabaseFeature, {
  enabled: true,
  critical: true,
  dependencies: [],
  config: {
    connectionString: process.env.DATABASE_URL
  }
});
```

### Trading Engine Feature

```javascript
class TradingEngine {
  constructor(config) {
    this.config = config;
    this.running = false;
  }

  async initialize() {
    console.log('📦 Initializing trading engine...');
    // Load strategies, connect to exchange APIs
  }

  async start() {
    console.log('🚀 Starting trading engine...');
    this.running = true;
    this.tradingLoop();
  }

  async stop() {
    console.log('🛑 Stopping trading engine...');
    this.running = false;
    // Close positions, disconnect from exchanges
  }

  async tradingLoop() {
    while (this.running) {
      try {
        await this.executeTrades();
        featureManager.updateFeatureHealth('trading', true, {
          positions: this.activePositions.length
        });
      } catch (error) {
        featureManager.updateFeatureHealth('trading', false);
      }
      await sleep(1000);
    }
  }
}

featureManager.registerFeature('trading', TradingEngine, {
  enabled: true,
  critical: false,
  dependencies: ['database'],
  config: {
    mode: 'paper',
    maxPositions: 5
  }
});
```

## Best Practices

### 1. Use Proper Dependencies

Always declare dependencies explicitly:

```javascript
// ✅ Good
featureManager.registerFeature('api', APIServer, {
  dependencies: ['database', 'auth']
});

// ❌ Bad - accessing database without declaring dependency
featureManager.registerFeature('api', APIServer, {
  dependencies: []  // Should include database!
});
```

### 2. Mark Critical Features Appropriately

```javascript
// ✅ Critical features
- database
- authentication
- core API

// ✅ Non-critical features  
- analytics
- notifications
- reporting
- debug tools
```

### 3. Implement Graceful Shutdown

```javascript
class MyFeature {
  async stop() {
    // 1. Stop accepting new work
    this.accepting = false;
    
    // 2. Complete in-progress work
    await this.waitForPendingWork();
    
    // 3. Clean up resources
    await this.cleanup();
  }
}
```

### 4. Report Health Accurately

```javascript
class MyFeature {
  checkHealth() {
    return (
      this.connection.isAlive() &&
      this.queue.length < this.maxQueueSize &&
      this.errorRate < 0.1
    );
  }
}
```

### 5. Handle Initialization Errors

```javascript
class MyFeature {
  async initialize() {
    try {
      await this.setup();
    } catch (error) {
      // Clean up partial initialization
      await this.cleanup();
      throw error;  // Let FeatureManager handle it
    }
  }
}
```

## Troubleshooting

### Circular Dependency Error

```
Error: Circular dependency detected involving feature-a
```

**Solution:** Review dependencies, remove circular references:
```javascript
// ❌ Circular
featureA depends on featureB
featureB depends on featureA

// ✅ Fix: Use event bus instead
featureA emits events
featureB subscribes to events
```

### Feature Won't Start

1. Check if feature is enabled
2. Check if dependencies are initialized
3. Check feature status for error message
4. Review feature's `start()` method logs

### System Health Always Unhealthy

1. Check which features are unhealthy
2. Review feature health metrics
3. Check if critical features are failing
4. Review health update logic in features

## Integration Example

```javascript
import FeatureManager from './core/FeatureManager.js';
import ErrorHandler from './core/ErrorHandler.js';
import config from '../config/error-handling.json' assert { type: 'json' };

// Initialize systems
const errorHandler = new ErrorHandler(config.errorHandler);
const featureManager = new FeatureManager(config.features);

errorHandler.initialize();

// Register features
featureManager.registerFeature('database', DatabaseFeature, {
  enabled: config.features.database.enabled,
  critical: config.features.database.critical,
  dependencies: [],
  config: { connectionString: process.env.DATABASE_URL }
});

featureManager.registerFeature('trading', TradingEngine, {
  enabled: config.features.trading.enabled,
  critical: config.features.trading.critical,
  dependencies: ['database'],
  config: { mode: process.env.TRADING_MODE }
});

// Handle errors from features
featureManager.on('featureError', async ({ name, error }) => {
  await errorHandler.handleError('FEATURE_ERROR', error, { feature: name });
});

// Start system
try {
  await featureManager.initializeAll();
  await featureManager.startAll();
  console.log('✅ All features started successfully');
} catch (error) {
  console.error('❌ Failed to start features:', error);
  await errorHandler.handleError('STARTUP_FAILED', error);
  process.exit(1);
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  await featureManager.shutdown();
  await errorHandler.shutdown();
  process.exit(0);
});
```
