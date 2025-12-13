#!/bin/bash
###############################################################################
# auto-setup.sh - Comprehensive Setup Script for The-basics System
#
# This script automatically detects the environment and sets up all
# required dependencies, databases, and configurations.
#
# Usage:
#   ./scripts/auto-setup.sh [--local|--cloud|--aws]
#
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/.unified-system/logs"
LOG_FILE="$LOG_DIR/setup.log"

# Create log directory
mkdir -p "$LOG_DIR"

###############################################################################
# Utility Functions
###############################################################################

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        log "✓ $1 is installed"
        return 0
    else
        log_warn "✗ $1 is not installed"
        return 1
    fi
}

###############################################################################
# Environment Detection
###############################################################################

detect_environment() {
    log_info "Detecting environment..."
    
    # Check for AWS
    if [ -n "$AWS_EXECUTION_ENV" ] || [ -f /etc/ecs/ecs.config ]; then
        echo "aws"
        return
    fi
    
    # Check for Railway
    if [ -n "$RAILWAY_ENVIRONMENT" ]; then
        echo "railway"
        return
    fi
    
    # Check for Heroku
    if [ -n "$DYNO" ]; then
        echo "heroku"
        return
    fi
    
    # Check for Docker
    if [ -f /.dockerenv ]; then
        echo "docker"
        return
    fi
    
    # Default to local
    echo "local"
}

###############################################################################
# System Requirements Installation
###############################################################################

install_system_packages() {
    log "Installing system packages..."
    
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        log_info "Detected Debian/Ubuntu system"
        sudo apt-get update
        sudo apt-get install -y \
            curl \
            wget \
            git \
            build-essential \
            python3 \
            python3-pip \
            python3-venv \
            nodejs \
            npm \
            sqlite3 \
            redis-server \
            || log_warn "Some system packages may have failed to install"
    elif [ -f /etc/redhat-release ]; then
        # RedHat/CentOS
        log_info "Detected RedHat/CentOS system"
        sudo yum update -y
        sudo yum install -y \
            curl \
            wget \
            git \
            gcc \
            gcc-c++ \
            make \
            python3 \
            python3-pip \
            nodejs \
            npm \
            sqlite \
            redis \
            || log_warn "Some system packages may have failed to install"
    elif [ "$(uname)" == "Darwin" ]; then
        # macOS
        log_info "Detected macOS system"
        if ! check_command brew; then
            log_warn "Homebrew not found. Installing..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install node python3 redis sqlite3 || log_warn "Some packages may have failed to install"
    else
        log_warn "Unknown OS. Please install dependencies manually."
    fi
}

install_node_dependencies() {
    log "Installing Node.js dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Update npm if needed
    if check_command npm; then
        npm install -g npm@latest || log_warn "Failed to update npm"
    fi
    
    # Install project dependencies
    if [ -f package.json ]; then
        npm install || log_error "Failed to install Node.js dependencies"
        log "✓ Node.js dependencies installed"
    else
        log_warn "No package.json found"
    fi
}

install_python_dependencies() {
    log "Installing Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv || log_error "Failed to create virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate || log_warn "Failed to activate virtual environment"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel || log_warn "Failed to upgrade pip"
    
    # Install requirements
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt || log_warn "Some Python packages may have failed to install"
        log "✓ Python dependencies installed"
    fi
    
    if [ -f requirements_chimera.txt ]; then
        pip install -r requirements_chimera.txt || log_warn "Some chimera packages may have failed to install"
    fi
}

###############################################################################
# Database Setup
###############################################################################

setup_databases() {
    log "Setting up databases..."
    
    # Create database directories
    mkdir -p "$PROJECT_ROOT/.unified-system/db"
    mkdir -p "$PROJECT_ROOT/.unified-system/checkpoints"
    
    # Initialize SQLite databases
    log_info "Initializing SQLite databases..."
    sqlite3 "$PROJECT_ROOT/.unified-system/db/system.db" "CREATE TABLE IF NOT EXISTS version (id INTEGER PRIMARY KEY, version TEXT);" || log_warn "SQLite initialization may have failed"
    
    # Start Redis if local
    if [ "$ENVIRONMENT" == "local" ]; then
        if check_command redis-server; then
            log_info "Starting Redis server..."
            redis-server --daemonize yes || log_warn "Failed to start Redis"
        fi
    fi
    
    log "✓ Databases initialized"
}

###############################################################################
# Credential Setup
###############################################################################

setup_credentials() {
    log "Setting up credentials..."
    
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_info "Creating .env file from template..."
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env" || log_error "Failed to create .env file"
        
        log_warn "Please edit .env file with your actual credentials"
        log_warn "Required: NDAX_API_KEY, NDAX_API_SECRET for trading"
        log_warn "Optional: AI platform keys, freelance platform keys"
    else
        log "✓ .env file already exists"
    fi
    
    # Generate encryption key if not present
    if ! grep -q "ENCRYPTION_KEY=" "$PROJECT_ROOT/.env" || grep -q "ENCRYPTION_KEY=$" "$PROJECT_ROOT/.env"; then
        log_info "Generating encryption key..."
        ENCRYPTION_KEY=$(openssl rand -hex 32)
        echo "ENCRYPTION_KEY=$ENCRYPTION_KEY" >> "$PROJECT_ROOT/.env"
        log "✓ Encryption key generated"
    fi
    
    # Generate JWT secret if not present
    if ! grep -q "JWT_SECRET=" "$PROJECT_ROOT/.env" || grep -q "JWT_SECRET=$" "$PROJECT_ROOT/.env"; then
        log_info "Generating JWT secret..."
        JWT_SECRET=$(openssl rand -hex 32)
        echo "JWT_SECRET=$JWT_SECRET" >> "$PROJECT_ROOT/.env"
        log "✓ JWT secret generated"
    fi
}

