# API Reference

## Overview

This document provides a complete reference for the Bot Coordinator API.

**Base URL**: `http://localhost:8000`
**Version**: 1.0
**Format**: JSON

## Authentication

Currently, the API does not require authentication when accessed from localhost. In production, implement proper authentication.

## Endpoints

### Bot Coordinator API

#### Get System Status

```http
GET /status
```

**Response**:
```json
{
  "kill_switch_active": false,
  "bots": {
    "ndax": {
      "status": "running",
      "health": 100,
      "error_count": 0,
      "latest_errors": []
    },
    "quantum": {
      "status": "stopped",
      "health": 0,
      "error_count": 0,
      "latest_errors": []
    },
    "shadowforge": {
      "status": "stopped",
      "health": 0,
      "error_count": 0,
      "latest_errors": []
    }
  },
  "metrics": {
    "total_trades": 0,
    "total_profit_loss": 0.0,
    "bots_started": 3,
    "errors_handled": 0,
    "kill_switches_triggered": 0,
    "recoveries_attempted": 0,
    "recoveries_succeeded": 0
  },
  "timestamp": "2024-02-14T10:00:00Z"
}
```

#### Start Bot

```http
POST /start
Content-Type: application/json

{
  "bot": "ndax",
  "safe_mode": false
}
```

**Parameters**:
- `bot` (string, required): Bot name (`ndax`, `quantum`, or `shadowforge`)
- `safe_mode` (boolean, optional): Start in safe mode with reduced limits

**Response**:
```json
{
  "success": true,
  "bot": "ndax",
  "status": "starting",
  "message": "Bot start initiated"
}
```

#### Stop Bot

```http
POST /stop
Content-Type: application/json

{
  "bot": "ndax",
  "reason": "Manual stop"
}
```

**Parameters**:
- `bot` (string, required): Bot name or "all"
- `reason` (string, optional): Reason for stopping

**Response**:
```json
{
  "success": true,
  "bot": "ndax",
  "status": "stopped",
  "message": "Bot stopped successfully"
}
```

#### Pause Bot

```http
POST /pause
Content-Type: application/json

{
  "bot": "ndax"
}
```

**Response**:
```json
{
  "success": true,
  "bot": "ndax",
  "status": "paused",
  "message": "Bot paused"
}
```

#### Resume Bot

```http
POST /resume
Content-Type: application/json

{
  "bot": "ndax"
}
```

**Response**:
```json
{
  "success": true,
  "bot": "ndax",
  "status": "running",
  "message": "Bot resumed"
}
```

#### Health Check

```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "uptime": 3600,
  "version": "1.0.0"
}
```

#### Kill Switch

```http
POST /kill-switch
Content-Type: application/json

{
  "action": "activate",
  "reason": "Emergency stop"
}
```

**Parameters**:
- `action` (string, required): `activate`, `deactivate`, or `override`
- `reason` (string, required): Reason for action
- `approved_by` (string, optional): Name of approver

**Response**:
```json
{
  "success": true,
  "kill_switch_active": true,
  "message": "Kill switch activated",
  "timestamp": "2024-02-14T10:00:00Z"
}
```

#### Trigger Recovery

```http
POST /recovery
Content-Type: application/json

{
  "bot": "ndax",
  "force": false
}
```

**Parameters**:
- `bot` (string, required): Bot name to recover
- `force` (boolean, optional): Force recovery even if healthy

**Response**:
```json
{
  "success": true,
  "bot": "ndax",
  "recovery_started": true,
  "message": "Recovery initiated"
}
```

#### Start Sequential

```http
POST /start-sequential
```

Starts all bots in proper order with dependency checks.

**Response**:
```json
{
  "success": true,
  "bots_started": ["ndax", "quantum", "shadowforge"],
  "message": "All bots started successfully"
}
```

#### Stop All

```http
POST /stop-all
Content-Type: application/json

{
  "reason": "Maintenance"
}
```

**Response**:
```json
{
  "success": true,
  "bots_stopped": ["ndax", "quantum", "shadowforge"],
  "message": "All bots stopped"
}
```

### Monitoring API

**Base URL**: `http://localhost:8080`

#### Health Check

```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-02-14T10:00:00Z",
  "service": "health-monitor"
}
```

#### Get Metrics

```http
GET /metrics
```

**Response**:
```json
{
  "timestamp": "2024-02-14T10:00:00Z",
  "bots": {
    "ndax": {
      "status": "running",
      "health": 100,
      "positions": 3,
      "pnl_24h": 125.50,
      "trades_24h": 15
    }
  },
  "limits": {
    "total_max_daily_loss": 400,
    "total_max_exposure": 15000
  },
  "system": {
    "uptime": 3600,
    "memory_usage": 45.2,
    "cpu_usage": 12.5
  }
}
```

