# NDAX Quantum Trading Bot - CLI Guide

## Quick Start

The NDAX Quantum Trading Bot can be run from the command line in multiple ways.

## Installation & Running

### Method 1: Using npm script (Recommended)
```bash
npm install
npm run bot
```

### Method 2: Direct node execution
```bash
node bot.js
```

### Method 3: As an executable
```bash
chmod +x bot.js  # Make executable (once)
./bot.js
```

### Method 4: Global installation
```bash
npm install -g .  # Must run from project root
ndax-bot         # Run from anywhere
```

## Configuration

### Using Environment Variables

**Linux/macOS:**
```bash
export TRADING_MODE=paper
export BOT_PORT=9000
npm run bot
```

**Windows:**
```cmd
set TRADING_MODE=paper
set BOT_PORT=9000
npm run bot
```

### Using .env File (Recommended for Development)

Create a `.env` file in the project root:

```env
# Trading Configuration
TRADING_MODE=paper
AUTO_START=false
MAX_TRADES=5
RISK_LEVEL=low

# Freelance Configuration
FREELANCE_ENABLED=false
AUTO_BID=false
AUTO_EXECUTE=false

# AI Configuration
AI_ENABLED=false
TASK_QUEUE_SIZE=10

# Server Configuration
BOT_PORT=9000
NODE_ENV=development
```

Then simply run:
```bash
npm run bot
```

## Available Endpoints

Once the bot is running, access these endpoints:

| Endpoint | Description |
|----------|-------------|
| `http://localhost:9000/status` | Full bot status and configuration |
| `http://localhost:9000/health` | Health check and system metrics |
| `http://localhost:9000/freelance/status` | Freelance orchestrator status |
| `http://localhost:9000/trading/status` | Trading engine status |
| `http://localhost:9000/tasks/queue` | AI task queue status |
| `POST http://localhost:9000/tasks/add` | Add task to AI processing queue |

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `TRADING_MODE` | `paper` | Trading mode: `paper` or `live` |
| `AUTO_START` | `false` | Auto-start trading on bot launch |
| `MAX_TRADES` | `5` | Maximum concurrent trades |
| `RISK_LEVEL` | `low` | Risk level: `low`, `medium`, or `high` |
| `FREELANCE_ENABLED` | `false` | Enable freelance orchestrator |
| `AUTO_BID` | `false` | Automatically bid on freelance jobs |
| `AUTO_EXECUTE` | `false` | Automatically execute freelance jobs |
| `AI_ENABLED` | `false` | Enable AI task processing |
| `TASK_QUEUE_SIZE` | `10` | Maximum AI task queue size |
| `BOT_PORT` | `9000` | HTTP server port |
| `NODE_ENV` | `production` | Environment: `development` or `production` |

## Examples

### Running in Paper Trading Mode
```bash
export TRADING_MODE=paper
export AUTO_START=true
npm run bot
```

### Running with Freelance Enabled
```bash
export FREELANCE_ENABLED=true
export AUTO_BID=true
npm run bot
```

### Running with AI Processing
```bash
export AI_ENABLED=true
export TASK_QUEUE_SIZE=20
npm run bot
```

### Full Production Setup
```bash
export TRADING_MODE=live
export MAX_TRADES=10
export RISK_LEVEL=medium
export FREELANCE_ENABLED=true
export AI_ENABLED=true
export BOT_PORT=9000
npm run bot
```

## Monitoring

### Check Bot Status
```bash
curl http://localhost:9000/status
```

### Check Health
```bash
curl http://localhost:9000/health
```

### Add AI Task
```bash
curl -X POST http://localhost:9000/tasks/add \
  -H "Content-Type: application/json" \
  -d '{"type":"analysis","data":"some data","id":"task-123"}'
```

## Troubleshooting

### Port Already in Use
If port 9000 is already in use:
```bash
export BOT_PORT=9001
npm run bot
```

### Dependencies Not Installed
```bash
npm install
npm run bot
```

### Permission Denied (Linux/macOS)
```bash
chmod +x bot.js
./bot.js
```

## Stopping the Bot

The bot supports graceful shutdown:
- Press `Ctrl+C` to stop
- The bot will complete in-flight operations
- All services will shut down cleanly

## Security Notes

- Never run in `live` trading mode without proper testing
- Keep `AUTO_EXECUTE` disabled for freelance unless fully automated
- Use environment variables for sensitive configuration
- Never commit `.env` files to version control
- Review logs regularly in `./logs/bot-errors.log`

## Further Documentation

- [Main README](README.md) - Project overview
- [Error Handling Guide](docs/ERROR_HANDLING.md) - Error handling system
- [Feature Management Guide](docs/FEATURE_MANAGEMENT.md) - Feature lifecycle
- [System Monitoring Guide](docs/SYSTEM_MONITORING.md) - Health monitoring
