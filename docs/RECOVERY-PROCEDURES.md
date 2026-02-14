# Recovery Procedures

## Overview

This document provides step-by-step manual intervention procedures for various failure scenarios.

## When to Use Manual Recovery

Use manual recovery when:
- Automated recovery has failed multiple times
- System is in circuit breaker state
- Critical security issue detected
- Configuration needs manual review
- Complex failure requiring human judgment

## General Recovery Process

### Step 1: Assess the Situation

```bash
# Check system status
curl http://localhost:8000/status

# Review recent logs
tail -100 logs/bot-coordinator.log

# Check for active alerts
curl http://localhost:8080/alerts

# Review error patterns
python docs/analyze-logs.py
```

### Step 2: Stop All Operations

```bash
# Activate kill switch
curl -X POST http://localhost:8000/kill-switch \
  -H "Content-Type: application/json" \
  -d '{"action": "activate", "reason": "Manual recovery"}'

# Verify all bots stopped
curl http://localhost:8000/status | jq .bots
```

### Step 3: Investigate Root Cause

```bash
# Check logs for errors
grep -r "ERROR\|CRITICAL" logs/

# Review recent changes
git log --oneline -10

# Check system resources
top
df -h
free -h

# Test API connectivity
curl https://api.ndax.io/health
```

### Step 4: Fix the Issue

Follow scenario-specific procedures below.

### Step 5: Verify System Health

```bash
# Run health checks
python backend/bot-coordinator.py --health-check

# Test configurations
python -c "import json; json.load(open('config/bot-limits.json'))"

# Verify API access
# Test with paper mode first
```

### Step 6: Gradual Recovery

```bash
# Disable kill switch
curl -X POST http://localhost:8000/kill-switch \
  -d '{"action": "override", "reason": "Recovery complete"}'

# Start first bot in safe mode
curl -X POST http://localhost:8000/start \
  -d '{"bot": "ndax", "safe_mode": true}'

# Monitor for 30 minutes
watch -n 10 'curl -s http://localhost:8000/status'

# Start remaining bots if stable
curl -X POST http://localhost:8000/start-sequential
```

### Step 7: Document Recovery

Create recovery log:
```
Date: 2024-02-14 10:00
Issue: [Description]
Root Cause: [Cause]
Actions Taken: [Steps]
Outcome: [Success/Failure]
Lessons Learned: [Notes]
```

## Scenario-Specific Procedures

### Scenario 1: Bot Crashes Repeatedly

**Symptoms**: Bot starts but crashes within minutes

**Investigation**:
```bash
# Check crash logs
tail -200 logs/bot-coordinator.log | grep -A 10 "CRITICAL"

# Check for memory issues
grep -i "memory" logs/*.log

# Check for exceptions
grep -i "exception\|traceback" logs/*.log
```

**Recovery Steps**:

1. **Identify crash cause** from logs
   - Out of memory → Increase resources
   - Unhandled exception → Fix code
   - API errors → Check credentials

2. **Fix the issue**:
   ```bash
   # If memory issue
   # Increase available memory or reduce batch sizes
   
   # If API issue
   # Verify and update credentials in .env
   
   # If code issue
   # Apply bug fix or revert to stable version
   git checkout <stable_commit>
   ```

3. **Test in isolation**:
   ```bash
   # Start only the problematic bot
   python backend/bot-coordinator.py --bot ndax --test
   
   # Monitor for 1 hour
   # If stable, proceed to full restart
   ```

4. **Full restart**:
   ```bash
   # Start coordinator
   python backend/bot-coordinator.py
   
   # Start sequential
   curl -X POST http://localhost:8000/start-sequential
   ```

### Scenario 2: API Connection Failures

**Symptoms**: Multiple API timeout or connection refused errors

**Investigation**:
```bash
# Test network
ping api.ndax.io
traceroute api.ndax.io

# Test API directly
curl -v https://api.ndax.io/health

# Check firewall
sudo iptables -L
sudo ufw status

# Check DNS
nslookup api.ndax.io
```

**Recovery Steps**:

1. **Verify network connectivity**:
   ```bash
   # Test internet
   ping -c 5 8.8.8.8
   
   # Test DNS
   nslookup api.ndax.io
   
   # Test specific endpoint
   curl -I https://api.ndax.io
   ```

