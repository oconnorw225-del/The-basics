#!/bin/bash

# Start script for NDAX Quantum Engine
# Starts all components of the trading system

set -e

echo "🚀 Starting NDAX Quantum Engine..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Running setup..."
    ./setup.sh
fi

# Load environment variables
source .env 2>/dev/null || true

# Array to track background process IDs
PIDS=()

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    wait
}
trap cleanup EXIT INT TERM

# Start Python backend (if available)
if command -v python3 &> /dev/null && [ -f unified_system.py ]; then
    echo "🐍 Starting Python backend..."
    python3 unified_system.py &
    PIDS+=($!)
fi

# Start Node.js server
echo "🌐 Starting Node.js server..."
npm start &
PIDS+=($!)

# Start trading bot (if auto-start is enabled)
if [ "$AUTO_START" = "true" ]; then
    echo "🤖 Starting trading bot..."
    node bot.js &
    PIDS+=($!)
fi

# Start Vite dev server for frontend
echo "⚛️  Starting frontend development server..."
npm run dev

# Wait for all background processes
wait
