# Getting Started with Error Handling and Feature Management

This guide will help you integrate the comprehensive error handling and feature management system into your application.

## Quick Start

### 1. Basic Setup

```javascript
import ErrorHandler from './src/core/ErrorHandler.js';
import FeatureManager from './src/core/FeatureManager.js';
import HealthMonitor from './src/core/HealthMonitor.js';
import ShutdownHandler from './src/core/ShutdownHandler.js';

// Load configuration
import config from './config/error-handling.json' assert { type: 'json' };

// Initialize core systems
const errorHandler = new ErrorHandler(config.errorHandler);
const featureManager = new FeatureManager(config.features);
const healthMonitor = new HealthMonitor(config.healthMonitor);
const shutdownHandler = new ShutdownHandler(config.shutdownHandler);

// Initialize error handler first (catches all errors)
errorHandler.initialize();
shutdownHandler.initialize();
```

### 2. Create a Feature

```javascript
class MyFeature {
  constructor(config) {
    this.config = config;
    this.running = false;
  }

  async initialize() {
    console.log('Initializing MyFeature...');
    // Setup resources, validate config, etc.
  }

  async start() {
    console.log('Starting MyFeature...');
    this.running = true;
    // Start processing, open connections, etc.
  }

  async stop() {
    console.log('Stopping MyFeature...');
    this.running = false;
    // Close connections, cleanup resources, etc.
  }
}
```

### 3. Register Features

```javascript
// Register features with dependencies
featureManager.registerFeature('database', DatabaseFeature, {
  enabled: true,
  critical: true,      // System won't start if this fails
  dependencies: [],
  autoStart: true,
  config: { connectionString: process.env.DATABASE_URL }
});

featureManager.registerFeature('api', APIFeature, {
  enabled: true,
  critical: true,
  dependencies: ['database'],  // Starts after database
  autoStart: true,
  config: { port: 3000 }
});

featureManager.registerFeature('analytics', AnalyticsFeature, {
  enabled: true,
  critical: false,     // System continues if this fails
  dependencies: ['database'],
  autoStart: true,
  config: {}
});
```

### 4. Setup Shutdown Hooks

```javascript
shutdownHandler.registerHook('health-monitor', async () => {
  await healthMonitor.shutdown();
}, 100);  // Priority 100 - runs first

shutdownHandler.registerHook('feature-manager', async () => {
  await featureManager.shutdown();
}, 90);

shutdownHandler.registerHook('error-handler', async () => {
  await errorHandler.shutdown();
}, 80);
```

### 5. Start the System

```javascript
async function startSystem() {
  try {
    // Initialize all features
    await featureManager.initializeAll();
    
    // Start health monitoring
    healthMonitor.start();
    
    // Start all features
    await featureManager.startAll();
    
    console.log('✅ System started successfully!');
  } catch (error) {
    console.error('❌ Failed to start system:', error);
    await errorHandler.handleError('STARTUP_FAILED', error);
    process.exit(1);
  }
}

startSystem();
```

## Common Use Cases

### Use Case 1: API with Retry Logic

```javascript
import ErrorHandler from './src/core/ErrorHandler.js';

const errorHandler = new ErrorHandler();
errorHandler.initialize();

async function fetchUserData(userId) {
  return await errorHandler.withRetry(
    async () => {
      // Check circuit breaker
      if (errorHandler.isCircuitOpen('user-api')) {
        throw new Error('User API circuit breaker open');
      }

      try {
        const response = await fetch(`/api/users/${userId}`);
        errorHandler.recordServiceSuccess('user-api');
        return response.json();
      } catch (error) {
        await errorHandler.handleApiError(error, {
          service: 'user-api',
          endpoint: `/api/users/${userId}`
        });
        throw error;
      }
    },
    {
      maxRetries: 3,
      retryDelay: 1000,
      onRetry: (error, attempt) => {
        console.log(`Retry ${attempt} after error: ${error.message}`);
      }
    }
  );
}

// Usage
try {
  const user = await fetchUserData(123);
  console.log('User:', user);
} catch (error) {
  console.error('Failed to fetch user:', error.message);
}
```

### Use Case 2: Database Feature with Health Monitoring

```javascript
class DatabaseFeature {
  constructor(config) {
    this.config = config;
    this.connection = null;
    this.healthCheckInterval = null;
  }

  async initialize() {
    // Validate configuration
    if (!this.config.connectionString) {
      throw new Error('Database connection string required');
    }
  }

  async start() {
    // Connect to database
    this.connection = await this.connect();
    
    // Start health monitoring
    this.healthCheckInterval = setInterval(() => {
      this.checkHealth();
    }, 5000);
  }

  async stop() {
    // Stop health checks
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    
    // Close connection
    if (this.connection) {
      await this.connection.close();
    }
  }

  async connect() {
    // Implement database connection
    return { /* connection object */ };
  }

  async checkHealth() {
    try {
      // Ping database
      await this.connection.ping();
      
      // Report healthy
      featureManager.updateFeatureHealth('database', true, {
        connections: this.connection.activeConnections
      });
    } catch (error) {
      // Report unhealthy
      featureManager.updateFeatureHealth('database', false);
      
      // Log error
      await errorHandler.handleDatabaseError(error, {
        operation: 'health_check'
      });
    }
  }
}
```

### Use Case 3: Dynamic Feature Control

```javascript
// Disable a feature at runtime
await featureManager.disableFeature('analytics');
console.log('Analytics disabled');

// Re-enable later
await featureManager.enableFeature('analytics');
console.log('Analytics re-enabled');

// Get feature status
const status = featureManager.getFeatureStatus('analytics');
console.log('Analytics status:', status);
// {
//   enabled: true,
//   initialized: true,
//   running: true,
//   healthy: true,
//   error: null,
//   startedAt: "2025-12-13T21:30:47.256Z"
// }
```

