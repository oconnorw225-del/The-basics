#!/bin/bash

# Setup script for NDAX Quantum Engine
# This script sets up the complete development environment

set -e

echo "🚀 NDAX Quantum Engine Setup"
echo "=============================="

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✅ Node.js detected: $(node --version)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python3 not found. Some features may not work."
else
    echo "✅ Python3 detected: $(python3 --version)"
fi

# Install Node dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
npm install

# Create necessary directories
echo ""
echo "📁 Creating directory structure..."
mkdir -p .unified-system/logs
mkdir -p .unified-system/generated
mkdir -p .unified-system/backups

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# NDAX Quantum Engine Configuration
NODE_ENV=development
PORT=3000
BOT_PORT=9000

# Trading Mode (paper or live)
TRADING_MODE=paper
AUTO_START=false
MAX_TRADES=5
RISK_LEVEL=low

# API Configuration
VITE_API_URL=http://localhost:8000

# Optional: Add your API keys here
# NDAX_API_KEY=
# NDAX_API_SECRET=
EOF
    echo "✅ .env file created"
else
    echo "ℹ️  .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run 'npm run dev' to start the frontend development server"
echo "2. Run 'npm run unified' to start the Python backend (if configured)"
echo "3. Run 'node bot.js' to start the trading bot"
echo ""
echo "For more information, see QUICK_START.md"
