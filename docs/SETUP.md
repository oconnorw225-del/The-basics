# Bot System Setup Guide

## Overview

This guide covers the initial setup and configuration of the unified bot coordination system that manages three trading bots:
- **NDAX Bot**: NDAX exchange trading
- **Quantum Bot**: Quantum-enhanced trading strategies
- **ShadowForge Bot**: AI-powered trading strategies

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **Operating System**: Linux, macOS, or Windows WSL
- **Memory**: Minimum 4GB RAM
- **Storage**: At least 2GB free space

### Required Access
- GitHub repository access
- API keys for trading exchanges (if live trading)
- Email/Slack/Discord webhook URLs (for notifications)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/oconnorw225-del/The-basics.git
cd The-basics
```

### 2. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional packages for bot coordinator
pip install aiohttp
```

### 3. Install Node.js Dependencies

```bash
npm install
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Trading Mode
TRADING_MODE=paper  # 'paper' for simulation, 'live' for real trading

# Bot Settings
AUTO_START=false
MAX_TRADES=5
RISK_LEVEL=low

# API Keys (for live trading)
NDAX_API_KEY=your_api_key_here
NDAX_API_SECRET=your_api_secret_here

# Notifications
EMAIL_ENABLED=false
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=

# Server Ports
BOT_PORT=9000
COORDINATOR_PORT=8000
MONITOR_PORT=8080
```

### 5. Configure Bot Limits

Review and adjust `/config/bot-limits.json`:

```json
{
  "ndax_bot": {
    "max_daily_loss": 100,
    "max_daily_trades": 50,
    "max_position_size": 1000
  }
}
```

**Important**: Start with conservative limits, especially for live trading!

### 6. Configure Kill Switch

Review `/config/kill-switch.json`:

```json
{
  "enabled": true,
  "auto_trigger": true,
  "manual_override_allowed": true
}
```

### 7. Set Up Logging

Create logs directory:

```bash
mkdir -p logs/audit
```

### 8. Verify Installation

Run the verification script:

```bash
python backend/bot-coordinator.py --version
node bot.js --version
```

## Starting the System

### Option 1: Start Individual Components

#### Start Bot Coordinator
```bash
python backend/bot-coordinator.py
```

#### Start Health Monitor
```bash
python monitoring/health-monitor.py
```

#### Start NDAX Bot
```bash
node bot.js
```

### Option 2: Start All Components (Recommended)

```bash
./start.sh
```

## Accessing the Dashboard

Once the health monitor is running, access the dashboard at:

```
http://localhost:8080
```

The dashboard provides:
- Real-time bot status
- Trading metrics
- Kill switch controls
- Manual bot controls

## Initial Testing

### 1. Verify System Health

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-02-14T10:00:00Z",
  "service": "health-monitor"
}
```

### 2. Check Bot Coordinator Status

```bash
curl http://localhost:8000/health
```

### 3. Test Kill Switch

From the dashboard or via API:

```bash
curl -X POST http://localhost:8000/kill-switch \
  -H "Content-Type: application/json" \
  -d '{"action": "activate", "reason": "test"}'
```

## Configuration Best Practices

### Safety First
1. **Always start in paper trading mode**
2. **Set conservative limits initially**
3. **Enable kill switch with auto-trigger**
4. **Require manual approval for recovery**
5. **Monitor closely for first 24 hours**

### Recommended Initial Limits
- Max daily loss: $100
- Max position size: $1000
- Max concurrent positions: 3
- Stop loss: 5%

### Gradual Scaling
1. Run in paper mode for 1-2 weeks
2. Start with minimal limits in live mode
3. Gradually increase limits as confidence grows
4. Always maintain kill switch protection

## Monitoring Setup

### GitHub Actions Workflows

The system includes automated monitoring via GitHub Actions:

1. **Bot Health Check** - Runs every 15 minutes
   - Go to Actions → Bot Health Check → Enable

2. **Bot Recovery** - Triggered automatically on failures
   - Already enabled, runs on-demand

3. **Auto Fix and Deploy** - Runs on code changes
   - Enabled for main branch

### Email Notifications (Optional)

Configure in `/config/notification-config.json`:

```json
{
  "channels": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your-email@gmail.com",
      "recipients": ["alert@example.com"]
    }
  }
}
```

### Slack Notifications (Optional)

1. Create a Slack webhook URL
2. Add to `/config/notification-config.json`:

```json
{
  "channels": {
    "slack": {
      "enabled": true,
      "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
      "channel": "#trading-alerts"
    }
  }
}
```

## Troubleshooting Setup

### Issue: Python dependencies fail to install
```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

### Issue: Port already in use
```bash
# Check what's using the port
lsof -i :8080

# Kill the process or change port in config
```

### Issue: Bot coordinator won't start
```bash
# Check logs
tail -f logs/bot-coordinator.log

# Verify config files
python -c "import json; json.load(open('config/bot-limits.json'))"
```

### Issue: Dashboard not loading
```bash
# Verify health monitor is running
ps aux | grep health-monitor

# Check dashboard file exists
ls -la monitoring/status-dashboard.html
```

## Next Steps

After setup is complete:

1. Read [BOT-OPERATIONS.md](BOT-OPERATIONS.md) to understand bot coordination
2. Review [SAFETY-PROTOCOLS.md](SAFETY-PROTOCOLS.md) for safety procedures
3. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
4. Review [API-REFERENCE.md](API-REFERENCE.md) for API documentation

## Support

For issues or questions:
1. Check the troubleshooting guide
2. Review GitHub Issues
3. Check workflow run logs in Actions tab
4. Review system logs in `/logs` directory

## Security Notes

⚠️ **Important Security Reminders**:
- Never commit `.env` file to git
- Keep API keys secure and rotated regularly
- Use separate API keys for paper and live trading
- Enable 2FA on all exchange accounts
- Review security logs regularly
- Keep system and dependencies updated

## Updates and Maintenance

### Keeping System Updated
```bash
# Update repository
git pull origin main

# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update Node.js dependencies
npm update
```

### Backup Configuration
```bash
# Backup current config
tar -czf config-backup-$(date +%Y%m%d).tar.gz config/
```

### Log Rotation
```bash
# Archive old logs
find logs/ -name "*.log" -mtime +30 -exec gzip {} \;
```
