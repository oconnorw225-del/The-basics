#!/bin/bash

# Setup script for NDAX Quantum Engine
# This script sets up the complete development environment

set -e

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/scripts/common.sh"

log_step "NDAX Quantum Engine Setup"

# Check Node.js and Python
check_node || exit 1
check_python || true

# Install Node dependencies
log_info "Installing Node.js dependencies..."
npm install

# Create necessary directories
create_directories

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    log_info "Creating .env file..."
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
    log_success ".env file created"
else
    log_info ".env file already exists"
fi

log_success "Setup complete!"
log_info "Next steps:"
echo "  1. Run 'npm run dev' to start the frontend development server"
echo "  2. Run 'npm run unified' to start the Python backend (if configured)"
echo "  3. Run 'node bot.js' to start the trading bot"
log_info "For more information, see QUICK_START.md"
