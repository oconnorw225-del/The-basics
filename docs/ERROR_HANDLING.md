# Error Handling Guide

## Overview

The system implements comprehensive error handling across all components with automatic recovery, retry logic, and detailed logging.

## Error Categories

### 1. Network Errors
- **Examples**: Connection timeouts, DNS failures, network unreachable
- **Severity**: Usually recoverable
- **Recovery**: Automatic retry with exponential backoff
- **Timeout**: 30-60 seconds before giving up

### 2. Database Errors
- **Examples**: Connection lost, query timeout, deadlock
- **Severity**: Recoverable
- **Recovery**: Retry with connection reset
- **Timeout**: 3 retries with increasing delays

### 3. API Errors
- **Examples**: 4xx/5xx responses, rate limits, timeout
- **Severity**: Recoverable
- **Recovery**: 
  - 429 (Rate Limit): Back off and retry
  - 5xx: Retry with exponential backoff
  - 4xx: Log and fail (client error)

### 4. Filesystem Errors
- **Examples**: Permission denied, disk full, file not found
- **Severity**: Usually fatal
- **Recovery**: Alert and manual intervention required

### 5. Configuration Errors
- **Examples**: Missing required env vars, invalid config
- **Severity**: Fatal (prevents startup)
- **Recovery**: System won't start; fix configuration

### 6. Security Errors
- **Examples**: Authentication failure, authorization denied
- **Severity**: Fatal
- **Recovery**: Log incident, no automatic retry

## Error Severity Levels

### WARNING
- **Description**: Non-critical issues that don't affect functionality
- **Examples**: 
  - Missing optional configuration
  - Slow response time
  - Temporary resource spike
- **Action**: Log and continue
- **Notification**: None

### RECOVERABLE
- **Description**: Errors that can be automatically recovered
- **Examples**:
  - Network timeout
  - API rate limit hit
  - Temporary service unavailability
- **Action**: Retry with backoff, log attempt count
- **Notification**: After 3 failed retries

### FATAL
- **Description**: Critical errors requiring immediate attention
- **Examples**:
  - Security breach attempt
  - Data corruption
  - Unrecoverable crash
- **Action**: 
  - Generate crash dump
  - Alert administrators
  - Attempt graceful shutdown
- **Notification**: Immediate

## Retry Strategy

### Exponential Backoff

```python
delay = base_delay * (2 ** attempt_number)

# Example:
# Attempt 1: 1 second
# Attempt 2: 2 seconds
# Attempt 3: 4 seconds
# Attempt 4: 8 seconds
```

### Maximum Retries
- **Default**: 3 attempts
- **Configurable**: Via `MAX_RETRIES` environment variable
- **Circuit Breaker**: Opens after 5 failures in 5 minutes

### Jitter
Random jitter added to prevent thundering herd:
```python
actual_delay = delay * (0.5 + random.random() * 0.5)
```

## Circuit Breaker Pattern

### States

1. **CLOSED** (Normal Operation)
   - All requests processed
   - Failures tracked

2. **OPEN** (Failing)
   - Requests immediately fail
   - No actual calls made
   - Prevents cascade failures

3. **HALF-OPEN** (Testing)
   - Limited requests allowed
   - If successful: → CLOSED
   - If failed: → OPEN

### Configuration

```python
# Circuit opens after:
threshold_failures = 5
threshold_window = 300  # seconds (5 minutes)

# Circuit attempts to close after:
cooldown_period = 300  # seconds
```

## Error Handling Patterns

### 1. Try-Catch with Logging

```python
try:
    result = risky_operation()
except Exception as e:
    error_handler.handle_error(
        e,
        context={'operation': 'risky_operation'}
    )
    # Optionally re-raise or return default
```

### 2. Retry Wrapper

```python
result = error_handler.retry_with_backoff(
    function=api_call,
    max_retries=3,
    arg1='value'
)
```

### 3. Graceful Degradation

```python
try:
    return premium_feature()
except Exception as e:
    error_handler.handle_error(e)
    return basic_feature()  # Fallback
```

### 4. Fail-Fast

```python
if not critical_dependency_available():
    raise FatalError("Cannot operate without dependency")
```

## Crash Recovery

### Automatic Recovery Steps

1. **Detect Crash**
   - Process exit monitoring
   - Health check failure
   - Watchdog timeout

2. **Assess Situation**
   - Check circuit breaker status
   - Count recent crashes
   - Evaluate recovery strategy

3. **Attempt Recovery**
   - Restore from checkpoint (if available)
   - Restart process
   - Verify health after restart

4. **If Recovery Fails**
   - Open circuit breaker
   - Alert administrators
   - Log detailed crash information

