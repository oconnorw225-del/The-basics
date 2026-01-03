#!/bin/bash

################################################################################
# SETUP SCRIPT - The Basics Repository
# Checks dependencies and initializes the repository structure
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

################################################################################
# Helper Functions
################################################################################

print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║            THE-BASICS REPOSITORY SETUP                         ║"
    echo "║          Dependency Check & Initialization                     ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

command_exists() {
    command -v "$1" &> /dev/null
}

check_version() {
    local cmd="$1"
    local version_cmd="$2"
    local min_version="$3"
    
    if command_exists "$cmd"; then
        local version=$($version_cmd 2>&1 | head -n1)
        log_success "$cmd is installed: $version"
        return 0
    else
        log_error "$cmd is NOT installed (required: $min_version+)"
        return 1
    fi
}

################################################################################
# Dependency Checks
################################################################################

check_dependencies() {
    log_info "Checking required dependencies..."
    echo ""
    
    local all_ok=true
    
    # Git
    if check_version "git" "git --version" "2.0"; then
        true
    else
        log_warning "Install git: https://git-scm.com/downloads"
        all_ok=false
    fi
    
    # Node.js
    if check_version "node" "node --version" "16"; then
        true
    else
        log_warning "Install Node.js: https://nodejs.org/ (v16 or higher)"
        all_ok=false
    fi
    
    # npm
    if check_version "npm" "npm --version" "8"; then
        true
    else
        log_warning "npm should come with Node.js"
        all_ok=false
    fi
    
    # Python
    if check_version "python3" "python3 --version" "3.10"; then
        true
    else
        log_warning "Install Python: https://www.python.org/ (v3.10 or higher)"
        all_ok=false
    fi
    
    # pip
    if check_version "pip3" "pip3 --version" "20"; then
        true
    else
        log_warning "Install pip: python3 -m ensurepip --upgrade"
        all_ok=false
    fi
    
    echo ""
    
    # Optional dependencies
    log_info "Checking optional dependencies..."
    
    if command_exists "rsync"; then
        log_success "rsync is installed (recommended for consolidation)"
    else
        log_warning "rsync not found (optional, but recommended)"
        log_info "  Ubuntu/Debian: sudo apt-get install rsync"
        log_info "  macOS: brew install rsync"
    fi
    
    if command_exists "docker"; then
        log_success "docker is installed (optional)"
    else
        log_warning "docker not found (optional for containerized deployment)"
    fi
    
    echo ""
    
    if [ "$all_ok" = false ]; then
        log_error "Some required dependencies are missing. Please install them and run this script again."
        exit 1
    else
        log_success "All required dependencies are installed!"
    fi
}

################################################################################
# Directory Structure Initialization
################################################################################

init_directory_structure() {
    log_info "Initializing directory structure..."
    
    # Essential directories
    local dirs=(
        "api"
        "backend"
        "frontend"
        "docs"
        "tests"
        "config"
        "scripts"
        "automation"
        "backups"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_success "Created directory: $dir/"
        else
            log_info "Directory exists: $dir/"
        fi
    done
    
    # Create .gitkeep for empty directories
    if [ ! -f "backups/.gitkeep" ]; then
        echo "# Backups directory" > backups/.gitkeep
        log_success "Created backups/.gitkeep"
    fi
    
    log_success "Directory structure initialized"
}

################################################################################
# Install Dependencies
################################################################################

install_dependencies() {
    log_info "Installing project dependencies..."
    echo ""
    
    # Python dependencies
    if [ -f "requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        if pip3 install -r requirements.txt; then
            log_success "Python dependencies installed"
        else
            log_warning "Some Python dependencies failed to install"
        fi
    fi
    
    if [ -f "requirements_chimera.txt" ]; then
        log_info "Installing Chimera Python dependencies..."
        if pip3 install -r requirements_chimera.txt; then
            log_success "Chimera Python dependencies installed"
        else
            log_warning "Some Chimera dependencies failed to install"
        fi
    fi
    
    echo ""
    
    # Node.js dependencies
    if [ -f "package.json" ]; then
        log_info "Installing Node.js dependencies..."
        if npm install; then
            log_success "Node.js dependencies installed"
        else
            log_warning "Some Node.js dependencies failed to install"
        fi
    fi
    
    echo ""
    log_success "Dependency installation completed"
}

################################################################################
# Configuration Setup
################################################################################

setup_configuration() {
    log_info "Setting up configuration files..."
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log_warning ".env file not found"
            read -p "Would you like to create .env from .env.example? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cp .env.example .env
                log_success "Created .env from .env.example"
                log_warning "Please edit .env and fill in your actual credentials"
            fi
        else
            log_warning ".env.example not found. Cannot create .env automatically."
        fi
    else
        log_success ".env file exists"
    fi
    
    # Check consolidation config
    if [ -f "config/consolidation-config.json" ]; then
        log_success "Consolidation config found: config/consolidation-config.json"
    else
        log_warning "Consolidation config not found. This is needed for repository consolidation."
    fi
}

################################################################################
# Git Hooks Setup (Optional)
################################################################################

setup_git_hooks() {
    log_info "Setting up git hooks..."
    
    # Pre-commit hook to prevent committing .env files
    local pre_commit_hook=".git/hooks/pre-commit"
    
    if [ ! -f "$pre_commit_hook" ]; then
        cat > "$pre_commit_hook" << 'EOF'
#!/bin/bash
# Pre-commit hook to prevent committing sensitive files

# Check for forbidden file patterns
for file in $(git diff --cached --name-only); do
    case "$file" in
        .env|.env.local|.env.production|*.key|*.pem|*_secret_*|*api_key*)
            echo "Error: Attempting to commit sensitive file: $file"
            echo "Please remove this file from the commit."
            exit 1
            ;;
    esac
done

exit 0
EOF
        chmod +x "$pre_commit_hook"
        log_success "Git pre-commit hook installed"
    else
        log_info "Git pre-commit hook already exists"
    fi
}

################################################################################
# System Information
################################################################################

print_system_info() {
    echo ""
    log_info "System Information:"
    echo ""
    echo "  OS: $(uname -s)"
    echo "  Architecture: $(uname -m)"
    echo "  Working Directory: $(pwd)"
    echo ""
}

################################################################################
# Completion Summary
################################################################################

print_summary() {
    echo ""
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    SETUP COMPLETED                             ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    log_info "Next steps:"
    echo ""
    echo "  1. Configure your .env file with actual credentials"
    echo "  2. Review config/consolidation-config.json"
    echo "  3. Run consolidation: bash automation/consolidate.sh"
    echo "  4. Or trigger via GitHub Actions workflow"
    echo ""
    log_info "Useful commands:"
    echo ""
    echo "  npm run dev              - Start development server"
    echo "  python3 demo_chimera.py  - Test Chimera system"
    echo "  bash automation/consolidate.sh - Run consolidation"
    echo "  python3 automation/audit.py    - Run security audit"
    echo "  bash scripts/verify.sh   - Verify repository structure"
    echo ""
    log_success "Setup complete! You're ready to go."
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    print_banner
    print_system_info
    
    check_dependencies
    echo ""
    
    init_directory_structure
    echo ""
    
    read -p "Install project dependencies? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dependencies
        echo ""
    fi
    
    setup_configuration
    echo ""
    
    read -p "Set up git hooks to prevent committing secrets? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_git_hooks
        echo ""
    fi
    
    print_summary
}

# Run main function
main "$@"
