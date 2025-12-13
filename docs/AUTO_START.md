# Auto-Start System Guide

## Overview

The auto-start system provides automated setup and service orchestration for The-basics system, ensuring all components start in the correct order with proper health verification.

## Components

1. **auto-setup.sh** - Initial system setup
2. **auto-start.sh** - Service startup orchestration
3. **health-check.sh** - System health monitoring
4. **validate-system.sh** - System validation

## Quick Start

```bash
# 1. Initial setup (run once)
./scripts/auto-setup.sh

# 2. Start all services
./scripts/auto-start.sh

# 3. Check system health
./scripts/health-check.sh

# 4. Validate system
./scripts/validate-system.sh
```

---

## Auto-Setup Script

### Purpose

Automates the initial setup process:
- Detects environment (local/cloud/AWS)
- Installs system dependencies
- Sets up Node.js and Python
- Configures databases
- Creates credentials
- Sets up systemd service (Linux)

### Usage

```bash
# Basic setup
./scripts/auto-setup.sh

# Force local setup
./scripts/auto-setup.sh --local

# Cloud deployment setup
./scripts/auto-setup.sh --cloud

# AWS-specific setup
./scripts/auto-setup.sh --aws
```

### What It Does

1. **Environment Detection**
   - Detects AWS, Railway, Heroku, Docker, or local
   - Adjusts setup based on environment

2. **System Packages**
   - Installs Node.js, Python, Redis, SQLite
   - Platform-specific package managers
   - Build tools and dependencies

3. **Node.js Dependencies**
   - Updates npm
   - Installs package.json dependencies
   - Verifies installation

4. **Python Dependencies**
   - Creates virtual environment
   - Installs requirements.txt
   - Installs chimera requirements

5. **Database Setup**
   - Creates database directories
   - Initializes SQLite databases
   - Starts Redis (if local)

6. **Credential Setup**
   - Creates .env from template
   - Generates encryption key
   - Generates JWT secret

7. **Service Setup** (Linux only)
   - Creates systemd service
   - Enables auto-start on boot
   - Configures logging

8. **Health Checks**
   - Verifies all installations
   - Checks directories and files
   - Validates configuration

### Output

```
=========================================
The-basics System Auto-Setup
=========================================
[INFO] Environment: local
Starting setup process...
✓ curl is installed
✓ wget is installed
✓ git is installed
✓ Node.js dependencies installed
✓ Python dependencies installed
✓ Databases initialized
✓ .env file created
✓ Encryption key generated
✓ JWT secret generated
✓ Systemd service created
✓ All health checks passed
=========================================
Setup Complete!
=========================================
Next steps:
1. Edit .env file with your credentials
2. Run: ./scripts/health-check.sh to verify setup
3. Run: ./scripts/auto-start.sh to start the system
```

### Logs

Setup logs are saved to:
```
.unified-system/logs/setup.log
```

---

## Auto-Start Script

### Purpose

Orchestrates the startup of all system components in the correct order with dependency checking and health verification.

### Usage

```bash
# Start in development mode
./scripts/auto-start.sh
./scripts/auto-start.sh --dev

# Start in production mode
./scripts/auto-start.sh --prod

# Stop all services
./scripts/auto-start.sh --stop

# Check service status
./scripts/auto-start.sh --status
```

### Startup Sequence

1. **Pre-flight Checks**
   - Verify .env exists
   - Check node_modules
   - Check Python venv
   - Load environment variables

2. **Database Services** (if local)
   - Start Redis
   - Start PostgreSQL
   - Start MongoDB

3. **Backend API** (port 8000)
   - Activate Python venv
   - Run unified_system.py
   - Verify health endpoint

4. **AI Orchestrator**
   - Run freelance_engine/orchestrator.py
   - Only if AI platforms enabled

5. **Trading Engine** (port 9000)
   - Run bot.js
   - Only if trading enabled

6. **Dashboard** (port 3000)
   - Development: Vite dev server
   - Production: Built files

7. **Monitoring Services**
   - Prometheus (if enabled)
   - CloudWatch metrics

### Service Management

```bash
# Each service gets:
# - PID file in .unified-system/pids/
# - Log file in .unified-system/logs/
# - Health check verification

# Examples:
# Backend: .unified-system/pids/backend.pid
# Log: .unified-system/logs/backend.log
```

### Output

