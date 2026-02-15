# 🚀 How to Access Everything - Quick Start Guide

**Your Questions Answered:**
1. ✅ "Where do I access it?"
2. ✅ "Are all operations ongoing or prompted?"

---

## 🎯 Quick Answer

### Start the System
```bash
npm run fia
```

### Access Everything Here
- **Dashboard**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

---

## 📍 Where to Access Each Feature

### 1. Dashboard (Main Interface)
**URL**: http://localhost:5173

Open your browser and go to this address. You'll see:
- 💰 Live prices (250+ coins)
- 📊 Market metrics
- 👛 Wallet manager
- 📈 Asset portfolio
- 🔄 Live wallet feed
- 📁 File upload
- 🔑 API key manager
- 🤖 Bot status
- 💾 Backup manager

### 2. API Endpoints
**URL**: http://localhost:8000

**Interactive Docs**: http://localhost:8000/docs (Try API calls here!)

#### Key Endpoints:
```bash
# Market Data
GET  http://localhost:8000/api/market/prices
GET  http://localhost:8000/api/market/trending

# Portfolio
GET  http://localhost:8000/api/portfolio/assets
GET  http://localhost:8000/api/portfolio/summary

# Operations
POST http://localhost:8000/api/assets/transfer
POST http://localhost:8000/api/assets/swap
POST http://localhost:8000/api/assets/stake

# Backup
POST http://localhost:8000/api/backup/create
GET  http://localhost:8000/api/backup/list

# Automation
GET  http://localhost:8000/api/automation/settings
POST http://localhost:8000/api/automation/toggle
```

### 3. WebSocket (Real-time Updates)
**URL**: ws://localhost:8000/ws

Connect to receive instant updates:
- Price changes
- New transactions
- Balance updates
- Bot status changes

---

## ⚡ What Runs Automatically vs What You Control

### 🟢 AUTOMATIC (Always Running)

These run **continuously** without your input:

1. **Live Market Data** - Updates every 30 seconds
2. **Wallet Monitoring** - Real-time transaction detection
3. **Portfolio Tracking** - Balance updates every 30 seconds
4. **Bot Trading** - Bots trade automatically (if enabled)
5. **Health Checks** - System monitoring every 60 seconds
6. **Price Tracking** - Real-time via WebSocket
7. **Transaction Detection** - Instant alerts
8. **Backups** - Daily at 2 AM automatically

**You get instant updates without doing anything!**

### 🔵 MANUAL (You Control)

These require **your action**:

1. **Import Wallet** - You add wallets
2. **Transfer Assets** - You send funds
3. **Buy/Sell** - You decide trades
4. **Swap Tokens** - You initiate swaps
5. **Stake/Unstake** - You manage staking
6. **Upload Files** - You upload wallet files
7. **Add API Keys** - You add keys
8. **Manual Backup** - You trigger extra backups
9. **Start/Stop Bots** - You control bots
10. **Scan Address** - You request scans

**You have full control when you want it!**

### 🟡 CONFIGURABLE (Your Choice)

These can be **automatic OR manual**:

1. **Portfolio Rebalancing** - Auto or manual
2. **Yield Harvesting** - Auto or manual
3. **Gas Optimization** - Auto or manual
4. **Notifications** - Push or check manually
5. **Trade Approval** - Auto or require approval
6. **Backup Schedule** - Daily/weekly/manual

**Configure in**: `config/automation-settings.json`

---

## 🛠️ How to Use

### Starting the System
```bash
# Navigate to project directory
cd /path/to/The-basics

# Start everything with one command
npm run fia

# You'll see:
# ✅ Backend API: http://localhost:3000
# ✅ Dashboard Backend: http://localhost:8000  
# ✅ Dashboard Frontend: http://localhost:5173
# ✅ Bot Coordinator: Running
# ✅ Trading Bots: Active
```

### Opening the Dashboard
```bash
# Open in browser
http://localhost:5173

# Or from command line (Linux/Mac)
open http://localhost:5173

# Or (Windows)
start http://localhost:5173
```

### Viewing Your Portfolio
```bash
# Via API
curl http://localhost:8000/api/portfolio/assets

# Or open dashboard and navigate to Portfolio tab
```

### Importing a Wallet
```bash
# Via API
curl -X POST http://localhost:8000/api/assets/wallet/import \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_data": "your seed phrase or private key",
    "label": "My Wallet",
    "password": "master_password"
  }'

# Or use Dashboard → Wallet Manager → Import Wallet
```