### Crash Dump Contents

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "process_name": "trading_bot",
  "error_type": "SegmentationFault",
  "error_message": "...",
  "traceback": "...",
  "system_state": {
    "cpu_percent": 45.2,
    "memory_mb": 512,
    "disk_percent": 65
  },
  "process_state": {
    "uptime": 3600,
    "restart_count": 2
  }
}
```

## Freeze Detection

### Detection Methods

1. **Watchdog Timer**
   - Process must reset timer periodically
   - If not reset within timeout → frozen

2. **Heartbeat Monitoring**
   - Process sends heartbeat every N seconds
   - No heartbeat → potential freeze

3. **Resource Monitoring**
   - High CPU + no progress = infinite loop
   - No CPU + no response = deadlock

### Recovery Actions

**Soft Freeze** (60s threshold):
- Log warning
- Monitor for improvement
- Collect diagnostics

**Hard Freeze** (300s threshold):
- Force terminate process
- Generate freeze report
- Restart via crash handler

**Deadlock** (repeated freezes):
- Thread dump (if supported)
- Force kill
- Implement deadlock prevention

## Error Logging

### Log Format

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "ERROR",
  "logger": "trading_bot",
  "message": "API call failed",
  "error_type": "ConnectionError",
  "error_category": "network",
  "severity": "recoverable",
  "context": {
    "endpoint": "/api/trades",
    "attempt": 2,
    "max_retries": 3
  },
  "traceback": "..."
}
```

### Log Locations

- **Main Log**: `.unified-system/logs/unifiedsystem.log`
- **Error Log**: `.unified-system/logs/unifiedsystem_errors.log`
- **Crash Dumps**: `.unified-system/crash-dumps/`

### Log Rotation

- **Max Size**: 10 MB per file
- **Backups**: 5 files retained
- **Compression**: Automatic for old files

## Monitoring & Alerts

### Error Rate Monitoring

```python
# Track error rate
errors_per_minute = errors_last_minute / 60

# Alert if threshold exceeded
if errors_per_minute > 10:
    send_alert("High error rate detected")
```

### Alert Thresholds

- **Warning**: 5 errors/minute
- **Critical**: 10 errors/minute
- **Emergency**: 50 errors/minute or any fatal error

### Alert Channels

1. **Logs**: Always logged
2. **Metrics**: Exposed for Prometheus
3. **Email**: Fatal errors only (if configured)
4. **Slack/Discord**: Critical+ (if configured)

## Best Practices

### 1. Always Categorize Errors
```python
# Good
error_handler.handle_error(
    exception,
    context={'service': 'api', 'endpoint': '/users'}
)

# Bad
print(f"Error: {exception}")
```

### 2. Provide Context
```python
# Include relevant context
context = {
    'user_id': user_id,
    'operation': 'create_order',
    'input_data': sanitize(input_data)
}
```

### 3. Don't Swallow Exceptions
```python
# Good
try:
    risky_operation()
except Exception as e:
    error_handler.handle_error(e)
    raise  # Re-raise if caller needs to know

# Bad
try:
    risky_operation()
except:
    pass  # Silent failure
```

### 4. Use Appropriate Severity
```python
# Fatal for security issues
if not authenticate(user):
    raise SecurityError("Authentication failed")

# Recoverable for transient failures
if api_timeout():
    raise RecoverableError("API timeout")
```

### 5. Implement Timeouts
```python
# Always set timeouts
response = requests.get(url, timeout=30)

# For async operations
result = await asyncio.wait_for(
    async_operation(),
    timeout=60.0
)
```

## Testing Error Handling

### Unit Tests

```python
def test_retry_mechanism():
    call_count = [0]
    
    def failing_function():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ValueError("Temporary failure")
        return "success"
    
    result = error_handler.retry_with_backoff(
        failing_function,
        max_retries=3
    )
    
    assert result == "success"
    assert call_count[0] == 3
```

### Integration Tests

```python
def test_crash_recovery():
    # Simulate crash
    process_manager.crash_process("test_service")
    
    # Wait for recovery
    time.sleep(5)
    
    # Verify recovered
    status = process_manager.get_status("test_service")
    assert status == ProcessState.RUNNING
```

### Chaos Testing

```python
def test_network_partition():
    # Simulate network failure
    block_network()
    
    try:
        # System should handle gracefully
        result = make_api_call()
        assert result is None  # Returns None instead of crashing
    finally:
        restore_network()
```

## Troubleshooting

### High Error Rate

1. Check error logs for patterns
2. Review recent deployments/changes
3. Verify external service status
4. Check resource utilization
5. Examine circuit breaker states

### Process Keeps Crashing

1. Review crash dumps
2. Check resource limits
3. Verify dependencies available
4. Look for memory leaks
5. Check for infinite retry loops

### Frozen Processes

1. Check freeze detection logs
2. Review CPU/memory usage
3. Look for deadlock indicators
4. Check external service response times
5. Verify timeout configurations

### Circuit Breaker Always Open

1. Identify root cause of failures
2. Fix underlying issue
3. Reset circuit breaker manually:
   ```python
   crash_handler.circuit_open.pop(service_name)
   ```
4. Monitor for stability

## Configuration Reference

### Environment Variables

```bash
# Error handling
MAX_RETRIES=3
RETRY_BACKOFF_BASE=2.0
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=300

# Monitoring
HEALTH_CHECK_INTERVAL=60
FREEZE_SOFT_THRESHOLD=60
FREEZE_HARD_THRESHOLD=300

# Logging
LOG_LEVEL=INFO
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

### Programmatic Configuration

```python
error_handler = ErrorHandler(
    max_retries=3,
    retry_delay=1.0,
    exponential_backoff=True,
    crash_dump_dir=".unified-system/crash-dumps"
)
```

## Additional Resources

- [Architecture Documentation](ARCHITECTURE.md)
- [Monitoring Guide](MONITORING.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
