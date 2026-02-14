# Troubleshooting Guide

## Common Issues and Solutions

### Bot Issues

#### Bot Won't Start

**Symptoms**: Bot remains in "stopped" status

**Possible Causes**:
1. Kill switch is active
2. Configuration file missing/invalid
3. Port already in use
4. Missing dependencies
5. API credentials invalid

**Solutions**:
```bash
# Check kill switch status
curl http://localhost:8000/status

# Validate config files
python -c "import json; json.load(open('config/bot-limits.json'))"

# Check port availability
lsof -i :9000

# Install dependencies
pip install -r requirements.txt

# Check logs
tail -f logs/bot-coordinator.log
```

#### Bot Stops Unexpectedly

**Check**:
1. Error logs
2. Health check failures
3. API rate limits
4. Memory/CPU usage
5. Network connectivity

**Investigation**:
```bash
# Recent errors
grep "ERROR" logs/*.log | tail -20

# System resources
top -p $(pgrep -f bot-coordinator)

# Network
ping -c 5 api.ndax.io
```

#### Bot Shows "ERROR" Status

**Immediate Actions**:
1. Check error logs
2. Attempt recovery
3. If recovery fails, manual intervention

```bash
# View errors
tail -100 logs/bot-coordinator.log | grep ERROR

# Trigger recovery
curl -X POST http://localhost:8000/recovery \
  -d '{"bot": "ndax"}'

# Manual restart
python backend/bot-coordinator.py --restart ndax
```

### Kill Switch Issues

#### Kill Switch Won't Activate

**Check**:
1. Coordinator is running
2. API endpoint accessible
3. Configuration valid

```bash
# Test coordinator
curl http://localhost:8000/health

# Check config
cat config/kill-switch.json | jq .

# Force activation
python backend/bot-coordinator.py --kill-switch force
```

#### Kill Switch Won't Deactivate

**Check**:
1. Circuit breaker status
2. Cooldown period
3. System health

```bash
# Check circuit breaker
curl http://localhost:8000/status | jq .circuit_breaker

# Wait for cooldown
# Check config: recovery-settings.json

# Force override (use carefully)
curl -X POST http://localhost:8000/kill-switch \
  -d '{"action": "force_override", "reason": "Admin override"}'
```

#### False Positive Kill Switch Triggers

**Adjust sensitivity** in `config/kill-switch.json`:
```json
{
  "conditions": {
    "api_errors": {
      "threshold": 15,  // Increase from 10
      "window_minutes": 20  // Increase from 15
    }
  }
}
```

### Coordinator Issues

#### Coordinator Won't Start

**Check**:
1. Python version (3.11+)
2. Dependencies installed
3. Config files present
4. Port not in use

```bash
# Python version
python --version

# Install deps
pip install aiohttp

# Check configs
ls -la config/*.json

# Check port
lsof -i :8000
```

#### Coordinator Crashes

**Check logs**:
```bash
tail -100 logs/bot-coordinator.log
```

**Common causes**:
- Memory exhaustion
- Unhandled exception
- Network timeout
- Config file corruption

**Solutions**:
- Increase memory allocation
- Update error handling
- Add timeout configuration
- Validate/restore configs

#### Health Checks Failing

**Symptoms**: Bots show 0% health despite running

**Check**:
1. Bot endpoints responding
2. Network connectivity
3. Timeout settings

```bash
# Test endpoints
curl http://localhost:9000/health
curl http://localhost:9001/health
curl http://localhost:9002/health

# Adjust timeout
# Edit config/api-endpoints.json
{
  "health_check_config": {
    "timeout_seconds": 10  // Increase from 5
  }
}
```

### Dashboard Issues

#### Dashboard Won't Load

**Check**:
1. Health monitor running
2. Port accessible
3. Dashboard file exists

```bash
# Check monitor
ps aux | grep health-monitor

# Start monitor
python monitoring/health-monitor.py

# Verify file
ls -la monitoring/status-dashboard.html

# Access dashboard
curl http://localhost:8080/
```

#### Dashboard Shows Stale Data

**Causes**:
- Browser cache
- WebSocket disconnected
- Monitor not updating

