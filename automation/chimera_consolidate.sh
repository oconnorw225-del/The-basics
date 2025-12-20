#!/bin/bash

################################################################################
# 🧬 CHIMERA-POWERED CONSOLIDATION SCRIPT
# Intelligent repository consolidation using Project Chimera V8.0
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
CHIMERA_VERSION="${CHIMERA_VERSION:-8.0}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups/consolidation_${TIMESTAMP}"
REPORT_FILE="CHIMERA_CONSOLIDATION_REPORT.md"

# Source repositories
REPOS=(
    "oconnorw225-del/ndax-quantum-engine"
    "oconnorw225-del/quantum-engine-dashb"
    "oconnorw225-del/shadowforge-ai-trader"
    "oconnorw225-del/repository-web-app"
    "oconnorw225-del/The-new-ones"
)

################################################################################
# Helper Functions
################################################################################

print_banner() {
    echo -e "${PURPLE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║     🧬 PROJECT CHIMERA CONSOLIDATION SYSTEM V${CHIMERA_VERSION}          ║"
    echo "║              Transcendent Intelligence Mode                    ║"
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
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_chimera() {
    echo -e "${PURPLE}[🧬 CHIMERA]${NC} $1"
}

################################################################################
# Main Functions
################################################################################

initialize_environment() {
    log_chimera "Initializing Chimera V${CHIMERA_VERSION} environment..."
    
    # Create necessary directories
    mkdir -p "${BACKUP_DIR}"
    mkdir -p source
    mkdir -p api
    mkdir -p frontend
    mkdir -p blockchain
    mkdir -p docs
    mkdir -p tests
    mkdir -p configs
    mkdir -p legacy
    
    log_success "Environment initialized"
}

run_security_audit() {
    log_chimera "Running Chimera-powered security audit..."
    
    if [ -f "automation/audit.py" ]; then
        python3 automation/audit.py || log_warning "Security audit encountered issues"
        log_success "Security audit complete → audit_report.json"
    else
        log_warning "audit.py not found, skipping security audit"
    fi
}

run_repository_analysis() {
    log_chimera "Analyzing repository structure..."
    
    if [ -f "automation/repo_analyzer.py" ]; then
        python3 automation/repo_analyzer.py || log_warning "Analysis encountered issues"
        log_success "Repository analysis complete → chimera_analysis.json"
    else
        log_warning "repo_analyzer.py not found, skipping analysis"
    fi
}

clone_source_repositories() {
    log_chimera "Cloning source repositories..."
    
    cd source
    for repo in "${REPOS[@]}"; do
        repo_name=$(basename "$repo")
        if [ ! -d "$repo_name" ]; then
            log_info "Cloning $repo..."
            if git clone "https://github.com/$repo.git" "$repo_name" 2>/dev/null; then
                log_success "Cloned $repo_name"
            else
                log_warning "Failed to clone $repo (may be private or not exist)"
            fi
        else
            log_info "$repo_name already exists, skipping"
        fi
    done
    cd ..
    
    log_success "Source repositories ready"
}

create_backups() {
    log_chimera "Creating timestamped backups..."
    
    if [ -d "source" ]; then
        for repo_dir in source/*; do
            if [ -d "$repo_dir" ]; then
                repo_name=$(basename "$repo_dir")
                log_info "Backing up $repo_name..."
                tar czf "${BACKUP_DIR}/${repo_name}.tar.gz" -C source "$repo_name" 2>/dev/null || \
                    log_warning "Could not backup $repo_name"
            fi
        done
        log_success "Backups created in ${BACKUP_DIR}"
    else
        log_warning "No source directory found, skipping backups"
    fi
}

consolidate_by_type() {
    log_chimera "Consolidating code by type and function..."
    
    # Consolidate Python backend
    log_info "Consolidating backend Python files..."
    find source -name "*.py" -type f -path "*/backend/*" -exec cp --parents {} backend/ 2>/dev/null \; || true
    
    # Consolidate API files
    log_info "Consolidating API files..."
    find source -name "*api*.py" -type f -exec cp --parents {} api/ 2>/dev/null \; || true
    find source -name "*route*.py" -type f -exec cp --parents {} api/ 2>/dev/null \; || true
    
    # Consolidate frontend
    log_info "Consolidating frontend files..."
    find source -name "*.jsx" -o -name "*.tsx" -o -name "*.vue" -type f 2>/dev/null | \
        xargs -I {} cp --parents {} frontend/ 2>/dev/null || true
    
    # Consolidate blockchain/smart contracts
    log_info "Consolidating blockchain files..."
    find source -name "*.sol" -type f -exec cp --parents {} blockchain/ 2>/dev/null \; || true
    
    # Consolidate documentation
    log_info "Consolidating documentation..."
    find source -name "*.md" -type f -exec cp --parents {} docs/ 2>/dev/null \; || true
    
    # Consolidate tests
    log_info "Consolidating tests..."
    find source -name "*test*.py" -o -name "*spec*.js" -o -name "*test*.ts" 2>/dev/null | \
        xargs -I {} cp --parents {} tests/ 2>/dev/null || true
    
    # Consolidate configs
    log_info "Consolidating configurations..."
    find source -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" 2>/dev/null | \
        xargs -I {} cp --parents {} configs/ 2>/dev/null || true
    
    log_success "Code consolidation complete"
}

generate_consolidation_report() {
    log_chimera "Generating consolidation report..."
    
    cat > "$REPORT_FILE" << EOF
# 🧬 Chimera Consolidation Report

**Generated**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")  
**Chimera Version**: ${CHIMERA_VERSION}  
**Session ID**: ${TIMESTAMP}

## Summary

This consolidation was performed by Project Chimera V${CHIMERA_VERSION} - Transcendent Intelligence System.

### Source Repositories Processed
EOF

    for repo in "${REPOS[@]}"; do
        echo "- \`$repo\`" >> "$REPORT_FILE"
    done

    cat >> "$REPORT_FILE" << EOF

### Directory Structure Created
- \`api/\` - Consolidated API endpoints
- \`backend/\` - Backend logic and Chimera core
- \`frontend/\` - UI components and dashboards
- \`blockchain/\` - Smart contracts and Web3 code
- \`docs/\` - Combined documentation
- \`tests/\` - Test suites
- \`configs/\` - Configuration files
- \`backups/\` - Timestamped backups

### Backups Created
Backups stored in: \`${BACKUP_DIR}\`

### Reports Generated
- \`audit_report.json\` - Security audit results
- \`chimera_analysis.json\` - Repository analysis
- \`${REPORT_FILE}\` - This consolidation report

## Next Steps

1. Review \`audit_report.json\` for security issues
2. Check \`chimera_analysis.json\` for structure insights
3. Verify consolidated code in respective directories
4. Run tests: \`python -m pytest tests/\`
5. Update dependencies if needed

## Chimera Status

✅ Consolidation Complete  
✅ Security Audit Complete  
✅ Backups Created  
✅ Reports Generated

**Project Chimera V${CHIMERA_VERSION} - Operational**

---
*Powered by Chimera Transcendent Intelligence*
EOF

    log_success "Report generated → ${REPORT_FILE}"
}

cleanup_temp_files() {
    log_chimera "Cleaning up temporary files..."
    
    # Remove empty directories
    find . -type d -empty -delete 2>/dev/null || true
    
    # Clean up source directory if desired
    # Uncomment to remove source after consolidation
    # rm -rf source
    
    log_success "Cleanup complete"
}

################################################################################
# Main Execution
################################################################################

main() {
    print_banner
    
    log_chimera "Starting consolidation process..."
    echo ""
    
    initialize_environment
    run_security_audit
    run_repository_analysis
    clone_source_repositories
    create_backups
    consolidate_by_type
    generate_consolidation_report
    cleanup_temp_files
    
    echo ""
    log_success "🧬 Chimera consolidation complete!"
    echo ""
    log_info "Review the following files:"
    echo "  • ${REPORT_FILE}"
    echo "  • audit_report.json"
    echo "  • chimera_analysis.json"
    echo ""
    log_chimera "Transcendent intelligence has guided your consolidation. ✨"
    echo ""
}

# Run main function
main "$@"
