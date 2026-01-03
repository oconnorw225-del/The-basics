#!/bin/bash

################################################################################
# INTELLIGENT REPOSITORY CONSOLIDATION SCRIPT
# Consolidates 5 source repositories into unified codebase
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_DIR="${REPO_ROOT}/source"
BACKUP_DIR="${REPO_ROOT}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${REPO_ROOT}/consolidation_${TIMESTAMP}.log"

# Source repositories
declare -A REPOS=(
    ["ndax-quantum-engine"]="https://github.com/oconnorw225-del/ndax-quantum-engine.git"
    ["quantum-engine-dashb"]="https://github.com/oconnorw225-del/quantum-engine-dashb.git"
    ["shadowforge-ai-trader"]="https://github.com/oconnorw225-del/shadowforge-ai-trader.git"
    ["repository-web-app"]="https://github.com/oconnorw225-del/repository-web-app.git"
    ["The-new-ones"]="https://github.com/oconnorw225-del/The-new-ones.git"
)

################################################################################
# Helper Functions
################################################################################

print_banner() {
    echo -e "${PURPLE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║       INTELLIGENT REPOSITORY CONSOLIDATION SYSTEM             ║"
    echo "║           Powered by Project Chimera V8.0                     ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log() {
    local level="$1"
    shift
    local message="$@"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1" | tee -a "$LOG_FILE"
}

################################################################################
# Main Functions
################################################################################

init_directories() {
    log_step "Initializing directory structure..."
    
    mkdir -p "${SOURCE_DIR}"
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${REPO_ROOT}/api"
    mkdir -p "${REPO_ROOT}/backend"
    mkdir -p "${REPO_ROOT}/frontend"
    mkdir -p "${REPO_ROOT}/docs"
    mkdir -p "${REPO_ROOT}/tests"
    
    log_success "Directory structure initialized"
}

clone_repositories() {
    log_step "Cloning source repositories..."
    
    cd "${SOURCE_DIR}"
    
    for repo_name in "${!REPOS[@]}"; do
        local repo_url="${REPOS[$repo_name]}"
        local repo_path="${SOURCE_DIR}/${repo_name}"
        
        if [ -d "$repo_path" ]; then
            log_info "Repository $repo_name already exists, pulling latest changes..."
            cd "$repo_path"
            git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || log_warning "Could not pull latest changes for $repo_name"
            cd "${SOURCE_DIR}"
        else
            log_info "Cloning $repo_name..."
            if git clone "$repo_url" "$repo_path" 2>&1 | tee -a "$LOG_FILE"; then
                log_success "Cloned $repo_name"
            else
                log_error "Failed to clone $repo_name"
            fi
        fi
    done
    
    cd "${REPO_ROOT}"
    log_success "All repositories cloned"
}

create_backups() {
    log_step "Creating backups of source repositories..."
    
    for repo_name in "${!REPOS[@]}"; do
        local repo_path="${SOURCE_DIR}/${repo_name}"
        if [ -d "$repo_path" ]; then
            local backup_file="${BACKUP_DIR}/${repo_name}_${TIMESTAMP}.tar.gz"
            log_info "Creating backup: $backup_file"
            
            tar -czf "$backup_file" -C "${SOURCE_DIR}" "$repo_name" 2>&1 | tee -a "$LOG_FILE"
            
            if [ -f "$backup_file" ]; then
                local size=$(du -h "$backup_file" | cut -f1)
                log_success "Backup created: $backup_file ($size)"
            else
                log_error "Failed to create backup for $repo_name"
            fi
        fi
    done
    
    log_success "All backups created in ${BACKUP_DIR}"
}

copy_with_conflict_resolution() {
    local src="$1"
    local dest="$2"
    local description="$3"
    
    if [ ! -e "$src" ]; then
        log_warning "Source not found: $src"
        return 1
    fi
    
    log_info "Copying $description: $src -> $dest"
    
    # Create destination directory if it doesn't exist
    mkdir -p "$(dirname "$dest")"
    
    # Use rsync for intelligent copying with conflict resolution
    if command -v rsync &> /dev/null; then
        rsync -av --update "$src" "$dest" 2>&1 | tee -a "$LOG_FILE" || log_warning "rsync failed for $description"
    else
        # Fallback to cp with update flag
        cp -ruv "$src" "$dest" 2>&1 | tee -a "$LOG_FILE" || log_warning "cp failed for $description"
    fi
}

