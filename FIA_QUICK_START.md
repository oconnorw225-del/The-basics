# FIA Quick Reference

## One Command to Rule Them All

```bash
npm run fia
```

That's it! FIA does everything automatically:
- ✅ Validates system (100-point score)
- ✅ Auto-configures missing components
- ✅ Starts all services in correct order
- ✅ Verifies health and reports status

## Common Commands

```bash
# Start everything
npm run fia

# Force start (bypass validation)
npm run fia:force

# Using shell script
./scripts/fia.sh

# Direct execution
node scripts/fia.js
```

## What You Get

After ~30-60 seconds:

```
✅ Backend API Server    → http://localhost:3000
✅ Bot Coordinator       → Background process
✅ NDAX Trading Bot      → http://localhost:9000
✅ Dashboard Backend     → http://localhost:8000
✅ Dashboard Frontend    → http://localhost:5173
```

## Before First Run

```bash
# Install dependencies (optional - FIA does this)
npm install
pip3 install -r requirements.txt

# Or just run FIA and let it handle everything
npm run fia
```

## Stopping Services

```bash
# Stop Node services
pkill -f "node server.js"
pkill -f "node backend/ndax_bot.js"

# Stop Python services
pkill -f "bot-coordinator.py"
pkill -f "uvicorn dashboard"

# Or kill by PID from FIA output
kill <PID>
```

## Check System Status

```bash
# Health checks
curl http://localhost:3000/health
curl http://localhost:9000/health
curl http://localhost:8000/health

# View logs
tail -f .unified-system/logs/*.log

# Check running processes
ps aux | grep -E "node|python3|uvicorn"
```

## Troubleshooting

### Score Too Low
```bash
# Run setup first
./scripts/setup.sh

# Then try FIA again
npm run fia
```

### Port Conflicts
```bash
# Find what's using port
lsof -i :3000

# Kill it
kill -9 <PID>

# Restart FIA
npm run fia
```

### Service Won't Start
```bash
# Check logs
tail -f .unified-system/logs/*.log

# Test service manually
node server.js
# or
python3 backend/bot-coordinator.py
```

## Production Mode

```bash
# Set environment
export NODE_ENV=production

# Copy production env
cp .env.production.template .env.production

# Edit with real values
nano .env.production

# Run FIA
npm run fia
```

## Validation Score

FIA checks 5 categories (20 points each):

1. **Config Files** - All JSON valid
2. **Environment** - .env exists
3. **Dependencies** - Node & Python packages
4. **Security** - Safety switch, JWT secrets
5. **Ports** - Required ports available

**Minimum**: 60/100 to proceed

## Full Documentation

See [FIA_ORCHESTRATOR.md](./FIA_ORCHESTRATOR.md) for complete details.

---

**Remember**: `npm run fia` is all you need! 🚀
