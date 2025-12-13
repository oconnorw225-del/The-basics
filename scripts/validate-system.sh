#!/bin/bash
###############################################################################
# validate-system.sh - System Validation Script for The-basics
#
# This script validates all file paths, imports, API endpoints, credentials,
# and wallet addresses to ensure system integrity.
#
# Usage:
#   ./scripts/validate-system.sh [--fix] [--verbose]
#
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Flags
FIX_ISSUES=false
VERBOSE=false

# Validation results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

###############################################################################
# Utility Functions
###############################################################################

log_pass() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    echo -e "${GREEN}[✓]${NC} $1"
}

log_fail() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    echo -e "${RED}[✗]${NC} $1"
}

log_warn() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    WARNINGS=$((WARNINGS + 1))
    echo -e "${YELLOW}[!]${NC} $1"
}

log_info() {
    if $VERBOSE; then
        echo -e "${BLUE}[i]${NC} $1"
    fi
}

###############################################################################
# File Path Validation
###############################################################################

validate_file_paths() {
    echo ""
    echo "========================================="
    echo "File Path Validation"
    echo "========================================="
    
    # Critical files
    local files=(
        "package.json"
        "server.js"
        "unified_system.py"
        ".env.example"
        "config/features.yaml"
        "src/core/error-handler.js"
        "src/core/recovery-system.py"
        "src/core/freeze-detector.js"
        "src/core/feature-manager.js"
        "src/security/credential-manager.js"
        "scripts/auto-setup.sh"
        "scripts/auto-start.sh"
        "scripts/health-check.sh"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$PROJECT_ROOT/$file" ]; then
            log_pass "File exists: $file"
        else
            log_fail "Missing file: $file"
        fi
    done
    
    # Critical directories
    local dirs=(
        "src"
        "src/core"
        "src/security"
        "scripts"
        "config"
        "aws"
        "aws/terraform"
    )
    
    for dir in "${dirs[@]}"; do
        if [ -d "$PROJECT_ROOT/$dir" ]; then
            log_pass "Directory exists: $dir"
        else
            log_fail "Missing directory: $dir"
        fi
    done
}

###############################################################################
# Import Validation
###############################################################################

validate_imports() {
    echo ""
    echo "========================================="
    echo "Import Validation"
    echo "========================================="
    
    # Check JavaScript imports
    log_info "Checking JavaScript imports..."
    
    if command -v node &> /dev/null; then
        # Test error-handler.js
        if node -e "require('$PROJECT_ROOT/src/core/error-handler.js')" 2>/dev/null; then
            log_pass "error-handler.js imports are valid"
        else
            log_warn "error-handler.js has import issues (may need dependencies)"
        fi
        
        # Test freeze-detector.js
        if node -e "require('$PROJECT_ROOT/src/core/freeze-detector.js')" 2>/dev/null; then
            log_pass "freeze-detector.js imports are valid"
        else
            log_warn "freeze-detector.js has import issues"
        fi
        
        # Test feature-manager.js
        if node -e "require('$PROJECT_ROOT/src/core/feature-manager.js')" 2>/dev/null; then
            log_pass "feature-manager.js imports are valid"
        else
            log_warn "feature-manager.js has import issues"
        fi
        
        # Test credential-manager.js
        if node -e "require('$PROJECT_ROOT/src/security/credential-manager.js')" 2>/dev/null; then
            log_pass "credential-manager.js imports are valid"
        else
            log_warn "credential-manager.js has import issues"
        fi
    else
        log_warn "Node.js not available, skipping JS import checks"
    fi
    
    # Check Python imports
    log_info "Checking Python imports..."
    
    if command -v python3 &> /dev/null; then
        # Test recovery-system.py
        if python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT/src/core'); import recovery_system" 2>/dev/null; then
            log_pass "recovery-system.py imports are valid"
        else
            log_warn "recovery-system.py has import issues (may need dependencies)"
        fi
    else
        log_warn "Python3 not available, skipping Python import checks"
    fi
}

###############################################################################
# Credential Format Validation
###############################################################################

validate_credential_format() {
    local key=$1
    local value=$2
    local pattern=$3
    
    if [[ "$value" =~ $pattern ]]; then
        return 0
    else
        return 1
    fi
}

validate_credentials() {
    echo ""
    echo "========================================="
    echo "Credential Validation"
    echo "========================================="
    
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_warn ".env file not found (use .env.example as template)"
        return
    fi
    
    # Load .env
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs 2>/dev/null || true)
    
    # Validate API keys
    if [ -n "$NDAX_API_KEY" ]; then
        if [ ${#NDAX_API_KEY} -ge 32 ]; then
            log_pass "NDAX_API_KEY format is valid"
        else
            log_fail "NDAX_API_KEY format is invalid (too short)"
        fi
    fi
    
    if [ -n "$OPENAI_API_KEY" ]; then
        if [[ "$OPENAI_API_KEY" =~ ^sk- ]]; then
            log_pass "OPENAI_API_KEY format is valid"
        else
            log_fail "OPENAI_API_KEY format is invalid (should start with sk-)"
        fi
    fi
    
    if [ -n "$HUGGINGFACE_API_KEY" ]; then
        if [[ "$HUGGINGFACE_API_KEY" =~ ^hf_ ]]; then
            log_pass "HUGGINGFACE_API_KEY format is valid"
        else
            log_fail "HUGGINGFACE_API_KEY format is invalid (should start with hf_)"
        fi
    fi
    
    # Validate wallet address
    if [ -n "$WALLET_ADDRESS" ]; then
        if [[ "$WALLET_ADDRESS" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
            log_pass "WALLET_ADDRESS format is valid"
        else
            log_fail "WALLET_ADDRESS format is invalid (should be 0x followed by 40 hex chars)"
        fi
    fi
    
    # Validate private key
    if [ -n "$PRIVATE_KEY" ]; then
        if [[ "$PRIVATE_KEY" =~ ^(0x)?[a-fA-F0-9]{64}$ ]]; then
            log_pass "PRIVATE_KEY format is valid"
        else
            log_fail "PRIVATE_KEY format is invalid (should be 64 hex characters)"
        fi
    fi
    
    # Validate AWS credentials
    if [ -n "$AWS_ACCESS_KEY_ID" ]; then
        if [[ "$AWS_ACCESS_KEY_ID" =~ ^AKIA[A-Z0-9]{16}$ ]]; then
            log_pass "AWS_ACCESS_KEY_ID format is valid"
        else
            log_fail "AWS_ACCESS_KEY_ID format is invalid"
        fi
    fi
    
    if [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        if [ ${#AWS_SECRET_ACCESS_KEY} -eq 40 ]; then
            log_pass "AWS_SECRET_ACCESS_KEY format is valid"
        else
            log_fail "AWS_SECRET_ACCESS_KEY format is invalid (should be 40 characters)"
        fi
    fi
    
    # Validate security keys
    if [ -n "$JWT_SECRET" ]; then
        if [ ${#JWT_SECRET} -ge 32 ]; then
            log_pass "JWT_SECRET is sufficiently long"
        else
            log_warn "JWT_SECRET is too short (should be at least 32 characters)"
        fi
    else
        log_warn "JWT_SECRET not set"
    fi
    
    if [ -n "$ENCRYPTION_KEY" ]; then
        if [ ${#ENCRYPTION_KEY} -eq 64 ]; then
            log_pass "ENCRYPTION_KEY is correct length (64 hex chars)"
        else
            log_warn "ENCRYPTION_KEY is incorrect length (should be 64 hex characters)"
        fi
    else
        log_warn "ENCRYPTION_KEY not set"
    fi
}

###############################################################################
# Configuration File Validation
###############################################################################

validate_configs() {
    echo ""
    echo "========================================="
    echo "Configuration File Validation"
    echo "========================================="
    
    # Validate features.yaml
    if [ -f "$PROJECT_ROOT/config/features.yaml" ]; then
        log_pass "features.yaml exists"
        
        # Try to parse it
        if command -v python3 &> /dev/null; then
            if python3 -c "import yaml; yaml.safe_load(open('$PROJECT_ROOT/config/features.yaml'))" 2>/dev/null; then
                log_pass "features.yaml is valid YAML"
            else
                log_fail "features.yaml has YAML syntax errors"
            fi
        fi
    else
        log_fail "features.yaml not found"
    fi
    
    # Validate package.json
    if [ -f "$PROJECT_ROOT/package.json" ]; then
        log_pass "package.json exists"
        
        if python3 -c "import json; json.load(open('$PROJECT_ROOT/package.json'))" 2>/dev/null || \
           node -e "require('$PROJECT_ROOT/package.json')" 2>/dev/null; then
            log_pass "package.json is valid JSON"
        else
            log_fail "package.json has JSON syntax errors"
        fi
    else
        log_fail "package.json not found"
    fi
}

###############################################################################
# API Endpoint Validation
###############################################################################

validate_api_endpoints() {
    echo ""
    echo "========================================="
    echo "API Endpoint Validation"
    echo "========================================="
    
    # Load .env
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs 2>/dev/null || true)
    fi
    
    # Check if services are running
    local backend_port=${PYTHON_PORT:-8000}
    if curl -s -f "http://localhost:$backend_port" > /dev/null 2>&1; then
        log_pass "Backend API is accessible on port $backend_port"
    else
        log_warn "Backend API is not accessible (service may not be running)"
    fi
    
    local dashboard_port=${PORT:-3000}
    if curl -s -f "http://localhost:$dashboard_port" > /dev/null 2>&1; then
        log_pass "Dashboard is accessible on port $dashboard_port"
    else
        log_warn "Dashboard is not accessible (service may not be running)"
    fi
}

###############################################################################
# Dependency Validation
###############################################################################

validate_dependencies() {
    echo ""
    echo "========================================="
    echo "Dependency Validation"
    echo "========================================="
    
    # Check Node.js dependencies
    if [ -f "$PROJECT_ROOT/package.json" ]; then
        if [ -d "$PROJECT_ROOT/node_modules" ]; then
            log_pass "node_modules directory exists"
            
            # Check for critical dependencies
            local deps=("express" "cors" "dotenv" "react" "react-dom")
            for dep in "${deps[@]}"; do
                if [ -d "$PROJECT_ROOT/node_modules/$dep" ]; then
                    log_info "✓ $dep installed"
                else
                    log_warn "$dep is missing from node_modules"
                fi
            done
        else
            log_fail "node_modules not found - run npm install"
        fi
    fi
    
    # Check Python dependencies
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        if [ -d "$PROJECT_ROOT/venv" ]; then
            log_pass "Python venv exists"
        else
            log_warn "Python venv not found - run python3 -m venv venv"
        fi
    fi
}

###############################################################################
# Permission Validation
###############################################################################

validate_permissions() {
    echo ""
    echo "========================================="
    echo "Permission Validation"
    echo "========================================="
    
    # Check script executability
    local scripts=("auto-setup.sh" "auto-start.sh" "health-check.sh" "validate-system.sh")
    
    for script in "${scripts[@]}"; do
        if [ -f "$PROJECT_ROOT/scripts/$script" ]; then
            if [ -x "$PROJECT_ROOT/scripts/$script" ]; then
                log_pass "$script is executable"
            else
                log_warn "$script is not executable"
                if $FIX_ISSUES; then
                    chmod +x "$PROJECT_ROOT/scripts/$script"
                    log_info "Fixed: Made $script executable"
                fi
            fi
        fi
    done
}

###############################################################################
# Main
###############################################################################

main() {
    # Parse arguments
    for arg in "$@"; do
        case $arg in
            --fix|-f)
                FIX_ISSUES=true
                ;;
            --verbose|-v)
                VERBOSE=true
                ;;
        esac
    done
    
    echo "========================================="
    echo "The-basics System Validation"
    echo "========================================="
    
    if $FIX_ISSUES; then
        echo "Fix mode: ENABLED"
    fi
    
    # Run all validations
    validate_file_paths
    validate_imports
    validate_credentials
    validate_configs
    validate_api_endpoints
    validate_dependencies
    validate_permissions
    
    # Summary
    echo ""
    echo "========================================="
    echo "Validation Summary"
    echo "========================================="
    echo "Total checks: $TOTAL_CHECKS"
    echo -e "${GREEN}Passed: $PASSED_CHECKS${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo -e "${RED}Failed: $FAILED_CHECKS${NC}"
    
    local success_rate=$(echo "scale=2; ($PASSED_CHECKS / $TOTAL_CHECKS) * 100" | bc)
    echo "Success rate: ${success_rate}%"
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${GREEN}✓ System validation passed${NC}"
        exit 0
    else
        echo -e "${RED}✗ System validation failed with $FAILED_CHECKS errors${NC}"
        exit 1
    fi
}

main "$@"
