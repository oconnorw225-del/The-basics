# System Monitoring and Health Checks

## Overview

The Health Monitor System provides real-time monitoring of system health, including:
- Heartbeat monitoring
- Memory leak detection
- CPU usage tracking
- Event loop lag detection
- Freeze detection and auto-recovery
- Automatic restart on unhealthy state

## Quick Start

```javascript
import HealthMonitor from './core/HealthMonitor.js';
import config from '../config/error-handling.json' assert { type: 'json' };

const healthMonitor = new HealthMonitor(config.healthMonitor);

// Start monitoring
healthMonitor.start();

// Get current metrics
const metrics = healthMonitor.getMetrics();
console.log(metrics);

// Get health status
const status = healthMonitor.getStatus();
console.log(status);
```

## Configuration

```javascript
const config = {
  heartbeatInterval: 5000,      // Heartbeat every 5 seconds
  memoryThreshold: 0.9,         // Alert at 90% memory usage
  cpuThreshold: 0.8,            // Alert at 80% CPU usage
  checkInterval: 10000,         // Health check every 10 seconds
  autoRestart: true,            // Auto-restart on unhealthy state
  maxRestarts: 5,               // Max auto-restart attempts
  freezeTimeout: 30000          // Detect freeze after 30 seconds
};

const healthMonitor = new HealthMonitor(config);
```

## Monitoring Capabilities

### 1. Heartbeat Monitoring

The heartbeat ensures the system is responsive:

```javascript
healthMonitor.on('heartbeat', ({ timestamp }) => {
  console.log(`💓 Heartbeat: ${timestamp}`);
});
```

**How it works:**
- Heartbeat emitted every `heartbeatInterval` (default: 5 seconds)
- Freeze detector checks time since last heartbeat
- If no heartbeat for `freezeTimeout`, system is considered frozen

### 2. Memory Monitoring

Track memory usage and detect leaks:

```javascript
healthMonitor.on('highMemory', ({ usage }) => {
  console.warn(`⚠️ High memory: ${(usage * 100).toFixed(2)}%`);
});

healthMonitor.on('memoryLeak', ({ current, history }) => {
  console.error('💧 Memory leak detected!');
  console.log('Current heap:', current);
  console.log('Recent history:', history);
});
```

**Memory Metrics:**
- `heapUsed` - Used heap memory
- `heapTotal` - Total heap size
- `external` - External C++ memory
- `rss` - Resident set size (total memory)

**Leak Detection:**
- Tracks last 100 memory readings
- Detects consistent growth pattern
- Alerts if memory grows >20% in recent history
- Triggers garbage collection if available

### 3. CPU Monitoring

Monitor CPU usage:

```javascript
healthMonitor.on('highCPU', ({ usage }) => {
  console.warn(`⚠️ High CPU: ${(usage * 100).toFixed(2)}%`);
});
```

**CPU Metrics:**
- `user` - CPU time in user code
- `system` - CPU time in system code
- Calculated as percentage of total time

### 4. Event Loop Lag

Detect event loop blocking:

```javascript
healthMonitor.on('eventLoopLag', ({ lag }) => {
  console.warn(`⚠️ Event loop lag: ${lag}ms`);
});
```

**What is measured:**
- Time between scheduling and executing `setImmediate()`
- Lag > 100ms indicates blocking operations
- Suggests need for optimization or worker threads

### 5. Freeze Detection

Detect when the system stops responding:

```javascript
healthMonitor.on('freeze', ({ timeSinceHeartbeat, lastHeartbeat }) => {
  console.error(`💥 System frozen! No heartbeat for ${timeSinceHeartbeat}ms`);
});
```

**How it works:**
- Checks heartbeat timing every `freezeTimeout`
- If heartbeat delayed beyond threshold, system is frozen
- Auto-restart triggered if `autoRestart: true`

## Health Checks

### Automatic Health Checks

Health checks run automatically at `checkInterval`:

```javascript
healthMonitor.on('healthCheck', ({ healthy, metrics, issues }) => {
  console.log('Health check:', healthy ? '✅' : '❌');
  console.log('Issues:', issues);
});
```

**Health check includes:**
- Memory usage check
- CPU usage check  
- Event loop lag check
- Updates all metrics
- Determines overall health

### Health State Changes

Monitor when system becomes unhealthy:

