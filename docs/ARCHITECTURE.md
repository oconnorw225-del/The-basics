# System Architecture

## Overview

The-basics is a comprehensive autonomous system that integrates trading, freelance, and AI capabilities with robust error handling, monitoring, and recovery mechanisms.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Start System (start_system.py)           │
│           Orchestrates all components and lifecycle         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Core Systems Layer                      │
├─────────────────────────────────────────────────────────────┤
│  • Unified Logger        • Config Manager                   │
│  • Error Handler         • Process Manager                  │
│  • Health Monitor        • Service Orchestrator             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Recovery & Resilience Layer                │
├─────────────────────────────────────────────────────────────┤
│  • Crash Handler         • Freeze Detector                  │
│  • Reload Manager        • Auto-Recovery                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Integration Layer                 │
├─────────────────────────────────────────────────────────────┤
│  • AI Manager            • API Gateway                      │
│  • Message Queue         • Metrics Collector                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Application Services                    │
├─────────────────────────────────────────────────────────────┤
│  • Python Backend (port 8000)                               │
│  • Node.js Server (port 3000)                               │
│  • Trading Bot    (port 9000)                               │
│  • Frontend (React)                                          │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Core Systems Layer

#### Unified Logger (`src/logging/logger.py`)
- **Purpose**: Centralized logging across all components
- **Features**:
  - Structured JSON logging
  - Multiple log levels (DEBUG, INFO, WARN, ERROR, FATAL)
  - Context injection for request tracking
  - Log rotation with configurable size limits
  - Separate error log files
  - Metric logging support

#### Config Manager (`src/config/manager.py`)
- **Purpose**: Single source of truth for configuration
- **Features**:
  - Loads from `.env` files and environment variables
  - Environment-specific configs (dev/staging/prod)
  - Type conversion and validation
  - Service configuration management
  - Port conflict detection
  - Secret management

#### Error Handler (`src/error_handler.py`)
- **Purpose**: Global error handling and recovery
- **Features**:
  - Error categorization (network, database, API, etc.)
  - Severity assessment (warning, recoverable, fatal)
  - Automatic retry with exponential backoff
  - Crash dump generation
  - Error statistics tracking
  - Notification system

#### Health Monitor (`src/health_monitor.py`)
- **Purpose**: System health monitoring and alerting
- **Features**:
  - Process heartbeat monitoring
  - System resource tracking (CPU, memory, disk)
  - Freeze detection
  - Network connectivity checks
  - Auto-recovery triggers
  - Continuous monitoring thread

#### Process Manager (`src/process_manager.py`)
- **Purpose**: Process lifecycle management
- **Features**:
  - Register and manage processes
  - Graceful startup and shutdown
  - Auto-restart on crash
  - Health check integration
  - Signal handling (SIGTERM, SIGINT)
  - Process status tracking

### 2. Recovery & Resilience Layer

#### Crash Handler (`src/recovery/crash_handler.py`)
- **Purpose**: Crash detection and recovery
- **Features**:
  - Multiple recovery strategies
  - Circuit breaker pattern
  - State checkpoint/restore
  - Exponential backoff retries
  - Crash history tracking

#### Freeze Detector (`src/recovery/freeze_detector.py`)
- **Purpose**: Detect and recover from process freezes
- **Features**:
  - Watchdog timers
  - Deadlock detection
  - Soft vs hard freeze classification
  - Auto-recovery mechanisms
  - Activity monitoring

#### Reload Manager (`src/recovery/reload_manager.py`)
- **Purpose**: Hot reload without downtime
- **Features**:
  - Module hot-reloading
  - Configuration reload
  - State preservation
  - Rollback support
  - Auto-reload monitoring

### 3. Service Integration Layer

#### AI Manager (`src/ai/manager.py`)
- **Purpose**: Coordinate all AI components
- **Features**:
  - Task queue with priority levels
  - Rate limiting
  - Cost tracking
  - Multiple AI component support
  - Task retry logic
  - Dead letter queue

#### API Gateway (`src/api/gateway.py`)
- **Purpose**: Unified API entry point
- **Features**:
  - Route management
  - Rate limiting per client
  - Request validation
  - Middleware support
  - Statistics tracking

#### Message Queue (`src/messaging/queue.py`)
- **Purpose**: Inter-service communication
- **Features**:
  - Publish/subscribe pattern
  - Request/response pattern
  - Priority queues
  - Dead letter queue
  - Message persistence

