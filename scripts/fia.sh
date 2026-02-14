#!/bin/bash

#
# FIA - Full Integration Activation
# Shell wrapper for easy execution
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║   FIA - FULL INTEGRATION ACTIVATION        ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$ROOT_DIR"

# Check if bun is available
if command -v bun &> /dev/null; then
    echo -e "${GREEN}Using Bun.js for maximum performance...${NC}"
    bun run scripts/fia.js "$@"
elif command -v node &> /dev/null; then
    echo -e "${YELLOW}Bun not found, using Node.js...${NC}"
    node scripts/fia.js "$@"
else
    echo -e "${RED}Error: Neither bun nor node found in PATH${NC}"
    exit 1
fi
