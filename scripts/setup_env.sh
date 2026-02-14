#!/bin/bash
################################################################################
# Environment Auto-Setup Script
# 
# Automatically generates secure environment configurations with:
# - JWT and session secrets
# - Database connection strings
# - Security settings
# - API key placeholders
#
# Usage:
#   ./scripts/setup_env.sh           # Interactive mode
#   ./scripts/setup_env.sh --auto    # Automatic mode (both dev & prod)
#   ./scripts/setup_env.sh --dev     # Development only
#   ./scripts/setup_env.sh --prod    # Production only
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🔐 ENVIRONMENT AUTO-POPULATOR                           ║
║                                                                      ║
║  Automatically generates secure configurations with:                ║
║    ✅ JWT & Session Secrets (cryptographically secure)              ║
║    ✅ Database Connection Strings                                   ║
║    ✅ Security Settings (HTTPS, Auth, Rate Limiting)                ║
║    ✅ API Key Detection & Placeholders                              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

# Run the Python setup script
cd "$REPO_ROOT"
python3 "$SCRIPT_DIR/setup_env.py" "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Environment setup completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Security Reminders:${NC}"
    echo "  • Never commit .env or .env.production to git"
    echo "  • Keep your JWT secrets secure"
    echo "  • Fill in actual API keys before deployment"
    echo "  • Review all settings for your specific needs"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Environment setup failed or was cancelled.${NC}"
    echo ""
fi

exit $exit_code
