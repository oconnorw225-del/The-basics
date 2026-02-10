#!/bin/bash
################################################################################
# Common Shell Utilities
# Shared functions for all shell scripts in the project
################################################################################

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

################################################################################
# Logging Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}▶ $1${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}\n"
}

################################################################################
# Utility Functions
################################################################################

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check Node.js version
check_node() {
    if ! command_exists node; then
        log_error "Node.js is not installed. Please install Node.js 18 or higher."
        return 1
    fi
    log_success "Node.js detected: $(node --version)"
    return 0
}

# Check Python version
check_python() {
    if ! command_exists python3; then
        log_warning "Python3 not found. Some features may not work."
        return 1
    fi
    log_success "Python3 detected: $(python3 --version)"
    return 0
}

# Create necessary directories
create_directories() {
    log_info "Creating directory structure..."
    mkdir -p .unified-system/logs
    mkdir -p .unified-system/generated
    mkdir -p .unified-system/backups
    log_success "Directory structure created"
}
