#!/bin/bash

################################################################################
# SMART CONSOLIDATION WRAPPER
# Interactive wrapper for repository consolidation with validation
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           SMART CONSOLIDATION SYSTEM                          ║"
    echo "║           Automated Repository Management                     ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_dependencies() {
    echo -e "${BLUE}[CHECK]${NC} Verifying dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed."
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        echo "❌ Git is required but not installed."
        exit 1
    fi
    
    echo -e "${GREEN}[✓]${NC} All dependencies satisfied"
}

install_python_deps() {
    echo -e "${BLUE}[SETUP]${NC} Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -q -r requirements.txt 2>/dev/null || \
            echo "⚠️  Some dependencies failed to install"
    fi
    
    echo -e "${GREEN}[✓]${NC} Python dependencies ready"
}
    
    echo -e "${GREEN}[✓]${NC} Selected consolidation mode"
}

run_pre_consolidation_checks() {
    echo -e "${BLUE}[CHECK]${NC} Running pre-consolidation checks..."
    
    # Check if we're in a git repository
    if [ ! -d ".git" ]; then
        echo "⚠️  Not in a git repository. Some features may not work."
    fi
    
    # Check available disk space
    available_space=$(df . | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 1048576 ]; then
        echo "⚠️  Low disk space (< 1GB). Consolidation may fail."
    fi
    
    echo -e "${GREEN}[✓]${NC} Pre-consolidation checks complete"
}

run_consolidation() {
    echo ""
    echo -e "${PURPLE}[CONSOLIDATION]${NC} Starting consolidation..."
    echo ""
    
    # Make sure script is executable
    chmod +x automation/consolidate_repos.sh
    
    # Run consolidation
    bash automation/consolidate_repos.sh
}

post_consolidation_summary() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  CONSOLIDATION COMPLETE                        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "📊 Generated Reports:"
    [ -f "audit_report.json" ] && echo "  ✓ audit_report.json"
    [ -f "analysis.json" ] && echo "  ✓ analysis.json"
    [ -f "CONSOLIDATION_REPORT.md" ] && echo "  ✓ CONSOLIDATION_REPORT.md"
    echo ""
    echo "📁 Consolidated Directories:"
    [ -d "api" ] && echo "  ✓ api/"
    [ -d "backend" ] && echo "  ✓ backend/"
    [ -d "frontend" ] && echo "  ✓ frontend/"
    [ -d "blockchain" ] && echo "  ✓ blockchain/"
    echo ""
    echo "💾 Backups:"
    backup_count=$(find backups -name "*.tar.gz" 2>/dev/null | wc -l)
    echo "  ✓ $backup_count backup archives created"
    echo ""
    echo "🔍 Next Steps:"
    echo "  1. Review CONSOLIDATION_REPORT.md"
    echo "  2. Check audit_report.json for security issues"
    echo "  3. Test consolidated code"
    echo "  4. Commit changes to repository"
    echo ""
}

main() {
    print_header
    check_dependencies
    
    # Interactive mode if no arguments
    if [ $# -eq 0 ]; then
        install_python_deps
        run_pre_consolidation_checks
    fi
    
    run_consolidation
    post_consolidation_summary
}

# Run main
main "$@"
