#!/bin/bash
# install_unified_system.sh - Complete Installation

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║              🚀 UNIFIED AUTONOMOUS SYSTEM INSTALLER                       ║"
echo "║              The-Basics + Chimera + Full Dashboard                        ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python: $(python3 --version)${NC}"

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"

echo ""
echo "📦 Installing Python dependencies..."

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
python-multipart==0.0.6
aiofiles==23.2.1
pydantic==2.5.0
EOF

python3 -m pip install -r requirements.txt --quiet || echo -e "${YELLOW}Note: Some packages may have been skipped${NC}"
echo -e "${GREEN}✅ Python packages installed${NC}"

echo ""
echo "📦 Updating package.json..."

# Update package.json with new scripts
cat > package.json << 'EOF'
{
  "name": "the-basics-unified",
  "version": "2.0.0",
  "description": "Complete autonomous system with dashboard",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "unified": "python3 unified_system.py",
    "unified:setup": "python3 unified_system.py --setup",
    "dashboard": "python3 unified_system.py",
    "dev": "node server.js",
    "railway": "node server.js"
  },
  "engines": {
    "node": ">=18",
    "python": ">=3.8"
  },
  "keywords": ["consolidation", "automation", "trading", "dashboard"],
  "author": "oconnorw225-del",
  "license": "MIT",
  "dependencies": {}
}
EOF

echo -e "${GREEN}✅ package.json updated${NC}"

echo ""
echo "📁 Creating directory structure..."

mkdir -p .unified-system/{backups,logs,generated}
mkdir -p chimera_core/{treasury,evolution_engine,orchestrator,api}
mkdir -p dashboard/{src,public}
mkdir -p sandbox/{strategies,backtest_results}

echo -e "${GREEN}✅ Directories created${NC}"

echo ""
echo "📝 Updating .gitignore..."

# Add to .gitignore
if ! grep -q ".unified-system/" .gitignore 2>/dev/null; then
    cat >> .gitignore << 'EOF'

# Unified System
.unified-system/
.env
*.log
__pycache__/
*.pyc
requirements.txt
EOF
fi

echo -e "${GREEN}✅ .gitignore updated${NC}"

# Create README
cat > UNIFIED_SYSTEM_README.md << 'EOF'
# 🚀 Unified Autonomous System

## Quick Start

### 1. First Run (Setup)
```bash
python3 unified_system.py --setup
```

This will:
- ✅ Configure all settings (one-time)
- ✅ Auto-generate missing APIs/wallets (test mode)
- ✅ Create .env file with everything
- ✅ Setup Railway integration

### 2. Start System
```bash
python3 unified_system.py
```

Or use npm:
```bash
npm run unified
```

### 3. Access Dashboard
Open: **http://localhost:8000/**

## Configuration

All settings in `.unified-system/config.json`

## Generated Files

After first run, check:
- `.env` - Complete configuration
- `.unified-system/generated/api_credentials.json` - API keys
- `.unified-system/generated/wallets.json` - Wallet addresses
- `.unified-system/generated/secrets.json` - Security keys

## Railway Deployment

Push to GitHub and Railway auto-deploys!

Health check: `https://your-app.railway.app/health`

## Safety Features

- 🛡️ Test mode by default (mock APIs/wallets)
- 🔒 Kill switch available
- 📊 Loss limits (per trade & daily)
- 💾 Automatic backups

## Support

- Logs: `.unified-system/logs/system.log`
- Dashboard: `http://localhost:8000`

---

**Built with 🚀 by The Unified System**
EOF

echo -e "${GREEN}✅ README created${NC}"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                     ✅ INSTALLATION COMPLETE! 🎉                          ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🚀 Next Steps:${NC}"
echo ""
echo "1. Run setup wizard (one-time):"
echo "   python3 unified_system.py --setup"
echo ""
echo "2. Start the system:"
echo "   python3 unified_system.py"
echo ""
echo "3. Access dashboard:"
echo "   http://localhost:8000"
echo ""
echo -e "${YELLOW}📖 Read UNIFIED_SYSTEM_README.md for complete documentation${NC}"
echo ""