**Solutions**:
```bash
# Clear cache
# Press Ctrl+Shift+R in browser

# Restart monitor
pkill -f health-monitor
python monitoring/health-monitor.py

# Check for errors
tail -f logs/health-monitor.log
```

### API Issues

#### API Authentication Fails

**Check**:
1. API keys in .env
2. Keys not expired
3. IP whitelist (if applicable)

```bash
# Verify env file
grep API_KEY .env

# Test API directly
curl -H "X-API-Key: your_key" https://api.ndax.io/health

# Rotate keys if needed
# 1. Generate new keys at exchange
# 2. Update .env
# 3. Restart bots
```

#### Rate Limit Exceeded

**Symptoms**: Many 429 errors in logs

**Solutions**:
```bash
# Reduce trading frequency
# Edit config/bot-limits.json
{
  "ndax_bot": {
    "max_daily_trades": 25,  // Reduce from 50
    "min_time_between_trades": 120  // Increase from 60
  }
}

# Add retry backoff
# Configure in bot code

# Use multiple API keys (if supported)
```

#### Connection Timeouts

**Check**:
1. Internet connection
2. API service status
3. Firewall rules

```bash
# Test connectivity
ping api.ndax.io

# Check DNS
nslookup api.ndax.io

# Test HTTPS
curl -v https://api.ndax.io

# Increase timeout
# Edit config/api-endpoints.json
{
  "health_check_config": {
    "timeout_seconds": 15
  }
}
```

### Configuration Issues

#### Invalid JSON Configuration

**Error**: "JSONDecodeError: Expecting value"

**Solutions**:
```bash
# Validate JSON
python -m json.tool config/bot-limits.json

# Find syntax error
cat config/bot-limits.json | jq .

# Restore from backup
cp config-backup/*.json config/
```

#### Missing Configuration Files

**Error**: "FileNotFoundError: config/bot-limits.json"

**Solution**:
```bash
# Check which files exist
ls -la config/

# Copy from examples
cp config/*.example.json config/

# Or restore from git
git checkout config/*.json
```

### Workflow Issues

#### GitHub Actions Workflow Fails

**Check workflow runs**:
1. Go to Actions tab
2. Click failed workflow
3. Review logs

**Common causes**:
- Missing secrets
- Permission issues
- Syntax errors
- API rate limits

**Solutions**:
```bash
# Validate workflow YAML
# Use GitHub's workflow validator

# Check secrets
# Settings → Secrets → Actions

# Test locally
act -l  # Using nektos/act
```

#### Health Check Workflow Not Running

**Check**:
1. Workflow is enabled
2. Schedule is correct
3. Branch protections

**Enable workflow**:
1. Go to Actions
2. Find "Bot Health Check"
3. Click "Enable workflow"

### Recovery Issues

#### Auto-Recovery Fails

**Check logs**:
```bash
tail -100 logs/recovery.log
```

**Common causes**:
- Service not responding
- Config issues
- Resource constraints

**Manual recovery**:
```bash
# Stop all bots
curl -X POST http://localhost:8000/stop-all

# Check system health
python backend/bot-coordinator.py --health-check

# Restart in safe mode
python backend/bot-coordinator.py --safe-mode

# Start individual bot
curl -X POST http://localhost:8000/start \
  -d '{"bot": "ndax", "safe_mode": true}'
```

#### Repeated Recovery Attempts

**Symptoms**: Recovery keeps failing and retrying

**Actions**:
1. Disable auto-recovery
2. Investigate root cause
3. Fix issue manually
4. Re-enable auto-recovery

```bash
# Disable auto-recovery
# Edit config/recovery-settings.json
{
  "auto_recovery": {
    "enabled": false
  }
}

# Restart coordinator
pkill -f bot-coordinator
python backend/bot-coordinator.py
```

### Performance Issues

#### High Memory Usage

**Check**:
```bash
# Monitor memory
top -p $(pgrep -f bot-coordinator)

# Check for leaks
python -m memory_profiler backend/bot-coordinator.py
```

**Solutions**:
- Restart bots periodically
- Clear old logs
- Optimize data structures
- Increase system RAM

#### Slow Response Times

