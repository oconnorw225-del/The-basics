# FIA - Full Integration Activation

## 🚀 One-Command System Startup

The **FIA (Full Integration Activation)** orchestrator is your intelligent command center for starting the entire trading system with 100% compliance validation.

## Quick Start

```bash
# Using npm (recommended)
npm run fia

# Using the shell script
./scripts/fia.sh

# Using bun (if installed)
bun fia

# Direct execution
node scripts/fia.js
```

## What FIA Does

FIA orchestrates your entire system startup with intelligence and precision:

### 1. 📋 Pre-Flight Validation (100-Point System)

Before starting anything, FIA validates:

- **Configuration Files (20 pts)**: All JSON configs valid
- **Environment Setup (20 pts)**: .env files present
- **Dependencies (20 pts)**: Node and Python packages
- **Security Settings (20 pts)**: Safety switch enabled, JWT secrets
- **Port Availability (20 pts)**: Required ports free

**Minimum Score**: 60/100 to proceed (configurable)

### 2. ⚙️ Smart Auto-Configuration

If issues are detected, FIA automatically:

- Installs missing dependencies
- Generates secure JWT secrets (64-char hex)
- Creates environment files from templates
- Enables safety protections
- Sets optimal configurations

### 3. 🎯 Ordered Service Startup

Services start in dependency order:

1. **Backend API Server** (Port 3000)
   - Core Express server
   - Health endpoint active
   
2. **Bot Coordinator** (Background)
   - Manages all trading bots
   - Safety monitoring
   
3. **NDAX Trading Bot** (Port 9000)
   - Primary trading interface
   - Real-time market data
   
4. **Dashboard Backend** (Port 8000)
   - FastAPI backend
   - WebSocket support
   
5. **Dashboard Frontend** (Port 5173)
   - React dashboard
   - Real-time monitoring

### 4. ✅ Health Validation

After startup, FIA verifies:

- HTTP health checks pass
- Services respond correctly
- Inter-service communication works
- 100% operational status achieved

### 5. 📊 Status Report

FIA provides comprehensive reporting:

```
╔════════════════════════════════════════════╗
║          ACTIVATION COMPLETE! 🚀            ║
╚════════════════════════════════════════════╝

📊 Final Scores:
   Validation Score: 95/100
   Operational Status: 100%
   Total Duration: 23s

🌐 Access Points:
   Dashboard:     http://localhost:5173
   API Server:    http://localhost:3000
   Bot API:       http://localhost:9000
   Dashboard API: http://localhost:8000

📝 Active Processes:
   Backend API Server: PID 12345
   Bot Coordinator: PID 12346
   NDAX Trading Bot: PID 12347
   Dashboard Backend: PID 12348
   Dashboard Frontend: PID 12349
```

## Validation Score Breakdown

| Category | Points | What's Checked |
|----------|--------|----------------|
| Configuration Files | 20 | All 5 JSON configs valid |
| Environment Setup | 20 | .env exists with values |
| Dependencies | 20 | Node & Python packages |
| Security Settings | 20 | Safety enabled, secrets set |
| Port Availability | 20 | Ports 3000/5000/8000/9000 free |
| **Total** | **100** | **Minimum 60 to proceed** |

## Advanced Usage

### Force Start (Bypass Validation)

```bash
npm run fia:force
```

⚠️ **Warning**: Only use if you know what you're doing!

### Environment Variables

FIA respects these environment variables:

- `FIA_MIN_SCORE`: Minimum validation score (default: 60)
- `FIA_AUTO_FIX`: Enable auto-fix (default: true)
- `FIA_VERBOSE`: Detailed logging (default: false)

Example:
```bash
FIA_MIN_SCORE=80 FIA_VERBOSE=true npm run fia
```

### Stopping Services

FIA starts services in detached mode. To stop them:

```bash
# Stop all Node processes
pkill -f "node server.js"
pkill -f "node backend/ndax_bot.js"

# Stop Python processes
pkill -f "bot-coordinator.py"
pkill -f "uvicorn dashboard"

# Or kill specific PIDs from the status report
kill <PID>
```

## What Gets Started

### Backend API Server (Node.js)
- **Port**: 3000
- **Command**: `node server.js`
- **Health**: `http://localhost:3000/health`
- **Purpose**: Core API, authentication, WebSocket

### Bot Coordinator (Python)
- **Port**: Background process
- **Command**: `python3 backend/bot-coordinator.py`
- **Purpose**: Manages trading bots, monitors safety

### NDAX Trading Bot (Node.js)
- **Port**: 9000
- **Command**: `node backend/ndax_bot.js`
- **Health**: `http://localhost:9000/health`
- **Purpose**: NDAX exchange integration, trading

### Dashboard Backend (FastAPI)
- **Port**: 8000
- **Command**: `uvicorn dashboard.backend.main:app`
- **Health**: `http://localhost:8000/health`
- **Purpose**: Dashboard API, real-time data