2. **Check API credentials**:
   ```bash
   # Verify API key in .env
   grep API_KEY .env
   
   # Test with valid key
   curl -H "X-API-Key: $NDAX_API_KEY" https://api.ndax.io/v1/account
   ```

3. **Adjust timeouts**:
   ```json
   // config/api-endpoints.json
   {
     "health_check_config": {
       "timeout_seconds": 15,  // Increase from 5
       "failure_threshold": 5   // Increase from 3
     }
   }
   ```

4. **Implement retry logic**:
   ```python
   # In bot code, add exponential backoff
   import time
   from functools import wraps
   
   def retry_with_backoff(retries=3, backoff=2):
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               for i in range(retries):
                   try:
                       return func(*args, **kwargs)
                   except Exception as e:
                       if i == retries - 1:
                           raise
                       time.sleep(backoff ** i)
           return wrapper
       return decorator
   ```

5. **Switch to backup API** (if available):
   ```json
   // config/api-endpoints.json
   {
     "external_apis": {
       "market_data": {
         "primary": "https://api.primary.com",
         "backup": "https://api.backup.com"
       }
     }
   }
   ```

### Scenario 3: Configuration Corruption

**Symptoms**: Bot won't start, JSON parse errors

**Investigation**:
```bash
# Validate all configs
for file in config/*.json; do
    echo "Checking $file"
    python -m json.tool "$file" > /dev/null || echo "INVALID: $file"
done

# Find syntax errors
jq . config/bot-limits.json
```

**Recovery Steps**:

1. **Backup corrupted files**:
   ```bash
   mkdir -p config/corrupted
   cp config/*.json config/corrupted/
   ```

2. **Restore from backup**:
   ```bash
   # From git
   git checkout config/bot-limits.json
   
   # Or from backup
   cp backups/config-latest/*.json config/
   ```

3. **Validate restored files**:
   ```bash
   # Check each file
   python -c "import json; json.load(open('config/bot-limits.json'))"
   python -c "import json; json.load(open('config/kill-switch.json'))"
   python -c "import json; json.load(open('config/recovery-settings.json'))"
   ```

4. **Restart system**:
   ```bash
   python backend/bot-coordinator.py
   ```

### Scenario 4: Kill Switch Won't Deactivate

**Symptoms**: Override command doesn't work, circuit breaker active

**Investigation**:
```bash
# Check circuit breaker status
curl http://localhost:8000/status | jq .circuit_breaker

# Check cooldown status
cat config/recovery-settings.json | jq .recovery.cooldown_period_minutes

# Check activation count
grep "kill switch" logs/bot-coordinator.log | wc -l
```

**Recovery Steps**:

1. **Check circuit breaker state**:
   ```bash
   # View state
   curl http://localhost:8000/status | jq .circuit_breaker
   
   # If active, need to reset
   ```

2. **Reset circuit breaker** (if needed):
   ```bash
   # Stop coordinator
   pkill -f bot-coordinator
   
   # Clear circuit breaker state
   rm -f /tmp/circuit-breaker-state.json
   
   # Restart coordinator
   python backend/bot-coordinator.py
   ```

3. **Force override** (use with caution):
   ```bash
   # Direct override
   curl -X POST http://localhost:8000/kill-switch \
     -H "Content-Type: application/json" \
     -d '{
       "action": "force_override",
       "reason": "Circuit breaker reset",
       "approved_by": "admin"
     }'
   ```

4. **Verify deactivation**:
   ```bash
   curl http://localhost:8000/status | jq .kill_switch_active
   # Should return: false
   ```

### Scenario 5: Data Loss/Corruption

**Symptoms**: Missing data, incorrect positions, balance mismatch

**Investigation**:
```bash
# Check database integrity
# (If using database)

# Check file integrity
ls -la logs/
ls -la config/

# Check git status
git status
git log --oneline -5
```

**Recovery Steps**:

1. **Stop all operations immediately**:
   ```bash
   curl -X POST http://localhost:8000/kill-switch \
     -d '{"action": "activate", "reason": "Data integrity issue"}'
   ```

2. **Assess data loss**:
   ```bash
   # Check what's missing
   # Compare with backups
   # Review transaction logs
   ```

3. **Restore from backup**:
   ```bash
   # List available backups
   ls -lt backups/
   
   # Restore latest backup
   tar -xzf backups/backup-latest.tar.gz -C /tmp/restore
   
   # Compare with current
   diff -r /tmp/restore/config config/
   ```

