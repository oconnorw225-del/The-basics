# 🚀 Autonomous Bot System - Deployment Guide

Complete deployment instructions for the autonomous bot system.

## ⚠️ SECURITY UPDATE

**IMPORTANT:** Next.js has been updated from 14.1.0 to 15.0.8 to patch critical vulnerabilities (DoS, Authorization Bypass, Cache Poisoning, SSRF). See [SECURITY_FIX_NEXTJS.md](SECURITY_FIX_NEXTJS.md) for details.

## 📋 Prerequisites

### System Requirements
- Python 3.11+
- Node.js 18+
- Git
- 2GB+ RAM
- 10GB+ disk space

### Required Secrets
Set these in GitHub Settings → Secrets and variables → Actions:

1. **SENDGRID_API_KEY** (Required for email notifications)
   - Get from: https://app.sendgrid.com/settings/api_keys
   - Used by: `.github/workflows/send_email_notifications.yml`

2. **GITHUB_TOKEN** (Auto-available in GitHub Actions)
   - Used by: Credential scanner to access repositories
   - Automatically provided by GitHub

## 🎯 Quick Deploy

### Step 1: Clone and Setup

```bash
# Clone repository
git clone https://github.com/oconnorw225-del/The-basics.git
cd The-basics

# Install Python dependencies
pip install -r requirements.txt
pip install -r dashboard/backend/requirements.txt

# Install Node dependencies (for dashboard)
cd dashboard/frontend
npm install
cd ../..
```

### Step 2: Configure Environment

Create `.env` file in project root:

```bash
# GitHub Access
GITHUB_TOKEN=ghp_your_token_here

# Email (SendGrid)
SENDGRID_API_KEY=SG.your_key_here

# Optional: Exchange APIs
NDAX_API_KEY=your_ndax_key
NDAX_SECRET=your_ndax_secret
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET=your_binance_secret
```

### Step 3: Initialize System

```bash
# Run complete integration (initializes everything)
python backend/complete_integration.py
```

This will:
1. ✅ Scan for credentials across all sources
2. ✅ Discover and register 44+ bots
3. ✅ Initialize asset recovery system
4. ✅ Generate dashboard components
5. ✅ Send initialization email to oconnorw225@gmail.com

### Step 4: Start Dashboard

In separate terminals:

```bash
# Terminal 1: Backend API
cd dashboard/backend
python main.py

# Terminal 2: Frontend
cd dashboard/frontend
npm run dev
```

Access:
- **Dashboard:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 📧 Email Notifications

### Setup

1. **Get SendGrid API Key:**
   - Sign up at https://sendgrid.com
   - Create API key with "Mail Send" permissions
   - Add to GitHub Secrets as `SENDGRID_API_KEY`

2. **Email Recipient:**
   - **HARDCODED:** oconnorw225@gmail.com
   - Cannot be changed (security feature)
   - All emails go to this address only

3. **Workflow:**
   - Runs every 30 minutes via `.github/workflows/send_email_notifications.yml`
   - Checks `notifications/outgoing.json` for pending emails
   - Sends via SendGrid
   - Updates `notifications/sent.json`

### Test Email System

```bash
# Queue a test notification
python backend/email_notifier.py

# Check pending notifications
cat notifications/outgoing.json

# Manual trigger (requires GitHub Actions)
# Go to: Actions → Send Email Notifications → Run workflow
```

## 🤖 System Operations

### Continuous Operations

Once started, the system runs these tasks automatically:

1. **Recovery Scans:** Every 2 hours
   - Scans exchanges, wallets, MtGox claims
   - Emails results if assets found

2. **Bot Discovery:** Every 30 minutes
   - Chimera V8 scans codebase
   - Registers new bots
   - Updates dashboard

3. **Credential Rescans:** Every hour
   - Re-scans all sources
   - Updates shared pool

4. **Daily Summary:** 8 AM daily
   - System statistics
   - Performance metrics
   - Emails to oconnorw225@gmail.com

5. **Chimera Upgrades:** Every 6 hours
   - Self-improving algorithm
   - Meta-learning from patterns

### Manual Operations

```bash
# Test credential scanner
python -c "
import asyncio
from backend.autonomous_credential_scanner import credential_scanner
result = asyncio.run(credential_scanner.scan_everything())
print(f'Found {result[\"credentials_found\"]} credentials')
"

# Test bot discovery
python -c "
import asyncio
from backend.chimera_dashboard_writer import chimera_writer
result = asyncio.run(chimera_writer.auto_scan_and_register_all())
print(f'Found {result[\"total_discovered\"]} bots')
"

# Test complete system
python backend/complete_integration.py

# Test dashboard backend only
cd dashboard/backend && python main.py

# Test email notifications
python backend/email_notifier.py
```

## 🏭 Production Deployment

### Option 1: Single Server

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r dashboard/backend/requirements.txt
cd dashboard/frontend && npm install && cd ../..

# Build frontend
cd dashboard/frontend
npm run build
cd ../..