```javascript
healthMonitor.on('unhealthy', (metrics) => {
  console.warn('⚠️ System unhealthy', metrics);
  // Alert operations team
  // Scale resources
  // Trigger recovery
});

healthMonitor.on('recovered', (metrics) => {
  console.log('✅ System recovered', metrics);
});
```

## Auto-Recovery

### Automatic Restart

When system becomes unhealthy and `autoRestart: true`:

```javascript
healthMonitor.on('restarting', ({ reason, attempt }) => {
  console.log(`🔄 Restarting (${reason}), attempt ${attempt}`);
});
```

**Restart triggers:**
- System health check fails
- System freeze detected
- Memory leak with critical usage
- Respects `maxRestarts` limit

**Restart process:**
1. Emit 'restarting' event
2. Wait 5 seconds for cleanup
3. Exit process with code 1
4. PM2/systemd/supervisor restarts process

### Max Restarts Reached

When restart limit is reached:

```javascript
healthMonitor.on('maxRestartsReached', ({ reason }) => {
  console.error(`❌ Max restarts reached: ${reason}`);
  // Manual intervention required
  // Alert operations team
  // Create incident ticket
});
```

**What to do:**
- Check system logs
- Review error patterns
- Check resource availability
- Manual restart may be needed

## Metrics API

### Get Current Metrics

```javascript
const metrics = healthMonitor.getMetrics();
console.log(metrics);
// {
//   cpu: { user: 123456, system: 78901 },
//   memory: {
//     heapUsed: 45678901,
//     heapTotal: 67890123,
//     external: 1234567,
//     rss: 123456789
//   },
//   eventLoop: { lag: 5 },
//   uptime: 123456,
//   memoryUsagePercent: 67.2,
//   healthy: true,
//   restartCount: 0
// }
```

### Get Status

```javascript
const status = healthMonitor.getStatus();
console.log(status);
// {
//   running: true,
//   healthy: true,
//   uptime: 123456,
//   restartCount: 0,
//   lastHeartbeat: 1702501847256,
//   metrics: { ... }
// }
```

## Memory Leak Detection

### How It Works

1. **Memory History Tracking**
   - Keeps last 100 memory readings
   - Each reading includes timestamp and heap usage

2. **Growth Pattern Analysis**
   - Checks if 8 out of 10 recent readings show growth
   - Calculates growth percentage

3. **Leak Criteria**
   - Consistent growth pattern detected
   - Growth > 20% in recent history

4. **Automatic Actions**
   - Trigger garbage collection if available
   - Emit 'memoryLeak' event
   - Can trigger auto-restart

### Running with Garbage Collection

Enable GC for manual triggering:

```bash
node --expose-gc your-app.js
```

Then the monitor can trigger GC:

```javascript
if (global.gc) {
  global.gc();
  console.log('🗑️ Garbage collection triggered');
}
```

## Integration Examples

### With Error Handler

```javascript
import HealthMonitor from './core/HealthMonitor.js';
import ErrorHandler from './core/ErrorHandler.js';

const healthMonitor = new HealthMonitor(config);
const errorHandler = new ErrorHandler();

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
```

### With Feature Manager

```javascript
import HealthMonitor from './core/HealthMonitor.js';
import FeatureManager from './core/FeatureManager.js';

const healthMonitor = new HealthMonitor(config);
const featureManager = new FeatureManager();

healthMonitor.on('unhealthy', async () => {
  // Disable non-critical features to reduce load
  await featureManager.disableFeature('analytics');
  await featureManager.disableFeature('reporting');
});

healthMonitor.on('recovered', async () => {
  // Re-enable features
  await featureManager.enableFeature('analytics');
  await featureManager.enableFeature('reporting');
});
```

### Exposing Health Endpoint

```javascript
import express from 'express';

const app = express();

app.get('/health', (req, res) => {
  const status = healthMonitor.getStatus();
  const httpStatus = status.healthy ? 200 : 503;
  
  res.status(httpStatus).json(status);
});

app.get('/metrics', (req, res) => {
  const metrics = healthMonitor.getMetrics();
  res.json(metrics);
});
```

### Dashboard Integration