### Dashboard Frontend (React)
- **Port**: 5173
- **Command**: `npm run dev`
- **Purpose**: Web dashboard, monitoring UI

## Startup Order Logic

FIA ensures dependencies are met:

```
1. Backend API      → Core infrastructure
2. Bot Coordinator  → Bot management (depends on API)
3. Trading Bots     → Market interface (depends on coordinator)
4. Dashboard API    → Data aggregation (depends on bots)
5. Dashboard UI     → User interface (depends on dashboard API)
```

Each service waits for the previous to initialize before starting.

## Troubleshooting

### Validation Fails (Score < 60)

**Problem**: Pre-flight check score too low

**Solutions**:
1. Run setup first: `./scripts/setup.sh`
2. Install dependencies: `npm install && pip3 install -r requirements.txt`
3. Generate environment: `python3 scripts/setup_env.py --auto`
4. Force start: `npm run fia:force` (not recommended)

### Port Already in Use

**Problem**: Service fails to start due to port conflict

**Solutions**:
```bash
# Find what's using the port
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or restart FIA (it detects running services)
npm run fia
```

### Service Won't Start

**Problem**: Individual service fails

**Solutions**:
1. Check logs: `tail -f .unified-system/logs/*.log`
2. Test manually: `node server.js` or `python3 backend/bot-coordinator.py`
3. Verify dependencies: `npm list` and `pip3 list`
4. Check configuration: Ensure config files are valid JSON

### Health Checks Fail

**Problem**: Service starts but health check fails

**Solutions**:
1. Wait longer (services may still be initializing)
2. Check if port is actually listening: `netstat -an | grep 3000`
3. Test manually: `curl http://localhost:3000/health`
4. Review logs for errors

## Configuration

### Minimum Score Threshold

Edit `scripts/fia.js` to change:

```javascript
return score >= 60; // Change this value
```

### Service Wait Times

Adjust wait times in the service definitions:

```javascript
{
  name: 'Backend API Server',
  waitTime: 5000, // Milliseconds to wait
}
```

### Health Check URLs

Customize health check endpoints:

```javascript
{
  name: 'Backend API Server',
  healthCheck: 'http://localhost:3000/health',
}
```

## Integration with Other Scripts

FIA works alongside existing scripts:

- **`./scripts/setup.sh`**: Initial setup, run once
- **`npm run fia`**: Start everything (run anytime)
- **`npm test`**: Run tests
- **`npm run unified`**: Alternative unified system

## Development Mode

For development, you can start services individually:

```bash
# Terminal 1: Backend
npm start

# Terminal 2: Dashboard Backend
cd dashboard/backend && uvicorn main:app --reload

# Terminal 3: Dashboard Frontend
npm run dev
```

FIA is designed for production/demo environments where you want everything running together.

## Production Deployment

For production:

1. Set environment: `NODE_ENV=production`
2. Use production env: `.env.production`
3. Run FIA: `npm run fia`

FIA automatically detects production mode and adjusts:
- Uses production database
- Enables all security features
- Disables debug logging
- Optimizes configurations

## Monitoring

After FIA starts the system:

```bash
# Watch all logs
tail -f .unified-system/logs/*.log

# Check specific service
curl http://localhost:3000/health

# View bot status
curl http://localhost:9000/status

# Dashboard metrics
curl http://localhost:8000/metrics
```

## Safety Features

FIA ensures safety by:

- ✅ Validating safety switch is enabled
- ✅ Checking all configurations before startup
- ✅ Starting services in safe order
- ✅ Verifying health before declaring operational
- ✅ Providing clear feedback at each step

## Performance

Typical FIA execution:

- **Validation**: 2-5 seconds
- **Auto-configuration**: 5-10 seconds (if needed)
- **Service startup**: 15-30 seconds
- **Health checks**: 5-10 seconds
- **Total**: 30-60 seconds to full operation

## FAQ

**Q: Do I need Bun.js?**  
A: No, FIA works with Node.js. Bun is optional for better performance.

**Q: Can I customize what services start?**  
A: Yes, edit the `serviceSequence` array in `scripts/fia.js`.

**Q: What if a service is already running?**  
A: FIA detects this and skips starting it again.

**Q: How do I stop everything?**  
A: Use `pkill` commands or kill individual PIDs from the status report.

**Q: Can I run FIA multiple times?**  
A: Yes, it's idempotent. It detects what's running and only starts what's needed.

**Q: What happens if validation fails?**  
A: FIA stops and reports issues. Fix them or use `--force` to bypass.

## Contributing

To add a new service to FIA:

1. Add to `serviceSequence` in `scripts/fia.js`
2. Specify command, port, health check
3. Set appropriate `waitTime`
4. Update this documentation

## Support

If FIA isn't working:

1. Check the troubleshooting section
2. Review logs in `.unified-system/logs/`
3. Run validation manually: See pre-flight checks
4. File an issue with FIA output

## License

Same as parent project (MIT)

---

**FIA** - Because starting your trading system should be one command, not twenty. 🚀
