# System Architecture - Feature Management & Error Handling

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Application Layer                        │
│  (bot.js, server.js, freelance_engine/orchestrator.py, etc.)  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ uses
┌─────────────────────────────────────────────────────────────────┐
│                         Core Systems                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ErrorHandler  │  │FeatureManager│  │HealthMonitor │         │
│  │              │  │              │  │              │         │
│  │• Retry Logic │  │• Lifecycle   │  │• Heartbeat   │         │
│  │• Circuit     │  │• Dependencies│  │• Memory Leak │         │
│  │  Breaker     │  │• Health Track│  │• CPU Monitor │         │
│  │• Error Logs  │  │• Enable/     │  │• Auto-restart│         │
│  │              │  │  Disable     │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │ProcessLinker │  │ShutdownHandler                           │
│  │              │  │              │                            │
│  │• Service     │  │• SIGTERM     │                           │
│  │  Discovery   │  │• SIGINT      │                           │
│  │• Event Bus   │  │• Graceful    │                           │
│  │• Dependencies│  │  Shutdown    │                           │
│  │              │  │• Cleanup     │                           │
│  └──────────────┘  └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓ configured by
┌─────────────────────────────────────────────────────────────────┐
│                      Configuration                              │
│              config/error-handling.json                         │
│  • Error thresholds  • Health monitoring  • Feature settings   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Error Handling Flow

```
Application Code
      ↓ error occurs
ErrorHandler.handleError()
      ↓
  ┌───────────────────┐
  │ Log Error         │
  │ Track Statistics  │
  │ Check Circuit     │
  │ Emit Event        │
  └───────────────────┘
      ↓
  ┌─────────────────────────┐
  │ Retry?                  │
  │ Yes → withRetry()       │
  │ No → Fail gracefully    │
  └─────────────────────────┘
```

### 2. Feature Lifecycle Flow

```
registerFeature()
      ↓
  ┌─────────────────┐
  │ Resolve         │
  │ Dependencies    │
  └─────────────────┘
      ↓
initializeAll()
      ↓
  ┌─────────────────┐
  │ For each        │
  │ feature (in     │
  │ dependency      │
  │ order):         │
  │                 │
  │ • initialize()  │
  │ • start()       │
  └─────────────────┘
      ↓
Features Running
      ↓
  ┌─────────────────┐
  │ Monitor Health  │
  │ Enable/Disable  │
  └─────────────────┘
      ↓
shutdown()
      ↓
  ┌─────────────────┐
  │ For each        │
  │ feature         │
  │ (reverse        │
  │ order):         │
  │                 │
  │ • stop()        │
  └─────────────────┘
```

### 3. Health Monitoring Flow

```
healthMonitor.start()
      ↓
  ┌─────────────────────────┐
  │ Every heartbeatInterval │
  │ (5 seconds):            │
  │                         │
  │ Emit heartbeat event    │
  └─────────────────────────┘
      ↓
  ┌─────────────────────────┐
  │ Every checkInterval     │
  │ (10 seconds):           │
  │                         │
  │ • Check memory          │
  │ • Check CPU             │
  │ • Check event loop      │
  │ • Detect leaks          │
  │ • Detect freeze         │
  └─────────────────────────┘
      ↓
  ┌─────────────────┐
  │ Unhealthy?      │
  │                 │
  │ Yes → Emit      │
  │       event     │
  │       Auto-     │
  │       restart?  │
  │                 │
  │ No → Continue   │
  └─────────────────┘
```

### 4. Shutdown Flow

```
SIGTERM/SIGINT received
      ↓
shutdownHandler.initiateShutdown()
      ↓
  ┌─────────────────────────┐
  │ 1. Stop new requests    │
  └─────────────────────────┘
      ↓
  ┌─────────────────────────┐
  │ 2. Wait for operations  │
  │    (grace period)       │
  └─────────────────────────┘
      ↓
  ┌─────────────────────────┐
  │ 3. Execute hooks        │
  │    (by priority):       │
  │                         │
  │    • Health Monitor     │
  │    • Feature Manager    │
  │    • Process Linker     │
  │    • Error Handler      │
  └─────────────────────────┘
      ↓
  ┌─────────────────────────┐
  │ 4. Final cleanup        │
  └─────────────────────────┘
      ↓
process.exit(0)
```

## Component Interactions

### ErrorHandler ↔ All Components
```
Any Component → ErrorHandler.handleError()
                ↓
ErrorHandler → Logs error
             → Emits event
             → Updates statistics
```

### FeatureManager ↔ Features
```
FeatureManager → Feature.initialize()
               → Feature.start()
               ↓
Feature → featureManager.updateFeatureHealth()
        ← Health status tracked
```

### HealthMonitor ↔ System
```
HealthMonitor → Checks process.memoryUsage()
              → Checks process.cpuUsage()
              → Checks event loop lag
              ↓
              Emits health events
              ↓
Listeners → Take action based on health
```

