# Unified System Management

## Quick Start

### Start the Entire System

```bash
# Start all services with monitoring and auto-recovery
python3 start_system.py
```

This single command will:
- ✅ Initialize all core systems (logging, config, error handling)
- ✅ Validate environment and configuration
- ✅ Start all services in correct dependency order
- ✅ Enable health monitoring and auto-recovery
- ✅ Provide real-time system status

### Prerequisites

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install Node.js dependencies
npm install
```

### Configuration

Create a `.env` file based on `.env.example`:

```bash
# Core Configuration
NODE_ENV=development
LOG_LEVEL=INFO

# Service Ports
PORT=3000                # Node server
PYTHON_PORT=8000        # Python backend
BOT_PORT=9000           # Trading bot

# Service Features
BOT_ENABLED=true
TRADING_MODE=paper
FREELANCE_ENABLED=false
AI_ENABLED=false

# Monitoring
HEALTH_CHECK_INTERVAL=60
```

## System Components

### Core Systems

1. **Unified Logger** (`src/logging/logger.py`)
   - Centralized logging with JSON formatting
   - Automatic log rotation
   - Context injection for request tracking

2. **Config Manager** (`src/config/manager.py`)
   - Environment-based configuration
   - Port conflict detection
   - Type-safe access to settings

3. **Error Handler** (`src/error_handler.py`)
   - Automatic error categorization
   - Retry with exponential backoff
   - Crash dump generation

4. **Health Monitor** (`src/health_monitor.py`)
   - Process heartbeat monitoring
   - System resource tracking
   - Auto-recovery triggers

5. **Process Manager** (`src/process_manager.py`)
   - Process lifecycle management
   - Graceful startup/shutdown
   - Auto-restart on crash

### Recovery & Resilience

6. **Crash Handler** (`src/recovery/crash_handler.py`)
   - Crash detection and recovery
   - Circuit breaker pattern
   - State checkpointing

7. **Freeze Detector** (`src/recovery/freeze_detector.py`)
   - Watchdog timers
   - Deadlock detection
   - Automatic process termination

8. **Reload Manager** (`src/recovery/reload_manager.py`)
   - Hot reload without downtime
   - Configuration reload
   - Rollback support

### Integration Layer

9. **AI Manager** (`src/ai/manager.py`)
   - Task queue with priorities
   - Rate limiting
   - Cost tracking

10. **API Gateway** (`src/api/gateway.py`)
    - Unified API entry point
    - Rate limiting
    - Request validation

11. **Message Queue** (`src/messaging/queue.py`)
    - Inter-service messaging
    - Pub/sub pattern
    - Dead letter queue

12. **Metrics Collector** (`src/monitoring/metrics.py`)
    - System and application metrics
    - Prometheus export
    - Time series data

## Usage Examples

### Basic Usage

```python
from src.logging.logger import create_logger
from src.config.manager import create_config_manager
from src.error_handler import create_error_handler

# Initialize
logger = create_logger()
config = create_config_manager()
error_handler = create_error_handler(logger=logger)

# Use error handling
try:
    risky_operation()
except Exception as e:
    error_handler.handle_error(e, context={'operation': 'example'})
```

### Advanced: Custom Service Integration

```python
from src.process_manager import create_process_manager
from src.health_monitor import create_health_monitor

# Initialize
pm = create_process_manager()
health = create_health_monitor()

# Register a service
pm.register_process(
    name='my_service',
    command=['python3', 'my_service.py'],
    auto_restart=True
)

# Register health monitoring
health.register_process(
    name='my_service',
    port=8080,
    health_endpoint='http://localhost:8080/health'
)

# Start service
pm.start_process('my_service')

# Monitor health
health.start_monitoring()
```

### AI Task Processing

```python
from src.ai.manager import create_ai_manager, TaskPriority

# Initialize
ai_manager = create_ai_manager()

# Register handler
async def process_task(data):
    # Your AI processing logic
    return {'result': 'success'}

ai_manager.register_task_handler('analysis', process_task)

# Queue task
task_id = ai_manager.queue_task(
    task_type='analysis',
    data={'input': 'data'},
    priority=TaskPriority.HIGH
)

# Execute
await ai_manager.execute_task(ai_manager.get_next_task())
```

### Metrics Collection

```python
from src.monitoring.metrics import create_metrics_collector, MetricType

# Initialize
metrics = create_metrics_collector()

# Register metrics
metrics.register_metric(
    'api_requests',
    MetricType.COUNTER,
    description='Total API requests'
)

# Record values
metrics.increment('api_requests')
metrics.set_gauge('active_users', 42)
metrics.observe('response_time_ms', 123.4)

# Get statistics
stats = metrics.get_statistics('response_time_ms')
```

## Monitoring

### Health Check

All services expose health endpoints:

```bash
# Node server
curl http://localhost:3000/health