**Check**:
```bash
# Measure API latency
curl -w "@curl-format.txt" http://localhost:8000/health

# Check system load
uptime
iostat
```

**Solutions**:
- Optimize database queries
- Add caching
- Reduce polling frequency
- Scale horizontally

#### Database Lock Issues

**If using SQLite**:
- Switch to PostgreSQL
- Reduce concurrent writes
- Add write-ahead logging

### Logging Issues

#### Logs Not Being Created

**Check**:
```bash
# Directory exists
ls -la logs/

# Permissions
ls -ld logs/
chmod 755 logs/

# Disk space
df -h
```

#### Logs Too Large

**Rotate logs**:
```bash
# Manual rotation
gzip logs/*.log

# Automated rotation (logrotate)
cat > /etc/logrotate.d/bot-coordinator << EOF
/path/to/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### Testing Issues

#### Paper Mode Not Working

**Check**:
```bash
# Verify env variable
echo $TRADING_MODE

# Set explicitly
export TRADING_MODE=paper

# Restart bots
python backend/bot-coordinator.py
```

#### Can't Switch to Live Mode

**Requirements**:
1. Completed paper mode testing
2. Valid API credentials
3. Explicit confirmation

```bash
# Set live mode
export TRADING_MODE=live

# Confirm
echo "WARNING: Switching to LIVE trading"
read -p "Are you sure? (yes/no): " confirm

# Restart with confirmation
if [ "$confirm" = "yes" ]; then
    python backend/bot-coordinator.py --live
fi
```

## Diagnostic Tools

### Health Check Script

```bash
#!/bin/bash
# health-check.sh

echo "=== System Health Check ==="

echo "1. Coordinator Status:"
curl -s http://localhost:8000/health || echo "FAILED"

echo -e "\n2. Monitor Status:"
curl -s http://localhost:8080/health || echo "FAILED"

echo -e "\n3. Bot Status:"
curl -s http://localhost:8000/status | jq .bots

echo -e "\n4. Recent Errors:"
grep ERROR logs/*.log | tail -5

echo -e "\n5. Kill Switch:"
curl -s http://localhost:8000/status | jq .kill_switch_active

echo -e "\n6. System Resources:"
free -h
df -h | grep -E "/$|logs"
```

### Log Analyzer

```python
#!/usr/bin/env python3
# analyze-logs.py

import sys
from pathlib import Path
from collections import Counter

def analyze_logs(log_dir="logs"):
    errors = Counter()
    warnings = Counter()
    
    for log_file in Path(log_dir).glob("*.log"):
        with open(log_file) as f:
            for line in f:
                if "ERROR" in line:
                    # Extract error type
                    parts = line.split("ERROR:")
                    if len(parts) > 1:
                        error_msg = parts[1].strip()[:50]
                        errors[error_msg] += 1
                elif "WARNING" in line:
                    parts = line.split("WARNING:")
                    if len(parts) > 1:
                        warn_msg = parts[1].strip()[:50]
                        warnings[warn_msg] += 1
    
    print("=== Log Analysis ===")
    print(f"\nTop Errors:")
    for msg, count in errors.most_common(5):
        print(f"  [{count}] {msg}")
    
    print(f"\nTop Warnings:")
    for msg, count in warnings.most_common(5):
        print(f"  [{count}] {msg}")

if __name__ == "__main__":
    analyze_logs()
```

## Getting Help

### Documentation
- [SETUP.md](SETUP.md) - Setup instructions
- [BOT-OPERATIONS.md](BOT-OPERATIONS.md) - Operations guide
- [SAFETY-PROTOCOLS.md](SAFETY-PROTOCOLS.md) - Safety procedures
- [API-REFERENCE.md](API-REFERENCE.md) - API documentation

### Support Channels
1. Check GitHub Issues
2. Review workflow logs
3. Check system logs
4. Contact administrators

### Reporting Issues

When reporting, include:
1. Error message
2. Relevant logs (last 50 lines)
3. Configuration (sanitized)
4. Steps to reproduce
5. Expected vs actual behavior
6. System information

### Debug Mode

Enable verbose logging:
```bash
export LOG_LEVEL=DEBUG
python backend/bot-coordinator.py
```