```
=========================================
The-basics System Auto-Start
=========================================
[INFO] Mode: dev
Running pre-flight checks...
✓ Environment variables loaded
✓ Pre-flight checks passed
Starting services...
Starting database services...
✓ Redis already running
✓ Database services ready
Starting backend API...
✓ backend started (PID: 12345)
✓ backend is running
✓ backend health check passed
Starting AI orchestrator...
✓ ai-orchestrator started (PID: 12346)
Starting trading engine...
[INFO] Trading disabled, skipping engine
Starting dashboard...
✓ dashboard started (PID: 12347)
✓ dashboard is running
✓ dashboard health check passed
=========================================
Startup sequence complete!
=========================================
✓ All services are running

Services:
  Dashboard:  http://localhost:3000
  Backend:    http://localhost:8000
  Bot:        http://localhost:9000

Logs: .unified-system/logs
PIDs: .unified-system/pids

To stop all services: ./scripts/auto-start.sh --stop
To check status: ./scripts/auto-start.sh --status
```

### Logs

Startup logs and service logs:
```
.unified-system/logs/startup.log
.unified-system/logs/backend.log
.unified-system/logs/dashboard.log
.unified-system/logs/ai-orchestrator.log
.unified-system/logs/trading-engine.log
```

---

## Health Check Script

### Purpose

Continuously monitor system health, verify services, check API endpoints, and validate configurations.

### Usage

```bash
# Basic health check
./scripts/health-check.sh

# Verbose output
./scripts/health-check.sh --verbose
./scripts/health-check.sh -v

# JSON output (for monitoring systems)
./scripts/health-check.sh --json
./scripts/health-check.sh -j
```

### What It Checks

1. **Service Status**
   - Backend running
   - Dashboard running
   - AI orchestrator (if enabled)
   - Trading engine (if enabled)

2. **API Endpoints**
   - Backend API responsive
   - Dashboard accessible
   - Bot API (if running)

3. **Database Connections**
   - Redis ping
   - PostgreSQL query
   - MongoDB ping
   - SQLite databases exist

4. **Resource Usage**
   - CPU utilization
   - Memory usage
   - Disk space
   - Log directory size

5. **Credential Validation**
   - .env file exists
   - Required credentials present
   - Credential formats valid

6. **File and Path Validation**
   - Critical files exist
   - Critical directories exist
   - Import paths valid

### Output

```
=========================================
The-basics System Health Check
=========================================

=========================================
Service Status Checks
=========================================
[✓] Service backend is running (PID: 12345)
[✓] Service dashboard is running (PID: 12347)

=========================================
API Endpoint Checks
=========================================
[✓] Backend API is responsive (port 8000)
[✓] Dashboard is responsive (port 3000)

=========================================
Database Connection Checks
=========================================
[✓] Redis is connected and responsive
[✓] SQLite system database exists

=========================================
Resource Usage
=========================================
[✓] CPU usage is normal (15.3%)
[✓] Memory usage is normal (42.1%)
[✓] Disk usage is normal (35%)

=========================================
Credential Validation
=========================================
[✓] .env file exists
[✓] JWT_SECRET is configured
[✓] ENCRYPTION_KEY is configured

=========================================
Health Summary
=========================================
Score: 18 / 18 (100.00%)
Status: All systems healthy ✓
```

### JSON Output

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "health_score": 18,
  "max_score": 18,
  "health_percent": 100.00,
  "status": "healthy",
  "issues": []
}
```

### Exit Codes

- `0` - All systems healthy or operational with warnings
- `1` - Critical issues detected

### Monitoring Integration

```bash
# Use with monitoring systems
./scripts/health-check.sh --json | \
  curl -X POST https://monitoring.example.com/health \
  -H "Content-Type: application/json" \
  -d @-

# Cron job for periodic checks
*/5 * * * * /path/to/scripts/health-check.sh --json > /var/log/health-check.log
```

---

## Validate System Script

### Purpose

Comprehensive validation of file paths, imports, credentials, and configurations.

### Usage

```bash
# Basic validation
./scripts/validate-system.sh

# Auto-fix issues
./scripts/validate-system.sh --fix
./scripts/validate-system.sh -f

# Verbose output
./scripts/validate-system.sh --verbose
./scripts/validate-system.sh -v