# Python backend  
curl http://localhost:8000/health

# Trading bot
curl http://localhost:9000/health
```

### System Status

View overall system status:

```python
from start_system import SystemOrchestrator

orchestrator = SystemOrchestrator()
if orchestrator.start():
    status = orchestrator.health_monitor.get_health_status()
    print(status)
```

### Logs

Logs are stored in `.unified-system/logs/`:
- `unifiedsystem.log` - All logs
- `unifiedsystem_errors.log` - Error logs only

### Metrics

Export Prometheus metrics:

```python
from src.monitoring.metrics import create_metrics_collector

metrics = create_metrics_collector()
print(metrics.export_prometheus())
```

## Testing

### Run All Tests

```bash
# Unit tests
python3 -m unittest discover tests -v

# Integration tests
python3 -m unittest tests.integration.test_system_startup -v
python3 -m unittest tests.integration.test_error_recovery -v
python3 -m unittest tests.integration.test_health_monitoring -v
```

### Test Specific Component

```bash
# Test error handling
python3 -m unittest tests.integration.test_error_recovery -v
```

## Troubleshooting

### System Won't Start

1. Check configuration:
   ```bash
   python3 -c "from src.config.manager import create_config_manager; print(create_config_manager())"
   ```

2. Verify all dependencies installed:
   ```bash
   pip3 install -r requirements.txt
   npm install
   ```

3. Check port availability:
   ```bash
   lsof -i :3000
   lsof -i :8000
   lsof -i :9000
   ```

### Service Keeps Crashing

1. Check crash dumps:
   ```bash
   ls -la .unified-system/crash-dumps/
   ```

2. Review error logs:
   ```bash
   tail -f .unified-system/logs/unifiedsystem_errors.log
   ```

3. Check recovery statistics:
   ```python
   from src.recovery.crash_handler import create_crash_handler
   handler = create_crash_handler()
   print(handler.get_crash_statistics())
   ```

### High Resource Usage

1. Check system metrics:
   ```python
   from src.monitoring.metrics import create_metrics_collector
   metrics = create_metrics_collector()
   print(metrics.collect_system_metrics())
   ```

2. Review process metrics:
   ```python
   print(metrics.collect_process_metrics())
   ```

### Process Frozen

The freeze detector should automatically handle this, but to check manually:

```python
from src.recovery.freeze_detector import create_freeze_detector
detector = create_freeze_detector()
print(detector.get_freeze_statistics())
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## Error Handling

See [docs/ERROR_HANDLING.md](docs/ERROR_HANDLING.md) for comprehensive error handling guide.

## Development

### Adding a New Service

1. Register in config manager:
   ```python
   config.services['new_service'] = ServiceConfig(
       name='new_service',
       port=9001,
       enabled=True,
       auto_start=True
   )
   ```

2. Register in process manager:
   ```python
   pm.register_process(
       name='new_service',
       command=['python3', 'new_service.py'],
       auto_restart=True
   )
   ```

3. Add health monitoring:
   ```python
   health.register_process(
       name='new_service',
       port=9001,
       health_endpoint='http://localhost:9001/health'
   )
   ```

4. Register crash recovery:
   ```python
   crash_handler.register_process('new_service')
   freeze_detector.register_watchdog('new_service')
   ```

### Adding New Metrics

```python
from src.monitoring.metrics import MetricType

# Register
metrics.register_metric(
    'my_metric',
    MetricType.COUNTER,
    description='My custom metric'
)

# Use
metrics.increment('my_metric')
```

### Custom Error Handling

```python
from src.error_handler import ErrorCategory, ErrorSeverity

# Define custom handler
def my_error_handler(error_record):
    if error_record['severity'] == 'fatal':
        # Send alert
        pass

# Register
error_handler.add_notification_handler(my_error_handler)
```

## Performance

### Benchmarks

- **Startup Time**: ~3-5 seconds for all services
- **Health Check**: <100ms
- **Error Handling Overhead**: <1ms
- **Metric Collection**: <50ms
- **Log Write**: <5ms

### Optimization Tips

1. **Reduce Log Level in Production**:
   ```bash
   LOG_LEVEL=WARN
   ```

2. **Adjust Health Check Interval**:
   ```bash
   HEALTH_CHECK_INTERVAL=120  # 2 minutes
   ```

3. **Tune Process Limits**:
   ```bash
   MAX_CONCURRENT_TASKS=10
   API_RATE_LIMIT=200
   ```

## Security

- All file operations use safe methods
- Input validation on all API endpoints
- Rate limiting prevents abuse
- No shell interpretation in subprocess calls
- Sensitive data not logged
- Crash dumps exclude secrets

## Contributing

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Check for security vulnerabilities

## License

MIT

## Support

For issues and questions:
- Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Review logs in `.unified-system/logs/`
- Open an issue on GitHub