4. **Reconcile with exchange**:
   ```bash
   # Query exchange for actual positions
   curl -H "X-API-Key: $API_KEY" https://api.ndax.io/v1/positions
   
   # Update local state to match
   # Manual reconciliation may be needed
   ```

5. **Verify and restart**:
   ```bash
   # Verify data integrity
   python backend/bot-coordinator.py --verify-data
   
   # Start in read-only mode first
   python backend/bot-coordinator.py --read-only
   
   # If safe, resume normal operations
   ```

### Scenario 6: Security Breach

**Symptoms**: Unauthorized trades, unknown API calls, suspicious activity

**IMMEDIATE ACTIONS**:

1. **Activate kill switch**:
   ```bash
   curl -X POST http://localhost:8000/kill-switch \
     -d '{"action": "activate", "reason": "SECURITY BREACH"}'
   ```

2. **Revoke all API keys**:
   - Log into exchange immediately
   - Revoke all API keys
   - Change account password
   - Enable 2FA if not already active

3. **Isolate system**:
   ```bash
   # Stop all services
   pkill -f bot-coordinator
   pkill -f health-monitor
   
   # Disconnect from network (if needed)
   sudo ifconfig eth0 down
   ```

4. **Preserve evidence**:
   ```bash
   # Backup all logs
   tar -czf security-incident-$(date +%Y%m%d-%H%M%S).tar.gz logs/
   
   # Snapshot current state
   curl http://localhost:8000/status > incident-status.json
   
   # Git state
   git log > incident-git-log.txt
   ```

5. **Investigation**:
   ```bash
   # Review all logs
   grep -r "authentication\|unauthorized\|suspicious" logs/
   
   # Check for unauthorized changes
   git diff HEAD
   
   # Review API call logs
   grep "API" logs/*.log
   ```

6. **Recovery** (after investigation):
   - Generate new API keys
   - Update all credentials
   - Review and update security measures
   - Scan for malware
   - Change all passwords
   - Review access logs
   - Test with paper mode extensively
   - Resume with extreme caution

### Scenario 7: System Resource Exhaustion

**Symptoms**: High memory, high CPU, disk full, OOM errors

**Investigation**:
```bash
# Memory
free -h
ps aux --sort=-%mem | head

# CPU
top -bn1 | head -20
ps aux --sort=-%cpu | head

# Disk
df -h
du -sh /* | sort -hr | head

# Open files
lsof | wc -l
ulimit -n
```

**Recovery Steps**:

1. **Free up resources**:
   ```bash
   # Clear old logs
   find logs/ -name "*.log" -mtime +7 -delete
   
   # Clear temp files
   rm -rf /tmp/*bot*
   
   # Clear cache
   rm -rf ~/.cache/*
   ```

2. **Kill resource-hungry processes**:
   ```bash
   # Find culprits
   ps aux --sort=-%mem | head -5
   
   # Kill if necessary
   kill -9 <PID>
   ```

3. **Adjust limits**:
   ```bash
   # Increase open file limit
   ulimit -n 4096
   
   # Add to /etc/security/limits.conf
   * soft nofile 4096
   * hard nofile 8192
   ```

4. **Optimize configuration**:
   ```json
   // Reduce batch sizes, polling frequency, etc.
   {
     "health_check_interval": 120,  // Increase from 60
     "max_concurrent_positions": 3   // Reduce from 5
   }
   ```

5. **Restart services**:
   ```bash
   python backend/bot-coordinator.py
   ```

## Post-Recovery Checklist

After any recovery:

- [ ] Document what happened
- [ ] Update runbook if needed
- [ ] Review and adjust limits
- [ ] Test kill switch
- [ ] Monitor for 24-48 hours
- [ ] Schedule follow-up review
- [ ] Update security measures
- [ ] Backup current configuration
- [ ] Review logs for patterns
- [ ] Train team on lessons learned

## Emergency Contacts

**Primary Administrator**: [Contact]
**Secondary Administrator**: [Contact]
**Exchange Support**: [Contact]
**Security Team**: [Contact]
**On-Call Schedule**: [Link]

## Related Documentation

- [SETUP.md](SETUP.md) - Setup instructions
- [BOT-OPERATIONS.md](BOT-OPERATIONS.md) - Normal operations
- [SAFETY-PROTOCOLS.md](SAFETY-PROTOCOLS.md) - Safety procedures
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [API-REFERENCE.md](API-REFERENCE.md) - API documentation