###############################################################################
# Service Setup
###############################################################################

setup_services() {
    log "Setting up services..."
    
    # Create systemd service file for auto-start on boot (Linux only)
    if [ -d /etc/systemd/system ] && [ "$ENVIRONMENT" == "local" ]; then
        log_info "Creating systemd service..."
        
        sudo tee /etc/systemd/system/the-basics.service > /dev/null <<EOF
[Unit]
Description=The-basics Autonomous Trading and AI System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_ROOT
ExecStart=$PROJECT_ROOT/scripts/auto-start.sh
Restart=on-failure
RestartSec=10
StandardOutput=append:$LOG_DIR/service.log
StandardError=append:$LOG_DIR/service-error.log

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        log "✓ Systemd service created"
        log_info "Enable with: sudo systemctl enable the-basics"
        log_info "Start with: sudo systemctl start the-basics"
    fi
}

###############################################################################
# Health Checks
###############################################################################

run_health_checks() {
    log "Running health checks..."
    
    local failed=0
    
    # Check Node.js
    if check_command node; then
        log_info "Node.js version: $(node --version)"
    else
        log_error "Node.js is not installed"
        failed=1
    fi
    
    # Check Python
    if check_command python3; then
        log_info "Python version: $(python3 --version)"
    else
        log_error "Python is not installed"
        failed=1
    fi
    
    # Check npm
    if check_command npm; then
        log_info "npm version: $(npm --version)"
    else
        log_error "npm is not installed"
        failed=1
    fi
    
    # Check pip
    if check_command pip || check_command pip3; then
        log_info "pip is installed"
    else
        log_warn "pip is not installed"
    fi
    
    # Check required directories
    for dir in "$LOG_DIR" "$PROJECT_ROOT/.unified-system/db" "$PROJECT_ROOT/config"; do
        if [ -d "$dir" ]; then
            log "✓ Directory exists: $dir"
        else
            log_error "Missing directory: $dir"
            failed=1
        fi
    done
    
    # Check required files
    for file in "$PROJECT_ROOT/.env" "$PROJECT_ROOT/package.json" "$PROJECT_ROOT/config/features.yaml"; do
        if [ -f "$file" ]; then
            log "✓ File exists: $(basename $file)"
        else
            log_warn "Missing file: $(basename $file)"
        fi
    done
    
    if [ $failed -eq 0 ]; then
        log "✓ All health checks passed"
        return 0
    else
        log_error "Some health checks failed"
        return 1
    fi
}

###############################################################################
# Build and Test
###############################################################################

build_project() {
    log "Building project..."
    
    cd "$PROJECT_ROOT"
    
    # Build frontend
    if [ -f package.json ] && grep -q "\"build\"" package.json; then
        log_info "Building frontend..."
        npm run build || log_warn "Frontend build failed"
    fi
    
    log "✓ Build complete"
}

###############################################################################
# Main Setup Flow
###############################################################################

main() {
    log "========================================="
    log "The-basics System Auto-Setup"
    log "========================================="
    
    # Detect environment
    ENVIRONMENT=$(detect_environment)
    log_info "Environment: $ENVIRONMENT"
    
    # Parse arguments
    if [ "$1" == "--local" ]; then
        ENVIRONMENT="local"
    elif [ "$1" == "--cloud" ]; then
        ENVIRONMENT="cloud"
    elif [ "$1" == "--aws" ]; then
        ENVIRONMENT="aws"
    fi
    
    # Run setup steps
    log "Starting setup process..."
    
    if [ "$ENVIRONMENT" == "local" ]; then
        install_system_packages || log_warn "System package installation had issues"
    fi
    
    install_node_dependencies || log_error "Failed to install Node.js dependencies"
    install_python_dependencies || log_warn "Python dependency installation had issues"
    setup_databases || log_warn "Database setup had issues"
    setup_credentials || log_warn "Credential setup had issues"
    
    if [ "$ENVIRONMENT" == "local" ]; then
        setup_services || log_warn "Service setup had issues"
    fi
    
    run_health_checks || log_warn "Some health checks failed"
    
    if [ "$ENVIRONMENT" == "local" ]; then
        build_project || log_warn "Build had issues"
    fi
    
    log "========================================="
    log "Setup Complete!"
    log "========================================="
    log_info "Next steps:"
    log_info "1. Edit .env file with your credentials"
    log_info "2. Run: ./scripts/health-check.sh to verify setup"
    log_info "3. Run: ./scripts/auto-start.sh to start the system"
    log_info ""
    log_info "For auto-start on boot (Linux):"
    log_info "  sudo systemctl enable the-basics"
    log_info "  sudo systemctl start the-basics"
}

# Run main function
main "$@"
