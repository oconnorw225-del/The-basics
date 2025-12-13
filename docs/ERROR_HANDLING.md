# Error Handling and Recovery Guide

## Overview

The-basics system includes comprehensive error handling and recovery mechanisms to ensure high availability and automatic recovery from failures.

## Components

### 1. Global Error Handler (`src/core/error-handler.js`)
### 2. Recovery System (`src/core/recovery-system.py`)
### 3. Freeze Detector (`src/core/freeze-detector.js`)

---

## Global Error Handler

### Features

- **Uncaught Exception Handling**: Catches all uncaught exceptions
- **Promise Rejection Handling**: Handles unhandled promise rejections
- **Auto-Restart**: Automatically restarts the process on critical errors
- **Error Logging**: Logs errors with rotation
- **Alert System**: Sends alerts on critical errors
- **Graceful Degradation**: Disables non-critical features on error

### Usage

```javascript
const { ErrorHandler } = require('./src/core/error-handler');

// Initialize with options
const errorHandler = ErrorHandler.getInstance({
  logDir: '.unified-system/logs',
  maxLogSize: 10 * 1024 * 1024,  // 10MB
  maxLogFiles: 5,
  enableAutoRestart: true,
  restartDelay: 5000,
  criticalErrorThreshold: 5,
  alertWebhook: process.env.ALERT_WEBHOOK_URL
});

// Listen to events
errorHandler.on('criticalError', (errorInfo) => {
  console.log('Critical error occurred:', errorInfo);
  // Send notification, log to external service, etc.
});

errorHandler.on('beforeRestart', (errorInfo) => {
  console.log('System is restarting...');
  // Clean up resources
});

// Manual error reporting
try {
  // Your code
} catch (error) {
  errorHandler.reportError('module-name', error, 'critical');
}

// Graceful degradation
errorHandler.degradeGracefully(['trading', 'ai-platforms']);

// Get error statistics
const stats = errorHandler.getStats();
console.log('Total errors:', stats.totalErrors);
console.log('Critical errors:', stats.criticalErrors);
```

### Configuration

```javascript
{
  // Log directory
  logDir: '.unified-system/logs',
  
  // Maximum log file size before rotation
  maxLogSize: 10 * 1024 * 1024,
  
  // Number of log files to keep
  maxLogFiles: 5,
  
  // Enable automatic restart on critical errors
  enableAutoRestart: true,
  
  // Delay before restarting (milliseconds)
  restartDelay: 5000,
  
  // Maximum critical errors before giving up
  criticalErrorThreshold: 5,
  
  // Webhook URL for alerts (Slack, Discord, etc.)
  alertWebhook: 'https://hooks.slack.com/...'
}
```

### Log Rotation

Logs are automatically rotated when they exceed `maxLogSize`. Old logs are renamed with a numeric suffix (.1, .2, etc.), and the oldest logs beyond `maxLogFiles` are deleted.

Log files:
- `errors.log` - All errors
- `warnings.log` - System warnings
- `degradation.log` - Graceful degradation events

---

## Recovery System

### Features

- **State Persistence**: Save system state to disk
- **Checkpoint/Restore**: Create and restore from checkpoints
- **Auto-Recovery**: Automatically recover from crashes
- **Database Recovery**: Reconnect to databases on failure
- **Retry Logic**: Exponential backoff retry for failed operations
- **Transaction Rollback**: Automatic rollback on database errors

### Usage

```python
from src.core.recovery_system import RecoverySystem, auto_checkpoint

# Initialize
recovery = RecoverySystem({
    'checkpoint_dir': '.unified-system/checkpoints',
    'max_checkpoints': 10,
    'retry_attempts': 3,
    'retry_delay': 5
})

# Create checkpoint
recovery.create_checkpoint(
    state_type='trading',
    data={'positions': positions, 'balance': balance},
    metadata={'timestamp': datetime.now().isoformat()}
)

# Restore from checkpoint
restored = recovery.restore_checkpoint('trading')
if restored:
    positions = restored['data']['positions']
    balance = restored['data']['balance']

# Retry with exponential backoff
def risky_operation():
    # Operation that might fail
    return api.call()

try:
    result = recovery.retry_with_backoff(risky_operation)
except Exception as e:
    print(f"Operation failed after all retries: {e}")

# Database transaction with rollback
def database_operation(conn):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trades ...")
    return cursor.lastrowid

conn = get_database_connection()
try:
    result = recovery.with_transaction_rollback(database_operation, conn)
except Exception as e:
    print(f"Transaction rolled back: {e}")

# Async retry
async def async_operation():
    return await api.async_call()

result = await recovery.async_retry_with_backoff(async_operation)

# Auto-checkpoint decorator
@auto_checkpoint('trading', recovery)
def execute_trade(trade_data):
    # This function's state will be automatically checkpointed
    result = process_trade(trade_data)
    return result
```

