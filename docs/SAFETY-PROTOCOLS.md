# Safety Protocols and Kill Switch Guide

## Overview

This document outlines the safety protocols, kill switch mechanisms, and oversight procedures for the bot coordination system.

⚠️ **IMPORTANT**: Trading with automated systems involves real financial risk. These safety mechanisms are designed to minimize risk but cannot eliminate it entirely.

## Kill Switch System

### What is the Kill Switch?

The kill switch is an emergency shutdown mechanism that immediately halts all trading operations across all bots when triggered.

### When to Use Kill Switch

**Immediate Activation Required**:
- Unexpected market volatility
- System malfunction detected
- API access compromised
- Runaway trading detected
- Daily loss limit approaching
- Exchange maintenance announced
- Security breach suspected

**Consider Activation**:
- Multiple consecutive losses
- Unusual trading patterns
- High error rates
- Performance degradation
- Testing new configurations

### Kill Switch Configuration

Located in `/config/kill-switch.json`:

```json
{
  "enabled": true,
  "auto_trigger": true,
  "manual_override_allowed": true,
  "conditions": {
    "max_daily_loss_reached": {
      "enabled": true,
      "threshold": 400,
      "action": "stop_all_bots"
    },
    "consecutive_failures": {
      "enabled": true,
      "threshold": 5,
      "window_minutes": 30,
      "action": "pause_affected_bot"
    }
  }
}
```

### Kill Switch Conditions

#### 1. Max Daily Loss Reached
```json
{
  "enabled": true,
  "threshold": 400,  // $400 total loss
  "action": "stop_all_bots"
}
```
**Trigger**: Total losses across all bots exceed $400
**Action**: Stop all bots immediately

#### 2. Consecutive Failures
```json
{
  "enabled": true,
  "threshold": 5,
  "window_minutes": 30,
  "action": "pause_affected_bot"
}
```
**Trigger**: 5 consecutive failed trades in 30 minutes
**Action**: Pause the affected bot

#### 3. Account Equity Drop
```json
{
  "enabled": true,
  "threshold_percentage": 30,
  "action": "stop_all_bots"
}
```
**Trigger**: Account equity drops by 30%
**Action**: Stop all bots immediately

#### 4. API Errors
```json
{
  "enabled": true,
  "threshold": 10,
  "window_minutes": 15,
  "action": "pause_affected_bot"
}
```
**Trigger**: 10 API errors in 15 minutes
**Action**: Pause the affected bot

#### 5. Network Issues
```json
{
  "enabled": true,
  "threshold": 5,
  "window_minutes": 10,
  "action": "pause_affected_bot"
}
```
**Trigger**: 5 network failures in 10 minutes
**Action**: Pause the affected bot

#### 6. Circuit Breaker
```json
{
  "enabled": true,
  "threshold": 3,
  "cooldown_minutes": 60,
  "action": "circuit_break"
}
```
**Trigger**: 3 kill switch activations in short period
**Action**: Enter circuit breaker mode (requires manual reset)

## Activating Kill Switch

### Method 1: Dashboard (Recommended)

1. Navigate to http://localhost:8080
2. Locate "Emergency Kill Switch" section
3. Click "ACTIVATE KILL SWITCH" button
4. Confirm activation

### Method 2: API Call

```bash
curl -X POST http://localhost:8000/kill-switch \
  -H "Content-Type: application/json" \
  -d '{
    "action": "activate",
    "reason": "Manual emergency stop"
  }'
```

### Method 3: Command Line

```bash
python backend/bot-coordinator.py --kill-switch activate
```

### Method 4: GitHub Actions

1. Go to Actions → Bot Recovery
2. Run workflow with kill switch option
3. Confirm activation

## What Happens When Kill Switch Activates

### Immediate Actions (< 1 second)

1. ✅ Stop accepting new trade signals
2. ✅ Cancel all pending orders (if possible)
3. ✅ Close open market orders
4. ✅ Pause all bot processes
5. ✅ Log activation with timestamp and reason

### Secondary Actions (1-5 seconds)

6. ✅ Send notifications to all configured channels
7. ✅ Create incident report
8. ✅ Snapshot current positions
9. ✅ Freeze trading limits
10. ✅ Update dashboard status

### What Does NOT Happen

❌ Existing positions are NOT automatically closed
❌ Limit orders are NOT cancelled (by design)
❌ Account access is NOT revoked
❌ Historical data is NOT affected

## Deactivating Kill Switch

