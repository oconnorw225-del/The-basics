#!/bin/bash

# Start script for NDAX Quantum Engine
# Starts all components of the trading system

set -e

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/scripts/common.sh"

log_step "Starting NDAX Quantum Engine"

# Check if .env exists
if [ ! -f .env ]; then
    log_warning ".env file not found. Running setup..."
    ./setup.sh
fi

# Load environment variables
source .env 2>/dev/null || true

# Array to track background process IDs
PIDS=()

# Function to cleanup background processes
cleanup() {
    log_info "Shutting down..."
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    wait
}
trap cleanup EXIT INT TERM

# Start Python backend (if available)
if command_exists python3 && [ -f unified_system.py ]; then
    log_info "Starting Python backend..."
    python3 unified_system.py &
    PIDS+=($!)
fi

# Start Node.js server
log_info "Starting Node.js server..."
npm start &
PIDS+=($!)

# Start trading bot (if auto-start is enabled)
if [ "$AUTO_START" = "true" ]; then
    log_info "Starting trading bot..."
    node bot.js &
    PIDS+=($!)
fi

# Start Vite dev server for frontend
log_info "Starting frontend development server..."
npm run dev

# Wait for all background processes
wait