#### Get Logs

```http
GET /logs?lines=50
```

**Query Parameters**:
- `lines` (integer, optional): Number of recent log lines (default: 100)

**Response**:
```json
{
  "timestamp": "2024-02-14T10:00:00Z",
  "logs": [
    {
      "file": "bot-coordinator.log",
      "line": "2024-02-14 10:00:00 - INFO - Bot started"
    }
  ]
}
```

#### Get Alerts

```http
GET /alerts
```

**Response**:
```json
{
  "timestamp": "2024-02-14T10:00:00Z",
  "alerts": [
    {
      "type": "warning",
      "message": "Approaching daily loss limit",
      "bot": "ndax",
      "timestamp": "2024-02-14T09:55:00Z"
    }
  ]
}
```

#### Dashboard

```http
GET /
```

Returns the HTML dashboard interface.

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2024-02-14T10:00:00Z"
}
```

### Error Codes

- `BOT_NOT_FOUND`: Specified bot does not exist
- `BOT_ALREADY_RUNNING`: Bot is already in running state
- `BOT_NOT_RUNNING`: Bot is not running
- `KILL_SWITCH_ACTIVE`: Kill switch is active, operation blocked
- `INVALID_PARAMETER`: Invalid request parameter
- `DEPENDENCY_FAILURE`: Bot dependency check failed
- `CONFIGURATION_ERROR`: Configuration file error
- `INTERNAL_ERROR`: Internal server error

## Rate Limits

- 60 requests per minute per endpoint
- 600 requests per hour per client

Exceeded rate limits return:
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT",
  "retry_after": 60
}
```

## WebSocket API (Future)

Real-time updates via WebSocket will be available at:
```
ws://localhost:8000/ws
```

## Data Types

### Bot Status
- `stopped`: Bot is not running
- `starting`: Bot is in startup process
- `running`: Bot is active and trading
- `paused`: Bot is paused (not trading)
- `error`: Bot encountered an error
- `recovery`: Bot is in recovery mode

### Alert Types
- `info`: Informational message
- `warning`: Warning that requires attention
- `high`: High priority issue
- `critical`: Critical issue requiring immediate action

## Code Examples

### Python

```python
import requests

# Start a bot
response = requests.post('http://localhost:8000/start', json={
    'bot': 'ndax',
    'safe_mode': False
})
print(response.json())

# Get status
status = requests.get('http://localhost:8000/status')
print(status.json())

# Activate kill switch
response = requests.post('http://localhost:8000/kill-switch', json={
    'action': 'activate',
    'reason': 'Emergency stop'
})
print(response.json())
```

### JavaScript

```javascript
// Start a bot
fetch('http://localhost:8000/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ bot: 'ndax', safe_mode: false })
})
  .then(res => res.json())
  .then(data => console.log(data));

// Get status
fetch('http://localhost:8000/status')
  .then(res => res.json())
  .then(data => console.log(data));
```

### curl

```bash
# Start bot
curl -X POST http://localhost:8000/start \
  -H "Content-Type: application/json" \
  -d '{"bot":"ndax"}'

# Get status
curl http://localhost:8000/status

# Activate kill switch
curl -X POST http://localhost:8000/kill-switch \
  -H "Content-Type: application/json" \
  -d '{"action":"activate","reason":"test"}'
```

## Webhooks (Optional)

Configure webhooks for events:

### Configuration

In `/config/notification-config.json`:
```json
{
  "webhooks": {
    "enabled": true,
    "endpoints": [
      {
        "url": "https://your-server.com/webhook",
        "events": ["bot_stopped", "kill_switch_triggered"],
        "secret": "your_webhook_secret"
      }
    ]
  }
}
```

### Webhook Payload

```json
{
  "event": "bot_stopped",
  "bot": "ndax",
  "reason": "Manual stop",
  "timestamp": "2024-02-14T10:00:00Z",
  "signature": "hmac_signature"
}
```

## Best Practices

1. **Always check health before operations**
2. **Use safe mode for first restarts**
3. **Monitor metrics during operations**
4. **Handle errors gracefully**
5. **Implement retry logic with backoff**
6. **Validate responses**
7. **Log all API calls**
8. **Use timeouts on requests**

## Changelog

### Version 1.0.0
- Initial API release
- Bot control endpoints
- Status and metrics endpoints
- Kill switch functionality
- Health monitoring
- Alert system

## Support

For API issues:
- Check API documentation
- Review error responses
- Check system logs
- Test with curl/Postman
- Report bugs via GitHub Issues