### Prerequisites for Deactivation

Before deactivating, verify:

✅ Root cause identified and resolved
✅ System health checks passed
✅ No active threats or anomalies
✅ Manual review completed
✅ Cooldown period elapsed (if required)

### Manual Override Procedure

#### Step 1: Review Incident
```bash
# Check logs for trigger cause
tail -100 logs/bot-coordinator.log | grep "KILL SWITCH"

# Review trading activity
curl http://localhost:8080/metrics
```

#### Step 2: Verify System Health
```bash
# Check all bots
python backend/bot-coordinator.py --health-check

# Verify API connectivity
curl http://localhost:8000/health
```

#### Step 3: Disable Kill Switch

Via Dashboard:
1. Navigate to http://localhost:8080
2. Click "MANUAL OVERRIDE" button
3. Enter override reason
4. Confirm deactivation

Via API:
```bash
curl -X POST http://localhost:8000/kill-switch \
  -H "Content-Type: application/json" \
  -d '{
    "action": "override",
    "reason": "System reviewed and safe to resume",
    "approved_by": "admin"
  }'
```

#### Step 4: Safe Mode Restart

After override, bots restart in safe mode:
- 50% reduced position sizes
- 50% reduced trade frequency
- Duration: 2 hours by default
- Extra monitoring enabled

### Auto-Recovery Settings

Configure in `/config/recovery-settings.json`:

```json
{
  "recovery": {
    "auto_recovery_enabled": false,
    "manual_approval_required": true,
    "cooldown_period_minutes": 60,
    "reduced_limits_on_recovery": true
  }
}
```

**Recommendation**: Keep `manual_approval_required: true` for safety

## Trading Limits

### Per-Bot Limits

Located in `/config/bot-limits.json`:

#### Position Limits
```json
{
  "ndax_bot": {
    "max_position_size": 1000,       // Max $1000 per position
    "max_concurrent_positions": 5,    // Max 5 positions at once
    "max_leverage": 1                 // No leverage (1x)
  }
}
```

#### Loss Limits
```json
{
  "ndax_bot": {
    "max_daily_loss": 100,           // Max $100 loss per day
    "stop_loss_percentage": 5,       // 5% stop loss per trade
    "emergency_stop_loss": 1000      // Hard stop at $1000 loss
  }
}
```

#### Trading Frequency
```json
{
  "ndax_bot": {
    "max_daily_trades": 50,          // Max 50 trades per day
    "min_time_between_trades": 60,   // 60 seconds minimum
    "max_trades_per_hour": 10        // Max 10 trades per hour
  }
}
```

### Global Limits

System-wide limits across all bots:

```json
{
  "global_limits": {
    "total_max_daily_loss": 400,        // $400 max total loss
    "total_max_exposure": 15000,        // $15,000 max total exposure
    "emergency_stop_loss": 1000,        // Emergency stop at $1000
    "consecutive_loss_limit": 5,        // Stop after 5 consecutive losses
    "account_equity_threshold": 0.3     // Stop at 30% equity drop
  }
}
```

## Monitoring and Alerts

### Alert Levels

#### Level 1: INFO
- Bot started/stopped normally
- Configuration updated
- Health check passed

**Action**: Log only, no notification

#### Level 2: WARNING
- Minor API errors
- Temporary connectivity issues
- Approaching daily limits

**Action**: Dashboard notification

#### Level 3: HIGH
- Bot stopped unexpectedly
- Multiple API errors
- 50% of limit reached
- Single failed health check

**Action**: Dashboard + log file + email (if configured)

#### Level 4: CRITICAL
- Kill switch triggered
- Loss limit reached
- Account equity drop
- Security issue detected

**Action**: All channels (dashboard, email, Slack, Discord)

### Notification Channels

Configure in `/config/notification-config.json`:

```json
{
  "channels": {
    "email": {
      "enabled": false,
      "recipients": ["alerts@example.com"],
      "priority_levels": ["critical", "high"]
    },
    "slack": {
      "enabled": false,
      "webhook_url": "https://hooks.slack.com/...",
      "priority_levels": ["critical", "high", "medium"]
    },
    "dashboard": {
      "enabled": true,
      "priority_levels": ["critical", "high", "medium", "low"]
    }
  }
}
```

## Safety Checklists

### Daily Operations Checklist

**Before Starting Bots**:
- [ ] Verify market conditions are normal
- [ ] Check for scheduled exchange maintenance
- [ ] Review overnight logs for issues
- [ ] Confirm all safety limits are set correctly
- [ ] Ensure kill switch is enabled
- [ ] Verify API credentials are valid
- [ ] Check account balances