### Transferring Assets
```bash
# Via API
curl -X POST http://localhost:8000/api/assets/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "eth_mainnet_native",
    "to_address": "0x123...",
    "amount": "0.5"
  }'

# Or use Dashboard → Portfolio → Select Asset → Transfer
```

### Creating a Backup
```bash
# Via API
curl -X POST http://localhost:8000/api/backup/create \
  -H "Content-Type: application/json" \
  -d '{"password": "your_master_password"}'

# Or use Dashboard → Backup Manager → Create Backup
```

### Checking Bot Status
```bash
# Via API
curl http://localhost:8000/api/bots/status

# Or use Dashboard → Bot Status
```

---

## 🎛️ Controlling Automation

### View Current Settings
```bash
curl http://localhost:8000/api/automation/settings
```

### Change Refresh Interval
```bash
curl -X POST http://localhost:8000/api/automation/settings \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": {
      "refresh_interval": 60
    }
  }'
```

### Enable Auto-Harvesting
```bash
curl -X POST http://localhost:8000/api/automation/toggle \
  -H "Content-Type: application/json" \
  -d '{
    "feature": "auto_harvest",
    "enabled": true
  }'
```

### Edit Config File Directly
```bash
# Open config file
nano config/automation-settings.json

# Change settings
# Save and restart: npm run fia
```

---

## 📊 What You See Where

### Dashboard Main Page
- Live price tickers scrolling
- Market metrics (total cap, volume)
- Fear & Greed Index
- Top trending coins

### Portfolio Page
- All your assets listed
- Location (chain, wallet, contract)
- Balance (native + USD)
- 24h change
- Transfer/Swap/Stake buttons

### Live Feed Page
- Real-time transaction stream
- Balance updates
- Token discoveries
- NFT activity

### Wallet Manager Page
- Import wallet interface
- List of all wallets
- Monitor wallet button
- Delete wallet option

### Asset Scanner Page
- Address input
- Chain selection
- Scan button
- Results display (transactions, tokens, NFTs)

### Backup Manager Page
- Create backup button
- List of backups
- Restore backup button
- Backup verification

### Bot Status Page
- Bot cards (NDAX, Quantum, ShadowForge)
- Status indicators
- Performance metrics
- Start/Stop controls

---

## 🔑 Important URLs

### Main Services
- Dashboard Frontend: http://localhost:5173
- Dashboard Backend: http://localhost:8000
- Backend API: http://localhost:3000
- Bot API: http://localhost:9000

### Documentation
- API Interactive Docs: http://localhost:8000/docs
- API ReDoc: http://localhost:8000/redoc
- WebSocket: ws://localhost:8000/ws

### Health Checks
- Backend: http://localhost:3000/health
- Dashboard: http://localhost:8000/health
- Bots: http://localhost:9000/status

---

## 🆘 Troubleshooting

### Dashboard Not Loading?
```bash
# Check if services are running
npm run fia

# Check port 5173 is free
lsof -i :5173

# Restart if needed
pkill -f vite
npm run fia
```

### API Not Responding?
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check logs
tail -f .unified-system/logs/*.log

# Restart
npm run fia
```

### No Live Updates?
```bash
# Check WebSocket connection in browser console
# Should see: WebSocket connection established

# Check automation settings
curl http://localhost:8000/api/automation/settings

# Ensure auto_refresh is true
```

---

## 📚 Additional Documentation

- **Complete Access Guide**: `ACCESS_GUIDE.md`
- **Operations Control**: `OPERATIONS_CONTROL.md`
- **Automation Controller**: `backend/automation_controller.py`
- **Config File**: `config/automation-settings.json`
- **FIA Orchestrator**: `FIA_ORCHESTRATOR.md`
- **Dashboard Implementation**: `DASHBOARD_IMPLEMENTATION_COMPLETE.md`

---

## 🎉 Summary

**To Access Everything:**
1. Run: `npm run fia`
2. Open: http://localhost:5173
3. Enjoy: All features in one dashboard!

**What's Automatic:**
- ✅ Live data updates (every 30s)
- ✅ Wallet monitoring (real-time)
- ✅ Bot trading (continuous)
- ✅ Backups (daily)

**What You Control:**
- ✅ Transfers, trades, swaps
- ✅ Wallet imports
- ✅ Bot start/stop
- ✅ Manual operations

**Configuration:**
- ✅ File: `config/automation-settings.json`
- ✅ API: `http://localhost:8000/api/automation/*`
- ✅ Dashboard: Toggle switches in UI

**Everything is accessible, documented, and under your control!** 🚀