consolidate_ndax_quantum_engine() {
    log_step "Consolidating ndax-quantum-engine..."
    local repo_path="${SOURCE_DIR}/ndax-quantum-engine"
    
    if [ ! -d "$repo_path" ]; then
        log_warning "Repository ndax-quantum-engine not found"
        return
    fi
    
    # Copy API code
    if [ -d "$repo_path/src" ]; then
        copy_with_conflict_resolution "$repo_path/src/" "${REPO_ROOT}/api/ndax/" "NDAX API"
    fi
    
    # Copy bot.js
    if [ -f "$repo_path/bot.js" ]; then
        copy_with_conflict_resolution "$repo_path/bot.js" "${REPO_ROOT}/backend/bot.js" "NDAX bot.js"
    fi
    
    # Copy docs
    if [ -d "$repo_path/docs" ]; then
        copy_with_conflict_resolution "$repo_path/docs/" "${REPO_ROOT}/docs/ndax/" "NDAX documentation"
    fi
    
    # Copy tests
    if [ -d "$repo_path/tests" ]; then
        copy_with_conflict_resolution "$repo_path/tests/" "${REPO_ROOT}/tests/ndax/" "NDAX tests"
    fi
    
    log_success "ndax-quantum-engine consolidated"
}

consolidate_quantum_engine_dashb() {
    log_step "Consolidating quantum-engine-dashb..."
    local repo_path="${SOURCE_DIR}/quantum-engine-dashb"
    
    if [ ! -d "$repo_path" ]; then
        log_warning "Repository quantum-engine-dashb not found"
        return
    fi
    
    # Copy frontend/dashboard
    if [ -d "$repo_path/src" ]; then
        copy_with_conflict_resolution "$repo_path/src/" "${REPO_ROOT}/frontend/dashboard/" "Dashboard frontend"
    fi
    
    # Copy docs
    if [ -d "$repo_path/docs" ]; then
        copy_with_conflict_resolution "$repo_path/docs/" "${REPO_ROOT}/docs/dashboard/" "Dashboard documentation"
    fi
    
    # Copy workflows
    if [ -d "$repo_path/.github/workflows" ]; then
        copy_with_conflict_resolution "$repo_path/.github/workflows/" "${REPO_ROOT}/.github/workflows/" "Dashboard workflows"
    fi
    
    log_success "quantum-engine-dashb consolidated"
}

consolidate_shadowforge_ai_trader() {
    log_step "Consolidating shadowforge-ai-trader..."
    local repo_path="${SOURCE_DIR}/shadowforge-ai-trader"
    
    if [ ! -d "$repo_path" ]; then
        log_warning "Repository shadowforge-ai-trader not found"
        return
    fi
    
    # Copy backend
    if [ -d "$repo_path/backend" ]; then
        copy_with_conflict_resolution "$repo_path/backend/" "${REPO_ROOT}/backend/shadowforge/" "Shadowforge backend"
    fi
    
    # Copy chimera_core
    if [ -d "$repo_path/chimera_core" ]; then
        copy_with_conflict_resolution "$repo_path/chimera_core/" "${REPO_ROOT}/backend/chimera/" "Chimera core"
    fi
    
    # Copy strategy files
    if [ -d "$repo_path/src" ]; then
        copy_with_conflict_resolution "$repo_path/src/" "${REPO_ROOT}/backend/strategy/" "Trading strategies"
    fi
    
    # Copy unified_system.py
    if [ -f "$repo_path/unified_system.py" ]; then
        copy_with_conflict_resolution "$repo_path/unified_system.py" "${REPO_ROOT}/backend/unified_system.py" "Unified system"
    fi
    
    # Copy tests
    if [ -d "$repo_path/tests" ]; then
        copy_with_conflict_resolution "$repo_path/tests/" "${REPO_ROOT}/tests/shadowforge/" "Shadowforge tests"
    fi
    
    # Copy docs
    if [ -d "$repo_path/docs" ]; then
        copy_with_conflict_resolution "$repo_path/docs/" "${REPO_ROOT}/docs/shadowforge/" "Shadowforge documentation"
    fi
    
    log_success "shadowforge-ai-trader consolidated"
}

consolidate_repository_web_app() {
    log_step "Consolidating repository-web-app..."
    local repo_path="${SOURCE_DIR}/repository-web-app"
    
    if [ ! -d "$repo_path" ]; then
        log_warning "Repository repository-web-app not found"
        return
    fi
    
    # Copy frontend
    if [ -d "$repo_path/src" ]; then
        copy_with_conflict_resolution "$repo_path/src/" "${REPO_ROOT}/frontend/web-app/" "Web app frontend"
    fi
    
    # Copy backend API
    if [ -d "$repo_path/backend" ]; then
        copy_with_conflict_resolution "$repo_path/backend/" "${REPO_ROOT}/backend/api/" "Web app API"
    fi
    
    # Copy docs
    if [ -d "$repo_path/docs" ]; then
        copy_with_conflict_resolution "$repo_path/docs/" "${REPO_ROOT}/docs/web-app/" "Web app documentation"
    fi
    
    # Copy workflows
    if [ -d "$repo_path/.github/workflows" ]; then
        copy_with_conflict_resolution "$repo_path/.github/workflows/" "${REPO_ROOT}/.github/workflows/" "Web app workflows"
    fi
    
    log_success "repository-web-app consolidated"
}