# Both fix and verbose
./scripts/validate-system.sh --fix --verbose
```

### What It Validates

1. **File Paths**
   - Critical files exist
   - Critical directories exist

2. **Import Validation**
   - JavaScript imports resolve
   - Python imports work
   - No broken dependencies

3. **Credential Validation**
   - All API keys present
   - Correct format
   - Valid wallet addresses
   - Proper AWS credentials

4. **Configuration Files**
   - features.yaml valid YAML
   - package.json valid JSON
   - Terraform configs valid

5. **Dependencies**
   - node_modules installed
   - Python venv exists
   - Required packages present

6. **Permissions**
   - Scripts executable
   - Directories writable

### Output

```
=========================================
The-basics System Validation
=========================================

=========================================
File Path Validation
=========================================
[✓] File exists: package.json
[✓] File exists: server.js
[✓] File exists: unified_system.py
[✓] Directory exists: src
[✓] Directory exists: scripts

=========================================
Import Validation
=========================================
[✓] error-handler.js imports are valid
[✓] freeze-detector.js imports are valid
[✓] feature-manager.js imports are valid

=========================================
Credential Validation
=========================================
[✓] .env file exists
[✓] JWT_SECRET is sufficiently long
[✓] ENCRYPTION_KEY is correct length
[✓] WALLET_ADDRESS format is valid

=========================================
Validation Summary
=========================================
Total checks: 25
Passed: 24
Warnings: 1
Failed: 0
Success rate: 96.00%
✓ System validation passed
```

### Auto-Fix

When run with `--fix`, the script automatically:
- Makes scripts executable
- Creates missing directories
- Generates missing security keys

---

## Systemd Service (Linux)

### Service File

Located at: `/etc/systemd/system/the-basics.service`

```ini
[Unit]
Description=The-basics Autonomous Trading and AI System
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/The-basics
ExecStart=/path/to/scripts/auto-start.sh
Restart=on-failure
RestartSec=10
StandardOutput=append:/path/to/.unified-system/logs/service.log
StandardError=append:/path/to/.unified-system/logs/service-error.log

[Install]
WantedBy=multi-user.target
```

### Service Management

```bash
# Enable auto-start on boot
sudo systemctl enable the-basics

# Start service
sudo systemctl start the-basics

# Stop service
sudo systemctl stop the-basics

# Restart service
sudo systemctl restart the-basics

# Check status
sudo systemctl status the-basics

# View logs
sudo journalctl -u the-basics -f
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
cat .unified-system/logs/startup.log

# Check specific service
cat .unified-system/logs/backend.log

# Check permissions
ls -la scripts/*.sh

# Make scripts executable
chmod +x scripts/*.sh
```

### Port Already in Use

```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in .env
PORT=3001
PYTHON_PORT=8001
```

### Database Connection Failed

```bash
# Check Redis
redis-cli ping

# Start Redis
redis-server --daemonize yes

# Check PostgreSQL
pg_isready

# Check MongoDB
mongod --version
```

### Missing Dependencies

```bash
# Reinstall Node.js dependencies
rm -rf node_modules
npm install

# Reinstall Python dependencies
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Best Practices

### 1. Always Run Health Checks

```bash
# After starting
./scripts/auto-start.sh
sleep 10
./scripts/health-check.sh
```

### 2. Monitor Logs

```bash
# Tail all logs
tail -f .unified-system/logs/*.log

# Or use multitail
multitail .unified-system/logs/*.log
```

### 3. Regular Validation

```bash
# Add to cron
0 0 * * * /path/to/scripts/validate-system.sh
```

### 4. Automated Recovery

```bash
# Use systemd for auto-restart
sudo systemctl enable the-basics

# Or use PM2
pm2 start scripts/auto-start.sh --name the-basics
pm2 save
pm2 startup
```

### 5. Backup Before Updates

```bash
# Backup .env
cp .env .env.backup

# Backup databases
cp -r .unified-system/db .unified-system/db.backup
```

---

## Integration with CI/CD

### GitHub Actions

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup
        run: ./scripts/auto-setup.sh --cloud
      
      - name: Validate
        run: ./scripts/validate-system.sh
      
      - name: Start Services
        run: ./scripts/auto-start.sh --prod
      
      - name: Health Check
        run: ./scripts/health-check.sh
```

### Docker Integration

```dockerfile
FROM node:18

WORKDIR /app
COPY . .

RUN ./scripts/auto-setup.sh --cloud
RUN ./scripts/validate-system.sh

CMD ["./scripts/auto-start.sh", "--prod"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD ./scripts/health-check.sh || exit 1
```

---

## Support

For auto-start issues:
1. Check startup logs
2. Verify pre-flight checks pass
3. Test services individually
4. Check firewall rules
5. Verify environment variables