### ProcessLinker ↔ Services
```
Service A → processLinker.registerService()
Service B → processLinker.registerService()
            ↓
processLinker.link()
            ↓
Service A ← connected to → Service B
            ↓
Event Bus (shared events and state)
```

## Integration Example

```javascript
// 1. Initialize core systems
const errorHandler = new ErrorHandler(config.errorHandler);
const featureManager = new FeatureManager(config.features);
const healthMonitor = new HealthMonitor(config.healthMonitor);
const shutdownHandler = new ShutdownHandler(config.shutdownHandler);

errorHandler.initialize();
shutdownHandler.initialize();

// 2. Wire up integrations
featureManager.on('featureError', async ({ name, error }) => {
  await errorHandler.handleError('FEATURE_ERROR', error, { feature: name });
});

healthMonitor.on('unhealthy', async (metrics) => {
  await errorHandler.handleError('SYSTEM_UNHEALTHY', 
    new Error('Health check failed'), { metrics });
});

// 3. Register shutdown hooks
shutdownHandler.registerHook('health-monitor', () => 
  healthMonitor.shutdown(), 100);
shutdownHandler.registerHook('feature-manager', () => 
  featureManager.shutdown(), 90);

// 4. Register features
featureManager.registerFeature('database', DatabaseFeature, {
  enabled: true, critical: true, dependencies: []
});
featureManager.registerFeature('api', APIFeature, {
  enabled: true, critical: true, dependencies: ['database']
});

// 5. Start system
await featureManager.initializeAll();
healthMonitor.start();
await featureManager.startAll();
```

## File Organization

```
The-basics/
├── src/core/               # Core systems
│   ├── ErrorHandler.js     # Error handling
│   ├── FeatureManager.js   # Feature lifecycle
│   ├── HealthMonitor.js    # Health monitoring
│   ├── ProcessLinker.js    # Service discovery
│   ├── ShutdownHandler.js  # Graceful shutdown
│   └── index.js           # Integration example
│
├── config/
│   └── error-handling.json # Central configuration
│
├── docs/                   # Documentation
│   ├── ERROR_HANDLING.md
│   ├── FEATURE_MANAGEMENT.md
│   ├── SYSTEM_MONITORING.md
│   └── GETTING_STARTED.md
│
├── tests/
│   └── test-core-systems.js # Tests
│
└── logs/                   # Runtime logs
    └── errors.log
```

## Key Design Patterns

### 1. Event-Driven Architecture
All core systems extend EventEmitter and communicate via events:
- Loose coupling between components
- Easy to add new listeners
- Supports plugin architecture

### 2. Lifecycle Management
All features follow initialize → start → stop pattern:
- Predictable initialization
- Clean shutdown
- Resource management

### 3. Circuit Breaker Pattern
ErrorHandler implements circuit breaker for external services:
- Prevents cascading failures
- Auto-recovery
- Fail-fast when service is down

### 4. Observer Pattern
Components can subscribe to system events:
- Health changes
- Error occurrences
- Feature state changes

### 5. Dependency Injection
Features receive configuration in constructor:
- Testable
- Configurable
- Flexible

## Performance Considerations

### Memory
- Health monitor tracks memory usage
- Detects memory leaks
- Can trigger garbage collection
- Auto-restart on high memory

### CPU
- Event loop lag detection
- CPU usage monitoring
- Warns on high CPU usage

### Scalability
- Event-driven architecture
- Async/await throughout
- Non-blocking operations
- Graceful degradation

## Security

- No secrets in code
- Input validation
- Rate limiting (bot.js)
- Whitelisted environment variables
- CodeQL scanned (0 vulnerabilities)

## Deployment

### Development
```bash
node src/core/index.js
```

### Production
```bash
# With PM2
pm2 start src/core/index.js --name "the-basics"

# With systemd
systemctl start the-basics

# With Docker
docker run -d the-basics
```

All deployment methods benefit from:
- Graceful shutdown on SIGTERM
- Auto-restart on crash (via HealthMonitor)
- Comprehensive logging
- Health check endpoints

## Monitoring

### Metrics Exposed
- Error count by type
- Circuit breaker status
- Feature health status
- Memory usage
- CPU usage
- Event loop lag
- Uptime

### Health Endpoints (if using Express)
- `GET /health` - System health
- `GET /metrics` - Detailed metrics
- `GET /features` - Feature status

## Summary

This architecture provides:
- ✅ Comprehensive error handling
- ✅ Automatic crash recovery
- ✅ Memory leak detection
- ✅ Graceful shutdown
- ✅ Feature lifecycle management
- ✅ Health monitoring
- ✅ Production-ready logging
- ✅ Zero security vulnerabilities

All components work together to create a robust, production-ready system.
