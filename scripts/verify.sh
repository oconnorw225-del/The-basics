#!/bin/bash

################################################################################
# VERIFICATION SCRIPT - The Basics Repository
# Validates repository structure and consolidation completeness
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

################################################################################
# Configuration
################################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

################################################################################
# Helper Functions
################################################################################

print_banner() {
    echo -e "${MAGENTA}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║          REPOSITORY VERIFICATION & VALIDATION                  ║"
    echo "║              Consolidation Completeness Check                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓ PASS]${NC} $1"
    ((PASSED_CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}[! WARN]${NC} $1"
    ((WARNING_CHECKS++))
}

log_error() {
    echo -e "${RED}[✗ FAIL]${NC} $1"
    ((FAILED_CHECKS++))
}

check_exists() {
    ((TOTAL_CHECKS++))
    local path="$1"
    local description="$2"
    local required="${3:-true}"
    
    if [ -e "$path" ]; then
        log_success "$description exists: $path"
        return 0
    else
        if [ "$required" = "true" ]; then
            log_error "$description missing: $path"
        else
            log_warning "$description not found (optional): $path"
        fi
        return 1
    fi
}

check_directory() {
    ((TOTAL_CHECKS++))
    local path="$1"
    local description="$2"
    local should_have_files="${3:-false}"
    
    if [ -d "$path" ]; then
        local file_count=$(find "$path" -type f 2>/dev/null | wc -l)
        if [ "$should_have_files" = "true" ] && [ "$file_count" -eq 0 ]; then
            log_warning "$description exists but is empty: $path"
        else
            log_success "$description exists ($file_count files): $path"
        fi
        return 0
    else
        log_error "$description missing: $path"
        return 1
    fi
}

check_file_not_empty() {
    ((TOTAL_CHECKS++))
    local path="$1"
    local description="$2"
    
    if [ -f "$path" ]; then
        local size
        if ! size=$(wc -l < "$path" 2>/dev/null); then
            size=0
        fi
        if [ "$size" -gt 0 ]; then
            log_success "$description is valid ($size lines)"
            return 0
        else
            log_warning "$description exists but is empty"
            return 1
        fi
    else
        log_error "$description not found: $path"
        return 1
    fi
}

################################################################################
# Verification Checks
################################################################################

verify_essential_directories() {
    log_info "Verifying essential directory structure..."
    echo ""
    
    check_directory "${REPO_ROOT}/api" "API directory"
    check_directory "${REPO_ROOT}/backend" "Backend directory" "true"
    check_directory "${REPO_ROOT}/frontend" "Frontend directory" "true"
    check_directory "${REPO_ROOT}/docs" "Documentation directory"
    check_directory "${REPO_ROOT}/tests" "Tests directory"
    check_directory "${REPO_ROOT}/config" "Config directory"
    check_directory "${REPO_ROOT}/scripts" "Scripts directory"
    check_directory "${REPO_ROOT}/automation" "Automation directory" "true"
    check_directory "${REPO_ROOT}/backups" "Backups directory"
    
    echo ""
}

verify_essential_files() {
    log_info "Verifying essential files..."
    echo ""
    
    check_file_not_empty "${REPO_ROOT}/README.md" "Main README"
    check_exists "${REPO_ROOT}/.gitignore" ".gitignore file"
    check_exists "${REPO_ROOT}/.env.example" "Environment example file"
    check_exists "${REPO_ROOT}/package.json" "package.json"
    check_exists "${REPO_ROOT}/requirements.txt" "Python requirements"
    
    echo ""
}

verify_consolidation_files() {
    log_info "Verifying consolidation system files..."
    echo ""
    
    check_exists "${REPO_ROOT}/automation/consolidate.sh" "Consolidation script"
    check_file_not_empty "${REPO_ROOT}/automation/README.md" "Automation documentation"
    check_exists "${REPO_ROOT}/config/consolidation-config.json" "Consolidation config"
    check_exists "${REPO_ROOT}/scripts/setup.sh" "Setup script"
    check_exists "${REPO_ROOT}/scripts/verify.sh" "Verification script (this file)"
    check_exists "${REPO_ROOT}/backups/.gitkeep" "Backups .gitkeep"
    
    echo ""
}

verify_github_workflows() {
    log_info "Verifying GitHub Actions workflows..."
    echo ""
    
    check_directory "${REPO_ROOT}/.github/workflows" "Workflows directory" "true"
    check_exists "${REPO_ROOT}/.github/workflows/consolidate.yml" "Consolidation workflow"
    
    echo ""
}

verify_consolidated_content() {
    log_info "Verifying consolidated content from source repositories..."
    echo ""
    
    # Check for content from each source repo
    log_info "Checking NDAX Quantum Engine content..."
    if [ -f "${REPO_ROOT}/backend/bot.js" ] || [ -d "${REPO_ROOT}/api/ndax" ]; then
        log_success "NDAX content found"
        ((PASSED_CHECKS++))
    else
        log_warning "NDAX content not found (may need consolidation)"
        ((WARNING_CHECKS++))
    fi
    ((TOTAL_CHECKS++))
    
    log_info "Checking Dashboard content..."
    if [ -d "${REPO_ROOT}/frontend/dashboard" ]; then
        log_success "Dashboard content found"
        ((PASSED_CHECKS++))
    else
        log_warning "Dashboard content not found (may need consolidation)"
        ((WARNING_CHECKS++))
    fi
    ((TOTAL_CHECKS++))
    
    log_info "Checking Shadowforge content..."
    if [ -d "${REPO_ROOT}/backend/chimera" ] || [ -d "${REPO_ROOT}/backend/strategy" ]; then
        log_success "Shadowforge content found"
        ((PASSED_CHECKS++))
    else
        log_warning "Shadowforge content not found (may need consolidation)"
        ((WARNING_CHECKS++))
    fi
    ((TOTAL_CHECKS++))
    
    log_info "Checking Web App content..."
    if [ -d "${REPO_ROOT}/frontend/web-app" ] || [ -d "${REPO_ROOT}/backend/api" ]; then
        log_success "Web App content found"
        ((PASSED_CHECKS++))
    else
        log_warning "Web App content not found (may need consolidation)"
        ((WARNING_CHECKS++))
    fi
    ((TOTAL_CHECKS++))
    
    log_info "Checking Recovery content..."
    if [ -d "${REPO_ROOT}/config/recovered" ] || [ -d "${REPO_ROOT}/scripts/recovery" ]; then
        log_success "Recovery content found"
        ((PASSED_CHECKS++))
    else
        log_warning "Recovery content not found (may need consolidation)"
        ((WARNING_CHECKS++))
    fi
    ((TOTAL_CHECKS++))
    
    echo ""
}

verify_security() {
    log_info "Verifying security configuration..."
    echo ""
    
    # Check that .env is not tracked
    if git -C "${REPO_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        if git -C "${REPO_ROOT}" ls-files --error-unmatch .env >/dev/null 2>&1; then
            log_error ".env file is tracked by git (SECURITY RISK!)"
        else
            log_success ".env file is not tracked by git"
            ((PASSED_CHECKS++))
        fi
    else
        log_warning "Not a git repository; skipping .env tracking check"
        ((WARNING_CHECKS++))
    fi
    ((TOTAL_CHECKS++))
    
    # Check .gitignore for sensitive patterns
    if grep -q "\.env$" "${REPO_ROOT}/.gitignore"; then
        log_success ".gitignore includes .env pattern"
        ((PASSED_CHECKS++))
    else
        log_error ".gitignore missing .env pattern"
    fi
    ((TOTAL_CHECKS++))
    
    if grep -q "backups/\*\.tar\.gz" "${REPO_ROOT}/.gitignore" || grep -q "backups/" "${REPO_ROOT}/.gitignore"; then
        log_success ".gitignore includes backup patterns"
        ((PASSED_CHECKS++))
    else
        log_warning ".gitignore may be missing backup patterns"
    fi
    ((TOTAL_CHECKS++))
    
    echo ""
}

verify_executability() {
    log_info "Verifying script executability..."
    echo ""
    
    local scripts=(
        "automation/consolidate.sh"
        "scripts/setup.sh"
        "scripts/verify.sh"
    )
    
    for script in "${scripts[@]}"; do
        ((TOTAL_CHECKS++))
        if [ -x "${REPO_ROOT}/${script}" ]; then
            log_success "$script is executable"
            ((PASSED_CHECKS++))
        else
            log_warning "$script is not executable (run: chmod +x $script)"
        fi
    done
    
    echo ""
}

check_for_backups() {
    log_info "Checking for backups..."
    echo ""
    
    local backup_count=$(find "${REPO_ROOT}/backups" -name "*.tar.gz" 2>/dev/null | wc -l)
    
    ((TOTAL_CHECKS++))
    if [ "$backup_count" -gt 0 ]; then
        log_success "Found $backup_count backup file(s)"
        ((PASSED_CHECKS++))
    else
        log_warning "No backup files found (run consolidation to create backups)"
    fi
    
    echo ""
}

suggest_fixes() {
    echo ""
    log_info "Suggested fixes for issues:"
    echo ""
    
    if [ $FAILED_CHECKS -gt 0 ] || [ $WARNING_CHECKS -gt 0 ]; then
        echo "  1. Run setup script: bash scripts/setup.sh"
        echo "  2. Run consolidation: bash automation/consolidate.sh"
        echo "  3. Make scripts executable: chmod +x scripts/*.sh automation/*.sh"
        echo "  4. Review .gitignore for security patterns"
        echo "  5. Ensure .env is not tracked: git rm --cached .env (if needed)"
        echo ""
    else
        echo "  No issues found! Repository is properly configured."
        echo ""
    fi
}

################################################################################
# Summary Report
################################################################################

print_summary() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                    VERIFICATION SUMMARY                         ${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  Total Checks:    $TOTAL_CHECKS"
    echo -e "  ${GREEN}Passed:          $PASSED_CHECKS${NC}"
    echo -e "  ${YELLOW}Warnings:        $WARNING_CHECKS${NC}"
    echo -e "  ${RED}Failed:          $FAILED_CHECKS${NC}"
    echo ""
    
    local pass_rate=0
    if [ $TOTAL_CHECKS -gt 0 ]; then
        pass_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    fi
    
    echo "  Pass Rate:       ${pass_rate}%"
    echo ""
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${GREEN}"
        echo "╔════════════════════════════════════════════════════════════════╗"
        echo "║                  ✓ VERIFICATION PASSED                         ║"
        echo "╚════════════════════════════════════════════════════════════════╝"
        echo -e "${NC}"
        
        if [ $WARNING_CHECKS -gt 0 ]; then
            echo -e "${YELLOW}Note: There are $WARNING_CHECKS warning(s) that should be reviewed.${NC}"
            echo ""
        fi
        
        return 0
    else
        echo -e "${RED}"
        echo "╔════════════════════════════════════════════════════════════════╗"
        echo "║                  ✗ VERIFICATION FAILED                         ║"
        echo "╚════════════════════════════════════════════════════════════════╝"
        echo -e "${NC}"
        echo ""
        return 1
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    cd "${REPO_ROOT}"
    
    print_banner
    echo ""
    log_info "Verifying repository: ${REPO_ROOT}"
    echo ""
    
    verify_essential_directories
    verify_essential_files
    verify_consolidation_files
    verify_github_workflows
    verify_consolidated_content
    verify_security
    verify_executability
    check_for_backups
    
    suggest_fixes
    print_summary
}

# Run main function and exit with appropriate code
if main "$@"; then
    exit 0
else
    exit 1
fi
