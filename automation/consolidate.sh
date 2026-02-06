#!/bin/bash
# Smart Consolidation Script with Validation & Error Handling

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_step() { echo -e "${BLUE}➜${NC} $1"; }

# Validation function
validate_source() {
    local src=$1
    local dest=$2
    
    if [ -d "$src" ]; then
        local count=$(find "$src" -type f 2>/dev/null | wc -l)
        if [ "$count" -gt 0 ]; then
            log_info "Found $count files in $src"
            return 0
        else
            log_warn "Directory $src exists but is empty"
            return 1
        fi
    else
        log_warn "Source directory $src does not exist"
        return 1
    fi
}

# Smart copy function with validation
smart_copy() {
    local src=$1
    local dest=$2
    local label=$3
    
    log_step "Processing $label..."
    
    if validate_source "$src" "$dest"; then
        cp -r "$src"/* "$dest/" 2>/dev/null && \
            log_info "Successfully copied $label to $dest/" || \
            log_warn "Partial copy for $label (some files may have failed)"
    else
        log_warn "Skipping $label - source not available"
    fi
}

# Main consolidation logic
log_step "Starting intelligent consolidation..."

# API consolidation
smart_copy "source/ndax-quantum-engine/api" "api" "Quantum Engine API"
smart_copy "source/shadowforge-ai-trader/api" "api" "ShadowForge API"

# Backend consolidation
smart_copy "source/shadowforge-ai-trader/strategy" "backend" "Trading Strategies"
smart_copy "source/ndax-quantum-engine/backend" "backend" "Quantum Backend"
smart_copy "source/shadowforge-ai-trader/src" "backend" "ShadowForge Core"

# Frontend consolidation
smart_copy "source/quantum-engine-dashb/src" "frontend" "Quantum Dashboard"
smart_copy "source/repository-web-app/src" "frontend" "Web App Components"
smart_copy "source/The-new-ones/frontend" "frontend" "New UI Components"

# Documentation
smart_copy "source/ndax-quantum-engine/docs" "docs" "Quantum Docs"
smart_copy "source/shadowforge-ai-trader/docs" "docs" "Trading Docs"
smart_copy "source/The-new-ones/docs" "docs" "Additional Docs"

# Workflows
smart_copy "source/quantum-engine-dashb/.github/workflows" ".github/workflows" "Dashboard Workflows"
smart_copy "source/repository-web-app/.github/workflows" ".github/workflows" "Web App Workflows"

# Tests
smart_copy "source/shadowforge-ai-trader/tests" "tests" "Trading Tests"
smart_copy "source/ndax-quantum-engine/tests" "tests" "Quantum Tests"
smart_copy "source/The-new-ones/tests" "tests" "Additional Tests"

log_info "Consolidation complete!"