### Database Schema

The recovery system uses SQLite to persist state:

```sql
-- Checkpoints table
CREATE TABLE checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    state_type TEXT NOT NULL,
    data TEXT NOT NULL,
    metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Recovery log table
CREATE TABLE recovery_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    recovery_type TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Configuration

```python
{
    # Directory to store checkpoints
    'checkpoint_dir': '.unified-system/checkpoints',
    
    # Maximum number of checkpoints per state type
    'max_checkpoints': 10,
    
    # Number of retry attempts
    'retry_attempts': 3,
    
    # Base retry delay in seconds
    'retry_delay': 5
}
```

### Checkpoint Management

```python
# Get checkpoint history
history = recovery.get_checkpoint_history('trading', limit=10)
for checkpoint in history:
    print(f"Checkpoint at {checkpoint['timestamp']}")
    print(f"Metadata: {checkpoint['metadata']}")

# Get recovery log
logs = recovery.get_recovery_log(limit=50)
for log in logs:
    print(f"{log['timestamp']} - {log['type']}: {log['status']}")
```

---

## Freeze Detector

### Features

- **Watchdog Timer**: Detects system freezes
- **Deadlock Detection**: Identifies deadlocked components
- **Memory Leak Detection**: Monitors memory usage trends
- **CPU Monitoring**: Tracks CPU utilization
- **Health Checks**: Runs registered health check functions
- **Auto-Reload**: Triggers restart on freeze detection

### Usage

```javascript
const { FreezeDetector } = require('./src/core/freeze-detector');

// Initialize
const detector = FreezeDetector.getInstance({
  heartbeatInterval: 5000,      // 5 seconds
  freezeThreshold: 30000,       // 30 seconds
  memoryLeakThreshold: 0.9,     // 90% of heap
  cpuThreshold: 0.95,           // 95% CPU
  checkInterval: 10000,         // 10 seconds
  enableAutoReload: true
});

// Start monitoring
detector.start();

// Register health checks
detector.registerHealthCheck('database', async () => {
  const result = await db.ping();
  if (!result) throw new Error('Database not responding');
  return true;
}, 5000); // 5 second timeout

detector.registerHealthCheck('api', async () => {
  const response = await fetch('http://localhost:8000/health');
  if (!response.ok) throw new Error('API not responding');
  return true;
});

// Listen to events
detector.on('freeze', (freezeInfo) => {
  console.error('System freeze detected!', freezeInfo);
  // Emergency actions
});

detector.on('memoryLeak', (leakInfo) => {
  console.error('Memory leak detected!', leakInfo);
  // Cleanup actions
});

detector.on('deadlock', (deadlockInfo) => {
  console.error('Deadlock detected!', deadlockInfo);
  // Recovery actions
});

detector.on('health', (healthStatus) => {
  console.log('Health check:', healthStatus.healthy);
});

detector.on('autoReload', (reloadInfo) => {
  console.log('System is being reloaded...');
  // Cleanup before reload
});

// Get health status
const status = detector.getHealthStatus();
console.log('System healthy:', status.healthy);
console.log('Frozen components:', status.frozenComponents);

// Get statistics
const stats = detector.getStats();
console.log('Memory trend:', stats.heapStats.trend);

// Stop monitoring
detector.stop();
```

### Configuration

```javascript
{
  // Heartbeat interval (milliseconds)
  heartbeatInterval: 5000,
  
  // Time without heartbeat before considering frozen (milliseconds)
  freezeThreshold: 30000,
  
  // Memory usage threshold (0.0 - 1.0)
  memoryLeakThreshold: 0.9,
  
  // CPU usage threshold (0.0 - 1.0)
  cpuThreshold: 0.95,
  
  // Health check interval (milliseconds)
  checkInterval: 10000,
  
  // Enable automatic reload on freeze
  enableAutoReload: true,
  
  // Health check timeout (milliseconds)
  healthCheckTimeout: 5000
}
```

### Exit Codes

The freeze detector uses specific exit codes:
- `2` - System freeze detected
- `3` - Memory leak critical
- `4` - Deadlock detected

These can be used in process managers (systemd, pm2, etc.) to determine restart behavior.

---

## Integration Example

Complete integration of all error handling components:

```javascript
// server.js
const { ErrorHandler } = require('./src/core/error-handler');
const { FreezeDetector } = require('./src/core/freeze-detector');