```javascript
import HealthMonitor from './core/HealthMonitor.js';

const healthMonitor = new HealthMonitor(config);

// Send metrics to dashboard every 5 seconds
setInterval(() => {
  const metrics = healthMonitor.getMetrics();
  
  dashboard.update({
    memory: metrics.memoryUsagePercent,
    cpu: metrics.cpu,
    eventLoopLag: metrics.eventLoop.lag,
    uptime: metrics.uptime,
    healthy: metrics.healthy
  });
}, 5000);
```

## Best Practices

### 1. Configure Thresholds Appropriately

```javascript
// Development
{
  memoryThreshold: 0.9,   // Allow high memory usage
  cpuThreshold: 0.95,     // Allow high CPU
  autoRestart: false      // Don't auto-restart
}

// Production
{
  memoryThreshold: 0.8,   // Conservative memory limit
  cpuThreshold: 0.7,      // Conservative CPU limit
  autoRestart: true       // Auto-recover from issues
}
```

### 2. Monitor Health Endpoints

Use external monitoring:

```bash
# Uptime monitoring
curl http://your-app/health

# Metrics scraping (Prometheus, etc.)
curl http://your-app/metrics
```

### 3. Alert on Health Events

```javascript
healthMonitor.on('unhealthy', async (metrics) => {
  await sendAlert({
    severity: 'warning',
    title: 'System Unhealthy',
    metrics
  });
});

healthMonitor.on('freeze', async () => {
  await sendAlert({
    severity: 'critical',
    title: 'System Frozen'
  });
});
```

### 4. Regular Baseline Updates

Update baseline metrics after warm-up:

```javascript
// After warm-up period
setTimeout(() => {
  healthMonitor.updateBaseline();
  console.log('📊 Baseline metrics updated');
}, 60000); // 1 minute
```

### 5. Review Restart Patterns

```javascript
healthMonitor.on('restarting', ({ reason, attempt }) => {
  logToFile({
    timestamp: new Date(),
    reason,
    attempt,
    metrics: healthMonitor.getMetrics()
  });
});

// Reset counter periodically if system is stable
setInterval(() => {
  const status = healthMonitor.getStatus();
  if (status.healthy && status.uptime > 3600000) { // 1 hour
    healthMonitor.resetRestartCounter();
  }
}, 3600000);
```

## Troubleshooting

### High Memory Warnings

1. Check for memory leaks in application code
2. Review object retention and caching
3. Check for growing arrays/collections
4. Profile with Chrome DevTools or clinic.js

### High CPU Warnings

1. Check for CPU-intensive operations
2. Review synchronous vs asynchronous code
3. Consider worker threads for heavy tasks
4. Profile with clinic.js or 0x

### Event Loop Lag

1. Identify blocking operations
2. Move heavy computation to worker threads
3. Use async I/O operations
4. Batch or throttle operations

### Frequent Restarts

1. Review restart logs and patterns
2. Check if thresholds are too aggressive
3. Verify external dependencies are healthy
4. Check for memory leaks
5. Increase resources if needed

### System Not Recovering

1. Check max restarts setting
2. Review logs for error patterns
3. Verify cleanup code in features
4. Check external service availability

## Complete Example

```javascript
import HealthMonitor from './core/HealthMonitor.js';
import config from '../config/error-handling.json' assert { type: 'json' };

// Initialize
const healthMonitor = new HealthMonitor(config.healthMonitor);

// Setup event handlers
healthMonitor.on('heartbeat', ({ timestamp }) => {
  // Optional: log heartbeats
});

healthMonitor.on('healthCheck', ({ healthy, issues }) => {
  if (!healthy) {
    console.warn('Health issues:', issues);
  }
});

healthMonitor.on('highMemory', ({ usage }) => {
  console.warn(`Memory usage: ${(usage * 100).toFixed(2)}%`);
});

healthMonitor.on('memoryLeak', ({ current, history }) => {
  console.error('Memory leak detected!');
  // Alert operations
});

healthMonitor.on('unhealthy', (metrics) => {
  console.error('System unhealthy', metrics);
  // Trigger recovery procedures
});

healthMonitor.on('restarting', ({ reason, attempt }) => {
  console.log(`Restarting: ${reason}, attempt ${attempt}`);
});

// Start monitoring
healthMonitor.start();

// Expose health endpoint
app.get('/health', (req, res) => {
  res.json(healthMonitor.getStatus());
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  await healthMonitor.shutdown();
});
```
