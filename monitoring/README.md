# Monitoring Directory

This directory contains monitoring and dashboard components for the bot coordination system.

## Components

### Status Dashboard (`status-dashboard.html`)
Real-time web dashboard for monitoring all bots.

**Features**:
- Live bot status indicators
- Trading metrics and P&L
- Kill switch controls
- Manual bot controls (start/stop/pause)
- System health metrics

**Access**: http://localhost:8080/

### Health Monitor (`health-monitor.py`)
Python service that provides monitoring APIs and serves the dashboard.

**Endpoints**:
- `GET /` - Dashboard HTML
- `GET /health` - Service health check
- `GET /metrics` - System metrics
- `GET /logs` - Recent log entries
- `GET /alerts` - Active alerts

**Start**: `python monitoring/health-monitor.py`

## Usage

### Starting the Health Monitor

```bash
python monitoring/health-monitor.py
```

The monitor will start on port 8080 by default.

### Accessing the Dashboard

Open your browser to:
```
http://localhost:8080
```

### API Usage

```bash
# Get system metrics
curl http://localhost:8080/metrics

# Get recent logs
curl http://localhost:8080/logs

# Check health
curl http://localhost:8080/health

# Get active alerts
curl http://localhost:8080/alerts
```

## Configuration

The health monitor reads configuration from:
- `config/bot-limits.json` - Trading limits
- `config/kill-switch.json` - Kill switch settings
- `config/api-endpoints.json` - Service endpoints

## Integration with Bot Coordinator

The health monitor works alongside the bot coordinator:

1. **Bot Coordinator** (port 8000): Controls bots
2. **Health Monitor** (port 8080): Monitors and displays status
3. **Individual Bots** (ports 9000+): Trading operations

## Alerts

The system monitors for:
- Bot health failures
- Trading limit violations
- API errors
- Kill switch activations
- System resource issues

Alerts are displayed on the dashboard and logged to files.

## Customization

### Dashboard Styling
Edit `status-dashboard.html` to customize:
- Colors and themes
- Layout and components
- Refresh intervals
- Displayed metrics

### Metrics Collection
Edit `health-monitor.py` to:
- Add new endpoints
- Collect additional metrics
- Integrate with external services
- Add custom alerts

## Monitoring Best Practices

1. **Always keep monitor running** during bot operations
2. **Check dashboard regularly** (every 2-4 hours minimum)
3. **Respond to alerts promptly**
4. **Review logs daily** for patterns
5. **Test kill switch monthly**

## Logs

Monitoring logs are stored in:
```
logs/health-monitor.log
```

## Production Deployment

For production:
1. Run monitor as a service (systemd, supervisor)
2. Add authentication to dashboard
3. Enable HTTPS
4. Set up external alerting (email, Slack)
5. Configure log rotation

## Troubleshooting

**Dashboard not loading**:
```bash
# Check if monitor is running
ps aux | grep health-monitor

# Check port availability
lsof -i :8080

# Restart monitor
pkill -f health-monitor
python monitoring/health-monitor.py
```

**No data showing**:
- Verify bot coordinator is running
- Check API endpoints configuration
- Review monitor logs

**Stale data**:
- Refresh browser (Ctrl+Shift+R)
- Check websocket connection
- Restart monitor service

## Related Documentation

- [SETUP.md](../docs/SETUP.md) - Initial setup
- [BOT-OPERATIONS.md](../docs/BOT-OPERATIONS.md) - Bot operations
- [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) - Common issues
- [API-REFERENCE.md](../docs/API-REFERENCE.md) - API documentation