**During Operation**:
- [ ] Monitor dashboard every 2-4 hours
- [ ] Review error logs if alerts received
- [ ] Check trading performance vs. limits
- [ ] Verify positions are within limits
- [ ] Respond to any alerts promptly

**End of Day**:
- [ ] Review total P&L vs. limits
- [ ] Check for any unusual patterns
- [ ] Review all triggered alerts
- [ ] Close any manual positions if needed
- [ ] Update incident log if issues occurred

### Weekly Review Checklist

- [ ] Review all kill switch activations
- [ ] Analyze bot performance metrics
- [ ] Check for pattern in errors/failures
- [ ] Review and adjust limits if needed
- [ ] Test kill switch activation (paper mode)
- [ ] Verify backup systems are functional
- [ ] Update documentation if needed

### Monthly Audit Checklist

- [ ] Comprehensive performance review
- [ ] Security audit of API keys
- [ ] Review and update safety limits
- [ ] Test disaster recovery procedures
- [ ] Update system dependencies
- [ ] Review and archive old logs
- [ ] Compliance check if applicable

## Emergency Procedures

### Scenario 1: Runaway Trading

**Symptoms**: Rapid unexpected trades, positions exceeding limits

**Immediate Actions**:
1. Activate kill switch (dashboard or API)
2. Log into exchange directly
3. Cancel all open orders manually
4. Close positions if necessary
5. Document what happened

**Investigation**:
1. Review bot logs for root cause
2. Check configuration for errors
3. Verify API rate limits not exceeded
4. Analyze trade logic for bugs

### Scenario 2: API Access Compromised

**Symptoms**: Unauthorized trades, unknown API requests

**Immediate Actions**:
1. Activate kill switch
2. Revoke API keys at exchange
3. Generate new API keys
4. Review all recent transactions
5. Contact exchange support

**Recovery**:
1. Investigate security breach
2. Update security practices
3. Re-secure API credentials
4. Test with paper mode
5. Resume with caution

### Scenario 3: Exchange Maintenance

**Symptoms**: Exchange announces maintenance window

**Preparation**:
1. Note maintenance window
2. Close positions before maintenance
3. Activate kill switch before window
4. Cancel all pending orders
5. Document positions snapshot

**After Maintenance**:
1. Verify exchange is operational
2. Test API connectivity
3. Start with single bot in paper mode
4. Gradually enable all bots
5. Monitor closely first hour

### Scenario 4: Major Market Event

**Symptoms**: Extreme volatility, circuit breakers, market halt

**Immediate Actions**:
1. Activate kill switch
2. Do NOT attempt to trade
3. Wait for market to stabilize
4. Review positions
5. Assess risk exposure

**Recovery**:
1. Wait for clear market direction
2. Reduce trading limits by 50%
3. Resume with single bot first
4. Monitor for several hours
5. Gradually return to normal operations

## Override Authorizations

### Who Can Override Kill Switch

Define authorized personnel:
- Primary Administrator
- Secondary Administrator
- On-call Engineer (with approval)

### Override Documentation

Every override must be documented:
- Timestamp
- Person authorizing override
- Reason for override
- Current system state
- Risk assessment
- Approval chain

### Override Log

Maintain override log:
```
Date: 2024-02-14 10:30:00
Authorized By: admin@example.com
Reason: False positive - API timeout was temporary
System State: All bots healthy, no open positions
Risk Level: Low
Approved: Yes
Notes: Waited 30 minutes after API recovery before override
```

## Testing Safety Mechanisms

### Monthly Kill Switch Test

1. Set system to paper mode
2. Activate kill switch via dashboard
3. Verify all bots stop
4. Check notifications sent
5. Test override procedure
6. Verify bots can restart
7. Document test results

### Limit Testing

1. Set very low limits (paper mode)
2. Trigger each limit condition
3. Verify proper response
4. Test recovery procedures
5. Document findings

## Related Documentation

- [BOT-OPERATIONS.md](BOT-OPERATIONS.md) - Bot coordination
- [RECOVERY-PROCEDURES.md](RECOVERY-PROCEDURES.md) - Recovery procedures
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

## Emergency Contacts

Maintain emergency contact list:
- Primary Admin: [Contact Info]
- Secondary Admin: [Contact Info]
- Exchange Support: [Contact Info]
- Security Team: [Contact Info]