consolidate_the_new_ones() {
    log_step "Consolidating The-new-ones..."
    local repo_path="${SOURCE_DIR}/The-new-ones"
    
    if [ ! -d "$repo_path" ]; then
        log_warning "Repository The-new-ones not found"
        return
    fi
    
    # Copy config files
    if [ -d "$repo_path/config" ]; then
        copy_with_conflict_resolution "$repo_path/config/" "${REPO_ROOT}/config/recovered/" "Recovery configs"
    fi
    
    # Copy .env.example if exists
    if [ -f "$repo_path/.env.example" ]; then
        copy_with_conflict_resolution "$repo_path/.env.example" "${REPO_ROOT}/config/.env.example.recovered" "Recovery env example"
    fi
    
    # Copy recovery scripts
    if [ -d "$repo_path/scripts" ]; then
        copy_with_conflict_resolution "$repo_path/scripts/" "${REPO_ROOT}/scripts/recovery/" "Recovery scripts"
    fi
    
    # Copy docs
    if [ -d "$repo_path/docs" ]; then
        copy_with_conflict_resolution "$repo_path/docs/" "${REPO_ROOT}/docs/recovery/" "Recovery documentation"
    fi
    
    log_success "The-new-ones consolidated"
}

generate_report() {
    log_step "Generating consolidation report..."
    
    local report_file="${REPO_ROOT}/CONSOLIDATION_REPORT.md"
    
    cat > "$report_file" << EOF
# Repository Consolidation Report

**Generated:** $(date '+%Y-%m-%d %H:%M:%S')  
**Timestamp:** ${TIMESTAMP}

## Overview

This report summarizes the consolidation of 5 source repositories into the unified \`the-basics\` codebase.

## Source Repositories

$(for repo in "${!REPOS[@]}"; do
    echo "- **$repo**: ${REPOS[$repo]}"
done)

## Consolidation Summary

### Files Consolidated

- **API Layer**: \`api/\`
  - NDAX Quantum Engine API
  - Repository Web App API

- **Backend**: \`backend/\`
  - Trading bot (bot.js)
  - Shadowforge AI trader
  - Chimera core intelligence
  - Trading strategies
  - Unified system

- **Frontend**: \`frontend/\`
  - Dashboard UI
  - Web application

- **Documentation**: \`docs/\`
  - NDAX documentation
  - Dashboard documentation
  - Shadowforge documentation
  - Web app documentation
  - Recovery documentation

- **Tests**: \`tests/\`
  - Combined test suites from all repositories

- **Configuration**: \`config/\`
  - Recovery configurations
  - Environment templates

## Backups Created

$(ls -lh "${BACKUP_DIR}"/*.tar.gz 2>/dev/null | awk '{print "- " $9 " (" $5 ")"}' || echo "No backups found")

## Log File

Full consolidation log: \`consolidation_${TIMESTAMP}.log\`

## Status

✅ Consolidation completed successfully

## Next Steps

1. Review consolidated files in each directory
2. Test integrated functionality
3. Update dependencies if needed
4. Run test suites
5. Deploy unified system

---

*Powered by Project Chimera V8.0 - Transcendent Intelligence*
EOF
    
    log_success "Report generated: $report_file"
}

cleanup() {
    log_step "Cleaning up temporary files..."
    
    # Optionally clean up source directory after consolidation
    # Uncomment to remove cloned repos after backup
    # rm -rf "${SOURCE_DIR}"
    
    log_success "Cleanup completed"
}

################################################################################
# Main Execution
################################################################################

main() {
    print_banner
    
    log_info "Starting repository consolidation..."
    log_info "Repository root: ${REPO_ROOT}"
    log_info "Log file: ${LOG_FILE}"
    
    init_directories
    clone_repositories
    create_backups
    
    log_step "Consolidating repositories..."
    consolidate_ndax_quantum_engine
    consolidate_quantum_engine_dashb
    consolidate_shadowforge_ai_trader
    consolidate_repository_web_app
    consolidate_the_new_ones
    
    generate_report
    cleanup
    
    echo ""
    log_success "╔════════════════════════════════════════════════════════════════╗"
    log_success "║          CONSOLIDATION COMPLETED SUCCESSFULLY                  ║"
    log_success "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    log_info "Review the consolidation report: CONSOLIDATION_REPORT.md"
    log_info "Check the log file for details: $LOG_FILE"
    echo ""
}

# Run main function
main "$@"
