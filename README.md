# the-basics

Autonomous Chimera system with comprehensive infrastructure for trading, freelance AI operations, and platform integration.

Automated consolidation of best parts from:
- ndax-quantum-engine
- quantum-engine-dashb
- shadowforge-ai-trader
- repository-web-app
- The-new-ones

## Quick Start

### System Restoration

To restore and reconfigure the autonomous Chimera system:

1. Go to **Actions** > **Autonomous Chimera System Restoration**
2. Click **Run workflow**
3. Configure restoration options:
   - **Scan mode**: Choose `full` for comprehensive scan
   - **Auto fix**: Enable to automatically fix issues
   - **Restore trading**: Enable to restore trading operations
   - **Restore freelance**: Enable to restore freelance AI jobs
   - **Restore bots**: Enable to restore bot connections
4. Review restoration report in workflow artifacts

See [Chimera Restoration Guide](docs/CHIMERA_RESTORATION.md) for detailed instructions.

### Consolidation

To consolidate code from source repositories:

1. Push this structure to GitHub.
2. Go to Actions > Consolidate Best Parts > Run workflow.
3. Review and use your unified repo!

## Running the NDAX Quantum Trading Bot (CLI)

The bot can be run directly from the command line in several ways.

📖 **[View the Complete CLI Guide](CLI_GUIDE.md)** for detailed instructions and examples.

### Option 1: Using npm script
```bash
npm run bot
```

### Option 2: Direct execution
```bash
node bot.js
```

### Option 3: After global installation
```bash
# From the project directory
npm install -g .
ndax-bot
```

**Note**: This installs the bot globally from the local project directory. You must run this command from within the project root.

### Bot Configuration

Configure the bot using environment variables. 

**Linux/macOS** (using bash/zsh):
```bash
# Trading settings
export TRADING_MODE=paper           # paper or live
export AUTO_START=true              # Auto-start trading
export MAX_TRADES=5                 # Max concurrent trades
export RISK_LEVEL=low              # low, medium, or high

# Freelance settings
export FREELANCE_ENABLED=true
export AUTO_BID=false
export AUTO_EXECUTE=false

# AI settings
export AI_ENABLED=true
export TASK_QUEUE_SIZE=10

# Server settings
export BOT_PORT=9000
```

**Windows** (using Command Prompt):
```cmd
set TRADING_MODE=paper
set AUTO_START=true
set MAX_TRADES=5
rem ... (same variables as above)
```

**Cross-platform** (using .env file):
Create a `.env` file in the project root:
```
TRADING_MODE=paper
AUTO_START=true
MAX_TRADES=5
RISK_LEVEL=low
FREELANCE_ENABLED=true
AI_ENABLED=true
BOT_PORT=9000
```

### Bot Endpoints

Once running, the bot exposes the following HTTP endpoints:

- `http://localhost:9000/status` - Full bot status and configuration
- `http://localhost:9000/health` - Health check and metrics
- `http://localhost:9000/freelance/status` - Freelance orchestrator status
- `http://localhost:9000/trading/status` - Trading engine status
- `http://localhost:9000/tasks/queue` - AI task queue status
- `POST http://localhost:9000/tasks/add` - Add task to AI queue

## Workflows

### 🤖 Autonomous Chimera System Restoration
**File**: `.github/workflows/chimera-system-restore.yml`

Comprehensive system restoration workflow that:
- Scans all platforms (GitHub, Railway, connected services)
- Analyzes configuration and identifies issues
- Generates and executes restoration plan
- Re-establishes bot connections and platform integrations
- Restores trading operations (paper mode)
- Restores freelance AI operations
- Validates system at maximum capacity

**Usage**: Manually trigger from Actions tab with configuration options.

**Documentation**: [docs/CHIMERA_RESTORATION.md](docs/CHIMERA_RESTORATION.md)

### 📦 Consolidate Best Parts
**File**: `.github/workflows/consolidate.yml`

Consolidates code from multiple source repositories into unified structure.

**Usage**: Manually trigger from Actions tab.

## Contents
- `/api` — consolidated APIs
- `/backend` — backend logic including Chimera system
- `/frontend` — UI components
- `/docs` — comprehensive documentation
- `/tests` — test suites
- `/automation` — scripts for consolidation and restoration
- `/backups` — archived original sources
- `/freelance_engine` — AI-based freelance job system
- `/chimera_core` — core Chimera autonomous system

## Usage Instructions

After merging this PR:
1. Navigate to the **Actions** tab in your repository
2. Select the **"Consolidate Best Parts"** or **"Autonomous Chimera System Restoration"** workflow
3. Click **"Run workflow"** button
4. Wait for the automation to complete
5. All source repositories will be backed up and their best parts will be automatically consolidated!

## Source Repositories
This consolidation pulls from the following repositories:
- [ndax-quantum-engine](https://github.com/oconnorw225-del/ndax-quantum-engine)
- [quantum-engine-dashb](https://github.com/oconnorw225-del/quantum-engine-dashb)
- [shadowforge-ai-trader](https://github.com/oconnorw225-del/shadowforge-ai-trader)
- [repository-web-app](https://github.com/oconnorw225-del/repository-web-app)
- [The-new-ones](https://github.com/oconnorw225-del/The-new-ones)

## System Components

### Autonomous Chimera System
Multi-version autonomous system (V4-V8) with:
- Autonomous trading operations
- Self-learning AI
- Multi-chain crypto operations
- Treasury management
- Solvency monitoring

### Freelance Engine
AI-based freelance job operations:
- Job prospecting
- Automated bidding
- Internal coding agent
- Payment handling

### Bot Operations
Automated bot systems for:
- Trading automation
- Platform monitoring
- Task automation

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

## Configuration

### System Configuration
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

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- API keys for exchanges
- Platform tokens (Railway, GitHub)
- Trading parameters
- Bot configurations

## Documentation

- [Chimera Restoration Guide](docs/CHIMERA_RESTORATION.md) - System restoration and recovery
- [Architecture](docs/ARCHITECTURE.md) - System architecture overview
- [Entry Points](docs/ENTRY_POINTS.md) - System entry points guide
- [Runbook](RUNBOOK.md) - Operations runbook
- [Deployment](DEPLOYMENT.md) - Deployment guide
- [Error Handling Guide](docs/ERROR_HANDLING.md) - Error handling patterns
- [Feature Management Guide](docs/FEATURE_MANAGEMENT.md) - Feature lifecycle management
- [System Monitoring Guide](docs/SYSTEM_MONITORING.md) - Health monitoring and metrics

## Key Features

✅ **No Unhandled Errors**: All errors are caught and logged  
✅ **Auto-Recovery**: System recovers from crashes and freezes  
✅ **Graceful Shutdown**: Clean shutdown without data loss  
✅ **Health Monitoring**: Real-time system health dashboard  
✅ **Easy to Extend**: Simple feature registration system  
✅ **Production Ready**: Comprehensive logging and monitoring

## Safety

- Trading operations default to **paper mode**
- All configuration changes are backed up
- Comprehensive validation before declaring success
- Manual approval required for critical operations
