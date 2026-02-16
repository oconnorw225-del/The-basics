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

# Run environment setup script
if [ ! -f .env ]; then
    log_info "Running environment setup..."
    python3 scripts/setup_env.py
else
    log_info ".env file already exists (use --force to regenerate)"
fi

# Run bot configuration setup
log_info "Initializing bot configurations..."
python3 scripts/init_bot_configs.py

# Inject secrets from environment (CI/CD only)
if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ] || [ -n "$RAILWAY_ENVIRONMENT" ]; then
    log_info "CI/CD detected - injecting secrets..."
    python3 scripts/inject_secrets.py
fi

log_success "Setup complete!"
log_info "Next steps:"
echo "  1. Review generated .env file and add your API keys"
echo "  2. Review config/bot-config.json for bot settings"
echo "  3. Copy config/credentials.template.json to config/credentials.json"
echo "  4. Run 'npm run dev' to start the frontend"
echo "  5. Run 'npm run fia' to start the full system"
log_info "For more information, see QUICK_START.md"