// Initialize error handler
const errorHandler = ErrorHandler.getInstance({
  enableAutoRestart: true,
  alertWebhook: process.env.ALERT_WEBHOOK_URL
});

// Initialize freeze detector
const freezeDetector = FreezeDetector.getInstance({
  enableAutoReload: true
});

// Register health checks
freezeDetector.registerHealthCheck('database', async () => {
  await db.ping();
  return true;
});

// Start monitoring
freezeDetector.start();

// Handle graceful shutdown
errorHandler.on('shutdown', (signal) => {
  freezeDetector.stop();
  // Cleanup resources
});

// Start application
const app = express();
// ... application code ...
```

```python
# unified_system.py
from src.core.recovery_system import RecoverySystem

# Initialize recovery system
recovery = RecoverySystem()

# Create checkpoint before critical operation
recovery.create_checkpoint('system', {
    'config': config,
    'state': current_state
})

# Retry API calls with backoff
def api_call():
    return requests.get('https://api.example.com/data')

try:
    result = recovery.retry_with_backoff(api_call)
except Exception as e:
    # Restore from last checkpoint
    restored = recovery.restore_checkpoint('system')
    if restored:
        config = restored['data']['config']
        current_state = restored['data']['state']
```

---

## Best Practices

### 1. Error Handling

- Use try-catch blocks for all risky operations
- Log errors with appropriate context
- Report critical errors immediately
- Implement graceful degradation
- Set up alerts for critical errors

### 2. Checkpointing

- Create checkpoints before critical operations
- Don't checkpoint too frequently (performance impact)
- Include relevant metadata
- Clean up old checkpoints
- Test restore functionality

### 3. Health Checks

- Register health checks for all critical components
- Set appropriate timeouts
- Include database, API, and service checks
- Monitor health status
- Act on health failures

### 4. Monitoring

- Monitor error rates
- Track memory usage trends
- Watch CPU utilization
- Check log file sizes
- Review recovery logs

### 5. Testing

- Test error scenarios
- Verify auto-restart works
- Test checkpoint restore
- Simulate system freezes
- Test health checks

---

## Troubleshooting

### System Keeps Restarting

**Cause**: Critical errors occurring repeatedly

**Solutions**:
1. Check error logs: `.unified-system/logs/errors.log`
2. Review recent code changes
3. Check resource limits (memory, CPU)
4. Verify database connectivity
5. Disable auto-restart temporarily to debug

### Checkpoints Not Being Created

**Cause**: Permission issues or disk space

**Solutions**:
1. Check directory permissions: `.unified-system/checkpoints`
2. Verify disk space
3. Check recovery logs
4. Ensure SQLite is installed

### Health Checks Failing

**Cause**: Service not running or misconfigured

**Solutions**:
1. Verify service is running
2. Check health check timeout
3. Review health check logic
4. Check network connectivity
5. Increase timeout if needed

### Memory Leak Warnings

**Cause**: Actual memory leak or configuration issue

**Solutions**:
1. Review memory usage history
2. Check for memory leaks in code
3. Adjust `memoryLeakThreshold` if needed
4. Force garbage collection
5. Restart service if necessary

---

## Monitoring Dashboard

View system health in real-time:

```bash
# Run health check
./scripts/health-check.sh --verbose

# View error logs
tail -f .unified-system/logs/errors.log

# Check recovery logs
sqlite3 .unified-system/checkpoints/state.db \
  "SELECT * FROM recovery_log ORDER BY created_at DESC LIMIT 10"

# Monitor memory
node -e "
const detector = require('./src/core/freeze-detector').getInstance();
detector.start();
detector.on('memoryCheck', (info) => console.log(info));
"
```

---

## Support

For issues with error handling and recovery:
1. Check logs in `.unified-system/logs/`
2. Review recovery logs in database
3. Enable verbose logging
4. Test components individually
5. Check GitHub issues for similar problems
