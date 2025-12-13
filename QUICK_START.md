# 🚀 Unified System - Quick Start Guide

## What You Have Now

Your repository now includes a complete **Unified Autonomous System** that combines:

1. ✅ **Branch Cleanup Tools** - Manage Copilot branches
2. ✅ **Unified System** - Python-based autonomous dashboard
3. ✅ **Auto-Configuration** - Generates missing APIs/wallets
4. ✅ **AWS Integration** - Ready to deploy
5. ✅ **CI/CD Pipeline** - Automated testing and deployment

## Installation (3 Simple Steps)

### Step 1: Run the Installer

```bash
./install_unified_system.sh
```

This will:
- Install Python dependencies (FastAPI, uvicorn, etc.)
- Update package.json with new scripts
- Create directory structure
- Setup .gitignore
- Takes about 30 seconds

### Step 2: Configure the System (One-Time)

```bash
python3 unified_system.py --setup
```

The setup wizard will ask:

1. **Operating Mode:**
   - `F` - Full Autonomous (everything automatic)
   - `M` - Manual Trading (auto code, manual trading)
   - `I` - Interactive (approve important actions)
   - `R` - Review Only (no automatic changes)

2. **API Keys:** Do you have API keys? (y/n)
   - Answer `n` and the system will generate test credentials

3. **Wallets:** Do you have wallet addresses? (y/n)
   - Answer `n` and the system will generate test addresses

The system will:
- Auto-generate all missing configurations
- Create `.env` file with test credentials
- Save configuration to `.unified-system/config.json`

### Step 3: Start the System

```bash
python3 unified_system.py
```

Or using npm:

```bash
npm run unified
```

## Access Your Dashboard

Open your browser: **http://localhost:8000**

You'll see:
- System status
- Health check endpoint
- Configuration overview

## What Got Auto-Generated?

Check these files (they're automatically created):

```bash
# Complete environment config (test mode)
cat .env

# API credentials (mock for testing)
cat .unified-system/generated/api_credentials.json

# Wallet addresses (test addresses)
cat .unified-system/generated/wallets.json

# Security secrets
cat .unified-system/generated/secrets.json
```

## AWS Deployment

Your system is ready for AWS deployment!

```bash
# Commit your changes
git add .
git commit -m "✅ Unified system configured"
git push
```

AWS deployment is automated through GitHub Actions. See [`DEPLOYMENT.md`](DEPLOYMENT.md) for full instructions.

## Branch Cleanup Tools

### Automated Cleanup

1. Go to **Actions** tab in GitHub
2. Select **Cleanup Copilot Branches**
3. Click **Run workflow**
4. Choose dry-run (to preview) or actual deletion

### Manual Cleanup

```bash
# Preview what would be deleted (dry run)
DRY_RUN=true bash automation/cleanup-branches.sh

# Actually delete stale branches (30+ days old)
DRY_RUN=false bash automation/cleanup-branches.sh

# Delete branches older than 60 days
STALE_DAYS=60 DRY_RUN=false bash automation/cleanup-branches.sh
```

## Available Commands

### NPM Scripts

```bash
npm run start      # Start Node.js server
npm run unified    # Start unified system
npm run unified:setup  # Run setup wizard
npm run dev        # Development mode
```

### Direct Python Commands

```bash
python3 unified_system.py           # Start system
python3 unified_system.py --setup   # Setup wizard
```

## Testing the System

### Health Check

```bash
curl http://localhost:8000/health
```

Should return:

```json
{
  "status": "healthy",
  "timestamp": "2025-...",
  "components": {
    "api": "operational",
    "trading": "disabled",
    "dashboard": "operational"
  }
}
```

### System Status

```bash
curl http://localhost:8000/api/status
```

## Safety Features

### Default Safety Settings

- ✅ Test mode by default (mock credentials)
- ✅ Trading disabled
- ✅ Paper trading only
- ✅ Approval required for important actions
- ✅ Loss limits configured (2% per trade, 5% daily)

### Generated Test Data

All auto-generated data is for **testing only**:
- API keys start with `test_`
- Wallet addresses are random (not real)
- No real money involved
- Safe to experiment with

### Replacing Test Data

When you're ready for production:

1. Edit `.env`:
```bash
nano .env
```

2. Replace test values with real credentials:
```bash
# Change from:
NDAX_API_KEY=ndax_test_abc123...

# To:
NDAX_API_KEY=your_real_api_key_here
```

3. Restart the system:
```bash
python3 unified_system.py
```

## Configuration Files

### `.unified-system/config.json`

Main system configuration - edit to customize behavior:

```json
{
  "auto_fix_code": false,
  "auto_commit": false,
  "trading_enabled": false,
  "dashboard_enabled": true,
  "require_approval": true
}
```

### `.env`

Environment variables (never commit this file!):
- API credentials
- Wallet addresses
- Security secrets
- System settings

## Troubleshooting

### Dashboard won't load

```bash
# Check if server is running
curl http://localhost:8000/health

# If not, start it
python3 unified_system.py
```

### Port already in use

```bash
# Find what's using port 8000
lsof -ti:8000

# Kill it (replace PID with actual process ID)
kill -9 <PID>

# Restart
python3 unified_system.py
```

### Missing dependencies

```bash
# Reinstall Python packages
pip install -r requirements.txt

# Reinstall Node packages
npm install
```

### Need to reset

```bash
# Delete generated configs
rm -rf .unified-system/

# Run setup again
python3 unified_system.py --setup
```

## File Structure

```
The-basics/
├── unified_system.py              # Main Python system
├── install_unified_system.sh      # Installation script
├── server.js                      # Node.js server
├── .github/
│   └── workflows/
│       ├── cleanup-branches.yml   # Branch cleanup workflow
│       └── unified-system.yml     # Unified system CI/CD
├── automation/
│   └── cleanup-branches.sh        # Branch cleanup script
├── docs/
│   ├── COPILOT_BRANCHES_FAQ.md   # Branch FAQ
│   └── BRANCH_CLEANUP.md          # Cleanup documentation
├── .unified-system/              # Generated (don't commit)
│   ├── config.json               # System config
│   ├── generated/                # Auto-generated files
│   └── logs/                     # System logs
└── .env                          # Credentials (don't commit!)
```

## Next Steps

1. ✅ Files installed
2. ✅ System configured
3. ✅ Dashboard accessible
4. ⏭️ Push to GitHub
5. ⏭️ AWS deployment (if configured)
6. ⏭️ Replace test credentials (when ready)
7. ⏭️ Enable features as needed

## Support

- **Logs:** `.unified-system/logs/system.log`
- **Config:** `.unified-system/config.json`
- **Generated Files:** `.unified-system/generated/`
- **Dashboard:** `http://localhost:8000`
- **Health:** `http://localhost:8000/health`

## Security Reminders

⚠️ **Important:**
- Never commit `.env` to git (already in .gitignore)
- Test credentials are for development only
- Use real credentials only in production
- Review auto-generated code before enabling auto-commit
- Keep trading disabled until fully tested

---

**Built with 🚀 by The Unified System**

*Everything you need, one command away.*