### Use Case 4: Monitoring Events

```javascript
// Listen to error events
errorHandler.on('apiError', ({ error, context }) => {
  console.error('API Error:', error.message);
  // Send to monitoring service
  sendToDatadog({ type: 'api_error', error, context });
});

errorHandler.on('circuitBreakerOpened', ({ serviceName, failures }) => {
  console.warn(`Circuit breaker opened for ${serviceName}`);
  // Alert operations team
  alertOps({ service: serviceName, failures });
});

// Listen to health events
healthMonitor.on('unhealthy', (metrics) => {
  console.warn('System unhealthy!', metrics);
  // Scale up resources
  scaleUpResources();
});

healthMonitor.on('memoryLeak', ({ current, history }) => {
  console.error('Memory leak detected!');
  // Trigger investigation
  createIncident('memory_leak', { current, history });
});

// Listen to feature events
featureManager.on('featureUnhealthy', ({ name, metrics }) => {
  console.warn(`Feature ${name} is unhealthy`);
  // Attempt recovery
  attemptFeatureRecovery(name);
});
```

### Use Case 5: Express.js Integration

```javascript
import express from 'express';
import ErrorHandler from './src/core/ErrorHandler.js';
import HealthMonitor from './src/core/HealthMonitor.js';
import FeatureManager from './src/core/FeatureManager.js';

const app = express();
const errorHandler = new ErrorHandler();
const healthMonitor = new HealthMonitor();
const featureManager = new FeatureManager();

errorHandler.initialize();

// Health check endpoint
app.get('/health', (req, res) => {
  const health = healthMonitor.getStatus();
  const features = featureManager.getSystemHealth();
  
  const status = health.healthy && features.healthy ? 200 : 503;
  
  res.status(status).json({
    healthy: health.healthy && features.healthy,
    health: health,
    features: features.summary,
    timestamp: new Date().toISOString()
  });
});

// Metrics endpoint
app.get('/metrics', (req, res) => {
  res.json({
    health: healthMonitor.getMetrics(),
    errors: errorHandler.getStats(),
    features: featureManager.getSystemHealth(),
    circuitBreakers: errorHandler.getCircuitBreakerStatus()
  });
});

// Feature control endpoint
app.post('/features/:name/enable', async (req, res) => {
  try {
    await featureManager.enableFeature(req.params.name);
    res.json({ success: true });
  } catch (error) {
    await errorHandler.handleError('FEATURE_ENABLE_FAILED', error, {
      feature: req.params.name
    });
    res.status(500).json({ error: error.message });
  }
});

app.post('/features/:name/disable', async (req, res) => {
  try {
    await featureManager.disableFeature(req.params.name);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  errorHandler.handleError('HTTP_REQUEST_ERROR', err, {
    method: req.method,
    path: req.path,
    body: req.body
  });
  
  res.status(500).json({
    error: 'Internal server error',
    requestId: req.id
  });
});

// Start server
app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

## Configuration

Edit `config/error-handling.json` to customize behavior:

```json
{
  "errorHandler": {
    "logErrors": true,
    "logPath": "./logs/errors.log",
    "maxRetries": 3,
    "retryDelay": 1000,
    "circuitBreakerThreshold": 5
  },
  "healthMonitor": {
    "heartbeatInterval": 5000,
    "memoryThreshold": 0.9,
    "cpuThreshold": 0.8,
    "checkInterval": 10000,
    "autoRestart": true,
    "maxRestarts": 5
  },
  "features": {
    "myFeature": {
      "enabled": true,
      "critical": false,
      "autoStart": true
    }
  }
}
```

## Testing

Run the test suite:

```bash
node tests/test-core-systems.js
```

Run the integration example:

```bash
node src/core/index.js
```

## Documentation

- [Error Handling Guide](docs/ERROR_HANDLING.md)
- [Feature Management Guide](docs/FEATURE_MANAGEMENT.md)
- [System Monitoring Guide](docs/SYSTEM_MONITORING.md)

## Best Practices

1. **Initialize ErrorHandler First**: Always initialize the error handler before other components
2. **Use Specific Error Handlers**: Use `handleApiError`, `handleDatabaseError`, etc. for better categorization
3. **Provide Context**: Always include context when handling errors for better debugging
4. **Mark Critical Features**: Only mark truly essential features as critical
5. **Monitor Circuit Breakers**: Watch for circuit breaker openings and investigate root causes
6. **Use Retry for Transient Failures**: Only retry operations that may succeed on subsequent attempts
7. **Register Shutdown Hooks**: Ensure all resources are properly cleaned up on shutdown
8. **Monitor Health**: Use the health monitor to detect and prevent issues early

## Troubleshooting

### System Not Starting

1. Check feature dependencies are correct
2. Review error logs in `./logs/errors.log`
3. Check critical features are healthy
4. Verify configuration in `config/error-handling.json`

### High Memory Usage

1. Check for memory leaks with health monitor events
2. Review feature health metrics
3. Check for unclosed connections or resources
4. Run with `--expose-gc` to enable manual garbage collection

### Circuit Breakers Opening

1. Check external service availability
2. Review API error logs
3. Verify network connectivity
4. Consider increasing circuit breaker threshold if false positives

### Features Not Starting

1. Check feature is enabled in configuration
2. Verify dependencies are initialized
3. Review feature status with `getFeatureStatus()`
4. Check feature logs for initialization errors

## Support

For issues or questions:
1. Review the documentation in `/docs`
2. Check the test examples in `/tests`
3. Review the integration example in `src/core/index.js`