# Start with systemd
sudo cp deployment/autonomous-bots.service /etc/systemd/system/
sudo systemctl enable autonomous-bots
sudo systemctl start autonomous-bots

# Start dashboard backend
cd dashboard/backend
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Serve frontend (production)
cd dashboard/frontend
npm start
```

### Option 2: Docker

```bash
# Build images
docker build -t autonomous-bots-backend -f Dockerfile.backend .
docker build -t autonomous-bots-dashboard -f Dockerfile.dashboard ./dashboard

# Run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Option 3: Cloud Platforms

#### Heroku
```bash
heroku create autonomous-bots
heroku config:set GITHUB_TOKEN=your_token
heroku config:set SENDGRID_API_KEY=your_key
git push heroku main
```

#### Railway
```bash
railway init
railway add
railway up
```

#### AWS/GCP/Azure
See `CLOUD_DEPLOYMENT_GUIDE.md` for platform-specific instructions.

## 🔒 Security Checklist

- [ ] SENDGRID_API_KEY set in GitHub Secrets
- [ ] GITHUB_TOKEN available (auto or manual)
- [ ] Email recipient verified (oconnorw225@gmail.com)
- [ ] `.env` file NOT committed to git
- [ ] Credentials files in `.gitignore`
- [ ] Dashboard CORS configured correctly
- [ ] API endpoints secured (if exposed publicly)
- [ ] Firewall rules configured
- [ ] SSL/TLS enabled for production

## 🧪 Testing

### Unit Tests

```bash
# Test individual components
python backend/bot_registry.py
python backend/email_notifier.py
python backend/autonomous_credential_scanner.py

# Test bot discovery
python backend/chimera_dashboard_writer.py

# Test dashboard backend
cd dashboard/backend && python -c "from main import app; print('OK')"
```

### Integration Tests

```bash
# Full system test
python backend/complete_integration.py

# Dashboard API test
curl http://localhost:8000/health
curl http://localhost:8000/api/bots
curl http://localhost:8000/api/stats
```

### WebSocket Test

```javascript
// In browser console at http://localhost:3000
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', e.data);
ws.send(JSON.stringify({type: 'ping'}));
```

## 📊 Monitoring

### System Health

```bash
# Check bot registry
python -c "from backend.bot_registry import bot_registry; print(bot_registry.get_registry_stats())"

# Check credentials
python -c "from backend.bot_credential_sharing import credential_sharing; print(credential_sharing.get_shared_pool_status())"

# Check recovery
python -c "from backend.complete_asset_recovery_system import asset_recovery; print(asset_recovery.get_recovery_stats())"

# Check notifications
python -c "from backend.email_notifier import email_notifier; print(email_notifier.get_notification_stats())"
```

### Logs

```bash
# Backend logs
tail -f backend.log

# Dashboard backend logs
tail -f dashboard/backend/api.log

# System integration logs
tail -f integration.log

# Email notification logs
tail -f notifications/email.log
```

## 🔧 Troubleshooting

### System Won't Start

1. Check Python version: `python --version` (need 3.11+)
2. Check dependencies: `pip list | grep -E "fastapi|aiohttp|uvicorn"`
3. Check for port conflicts: `lsof -i :8000`
4. Check environment variables: `env | grep -E "GITHUB_TOKEN|SENDGRID"`

### Emails Not Sending

1. Verify SENDGRID_API_KEY is set
2. Check `notifications/outgoing.json` has pending emails
3. Manually trigger workflow in GitHub Actions
4. Check SendGrid dashboard for API usage

### Bots Not Discovered

1. Run bot discovery manually: `python backend/chimera_dashboard_writer.py`
2. Check bot files exist in `backend/`, `src/`, etc.
3. Verify bot naming matches patterns (e.g., `*Bot`, `*Agent`)
4. Check bot registry: `cat config/bot_registry.json`

### Dashboard Not Loading

1. Check backend is running: `curl http://localhost:8000/health`
2. Check frontend build: `cd dashboard/frontend && npm run build`
3. Check browser console for errors
4. Verify WebSocket connection at `ws://localhost:8000/ws`

### Credentials Not Found

1. Check GitHub token is valid: `echo $GITHUB_TOKEN`
2. Verify repository access permissions
3. Check credential patterns in `autonomous_credential_scanner.py`
4. Look in `config/auto_discovered_credentials.json`

## 📞 Support

For issues or questions:
- **Email:** oconnorw225@gmail.com
- **Repository:** https://github.com/oconnorw225-del/The-basics
- **Issues:** https://github.com/oconnorw225-del/The-basics/issues

## 🎉 Success Criteria

Your deployment is successful when:

✅ System initializes without errors
✅ Credentials discovered (or gatekeeper alert sent)
✅ 44+ bots discovered and registered
✅ Dashboard accessible at http://localhost:3000
✅ API responding at http://localhost:8000
✅ WebSocket connected (green indicator)
✅ Email sent to oconnorw225@gmail.com
✅ Recovery scans running every 2 hours
✅ Bot discovery running every 30 minutes

Congratulations! Your autonomous bot system is now operational. 🚀
