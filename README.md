# the-basics

Automated consolidation of best parts from:
- ndax-quantum-engine
- quantum-engine-dashb
- shadowforge-ai-trader
- repository-web-app
- The-new-ones

## How To Use

1. Push this structure to GitHub.
2. Go to Actions > Consolidate Best Parts > Run workflow.
3. Review and use your unified repo!

## Contents
- `/api` — consolidated APIs
- `/backend` — backend logic
- `/frontend` — UI components
- `/docs` — documentation
- `/tests` — test suites
- `/automation` — scripts for consolidation
- `/backups` — archived original sources

## Running the Consolidation

Once this repository is set up:
1. Navigate to the **Actions** tab in GitHub
2. Select **"Consolidate Best Parts"** workflow
3. Click **"Run workflow"**
4. The automation will clone all source repositories, back them up, and consolidate the best parts

All source repositories will be backed up and the best parts will be consolidated automatically!

## System Architecture

### Core Systems

The application includes a comprehensive error handling and feature management system:

#### Error Handling (`src/core/ErrorHandler.js`)
- **Automatic Error Recovery**: Catches uncaught exceptions and unhandled rejections
- **Circuit Breaker Pattern**: Prevents cascading failures with external services
- **Retry Logic**: Exponential backoff for transient failures
- **Error Logging**: Detailed error logs with context and statistics
- **Graceful Degradation**: System continues with working features when non-critical features fail

[📖 Read the Error Handling Guide](docs/ERROR_HANDLING.md)

#### Feature Management (`src/core/FeatureManager.js`)
- **Centralized Registry**: Track all features (AI, trading, freelance, payments, etc.)
- **Lifecycle Management**: Initialize, start, stop features with proper dependency ordering
- **Dynamic Control**: Enable/disable features at runtime
- **Health Monitoring**: Track health and performance of each feature
- **Dependency Resolution**: Automatic startup order based on dependencies

[📖 Read the Feature Management Guide](docs/FEATURE_MANAGEMENT.md)

#### Health Monitor (`src/core/HealthMonitor.js`)
- **Freeze Detection**: Detects when system stops responding
- **Memory Leak Detection**: Tracks memory usage and identifies leaks
- **Performance Monitoring**: CPU, memory, event loop lag
- **Auto-Recovery**: Automatic restart on unhealthy state (configurable)
- **Heartbeat Monitoring**: Regular system health checks

[📖 Read the System Monitoring Guide](docs/SYSTEM_MONITORING.md)

#### Process Linker (`src/core/ProcessLinker.js`)
- **Service Discovery**: Components register and discover each other
- **Dependency Resolution**: Initialize services in correct order
- **Event Bus**: Centralized event system for inter-component communication
- **State Synchronization**: Share state between components

#### Shutdown Handler (`src/core/ShutdownHandler.js`)
- **Graceful Shutdown**: Clean shutdown of all components
- **Signal Handling**: SIGTERM, SIGINT, SIGHUP support
- **Operation Completion**: Waits for in-flight operations
- **Cleanup Hooks**: Extensible shutdown hooks for cleanup tasks

### Configuration

System configuration is centralized in `config/error-handling.json`:

```json
{
  "errorHandler": {
    "maxRetries": 3,
    "retryDelay": 1000,
    "circuitBreakerThreshold": 5
  },
  "healthMonitor": {
    "heartbeatInterval": 5000,
    "memoryThreshold": 0.9,
    "autoRestart": true
  },
  "features": {
    "trading": { "enabled": false, "critical": false },
    "freelance": { "enabled": true, "critical": true },
    "ai": { "enabled": true, "critical": true }
  }
}
```

### Key Features

✅ **No Unhandled Errors**: All errors are caught and logged  
✅ **Auto-Recovery**: System recovers from crashes and freezes  
✅ **Graceful Shutdown**: Clean shutdown without data loss  
✅ **Health Monitoring**: Real-time system health dashboard  
✅ **Easy to Extend**: Simple feature registration system  
✅ **Production Ready**: Comprehensive logging and monitoring