#### Metrics Collector (`src/monitoring/metrics.py`)
- **Purpose**: Performance and business metrics
- **Features**:
  - Counter, gauge, histogram metrics
  - System resource metrics
  - Process-specific metrics
  - Time series data storage
  - Prometheus export format

### 4. Service Orchestrator

#### Orchestrator (`src/orchestrator.py`)
- **Purpose**: Service coordination and startup order
- **Features**:
  - Dependency resolution
  - Ordered startup/shutdown
  - Service state management
  - Restart capabilities

## Data Flow

### Startup Flow

```
1. start_system.py initializes core systems
2. Configuration loaded from environment/files
3. Logger, error handler, health monitor initialized
4. Process manager registers all services
5. Services started in dependency order:
   - Database connections
   - Message queues
   - Python backend
   - Node.js services
   - Trading bot
   - Frontend
6. Health monitoring activated
7. Recovery systems enabled
8. System ready
```

### Error Recovery Flow

```
1. Error occurs in component
2. Error handler categorizes and assesses severity
3. If recoverable:
   - Retry with exponential backoff
   - Log and track statistics
4. If fatal:
   - Generate crash dump
   - Trigger notifications
   - Attempt recovery via crash handler
5. Crash handler evaluates:
   - Circuit breaker status
   - Recovery strategy
   - Retry count
6. Recovery attempted:
   - Restore from checkpoint
   - Restart process
   - Monitor for success
```

### Health Monitoring Flow

```
1. Continuous monitoring loop runs
2. Every N seconds:
   - Check process heartbeats
   - Monitor system resources
   - Verify service health endpoints
3. Issues detected:
   - Log warnings/errors
   - Update health status
   - Trigger recovery if needed
4. Recovery actions:
   - Restart frozen processes
   - Alert on critical failures
   - Update metrics
```

## Technology Stack

### Backend
- **Python 3.8+**: Core system components
- **FastAPI**: REST API framework
- **psutil**: System monitoring
- **httpx**: Async HTTP client

### Frontend
- **React 18**: UI framework
- **Vite**: Build tool
- **React Router**: Navigation

### Node.js Services
- **Express**: Web server
- **Node 18+**: Runtime

### Infrastructure
- **Railway**: Deployment platform
- **Terraform**: Infrastructure as code
- **GitHub Actions**: CI/CD

## Configuration

### Environment Variables

Core system:
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARN, ERROR)
- `NODE_ENV`: Environment (development, staging, production)
- `HEALTH_CHECK_INTERVAL`: Health check interval in seconds

Service ports:
- `PORT`: Node server port (default: 3000)
- `PYTHON_PORT`: Python backend port (default: 8000)
- `BOT_PORT`: Trading bot port (default: 9000)

Service features:
- `BOT_ENABLED`: Enable trading bot (true/false)
- `TRADING_MODE`: Trading mode (paper/live)
- `FREELANCE_ENABLED`: Enable freelance features
- `AI_ENABLED`: Enable AI task processing

See `.env.example` for full list.

## Monitoring & Observability

### Logs
- Location: `.unified-system/logs/`
- Format: Structured JSON (configurable)
- Rotation: 10MB files, 5 backups
- Separate error logs

### Metrics
- System: CPU, memory, disk, network
- Application: Requests, latency, errors
- Business: AI tasks, trades, revenue
- Export: Prometheus format

### Health Checks
- Endpoint: `/health` on each service
- System health: Aggregated from all services
- Resource monitoring: Real-time thresholds

## Security

### Process Isolation
- Each service runs in separate process
- Limited environment variable exposure
- No shell interpretation in subprocess calls

### Input Validation
- Rate limiting on API endpoints
- Request size limits
- Input sanitization
- Task validation before execution

### Error Handling
- Safe error messages (no stack traces in production)
- Crash dumps stored securely
- Sensitive data not logged

## Scalability

### Horizontal Scaling
- Stateless service design
- Message queue for async tasks
- Load balancing support

### Vertical Scaling
- Resource monitoring and alerts
- Auto-tuning based on load
- Configurable concurrency limits

## Disaster Recovery

### Backup
- State checkpoints
- Configuration backups
- Crash dump retention

### Recovery
- Automatic process restart
- Circuit breaker prevents cascade failures
- Graceful degradation

### Failover
- Health-based routing
- Redundancy for critical services
- State restoration from checkpoints
