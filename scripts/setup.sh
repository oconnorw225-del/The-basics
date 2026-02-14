#!/bin/bash

echo "🚀 Setting up The-Basics Bot System"
echo "===================================="
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js $(node --version)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.11+"
    exit 1
fi
echo "✅ Python $(python3 --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm 9+"
    exit 1
fi
echo "✅ npm $(npm --version)"

# Install Node.js dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
npm install
if [ $? -eq 0 ]; then
    echo "✅ Node.js dependencies installed"
else
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi

# Create Python virtual environment
echo ""
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment and install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

pip install --upgrade pip --quiet
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your actual API keys"
    echo "   File location: $(pwd)/.env"
else
    echo ""
    echo "ℹ️  .env file already exists, skipping creation"
fi

# Verify installations
echo ""
echo "🔍 Verifying installations..."

# Test Node.js
node -e "console.log('  ✅ Node.js works')" 2>/dev/null || echo "  ❌ Node.js test failed"

# Test Python imports
python3 -c "import aiohttp; import fastapi; print('  ✅ Python packages work')" 2>/dev/null || echo "  ⚠️  Some Python packages may need attention"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Activate Python venv: source venv/bin/activate"
echo "  3. Start the system:"
echo "     - Node.js: npm start"
echo "     - Python: python backend/bot-coordinator.py"
echo ""
echo "📚 For more info, see README.md"
