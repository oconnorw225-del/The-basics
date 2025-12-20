#!/bin/bash

################################################################################
# 🧠 SMART CONSOLIDATION WRAPPER
# Intelligent wrapper around Chimera consolidation with additional features
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
    echo "║           🧠 SMART CONSOLIDATION SYSTEM                        ║"
    echo "║        Powered by Project Chimera Intelligence                ║"
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
    
    if [ -f "requirements_chimera.txt" ]; then
        pip install -q -r requirements_chimera.txt 2>/dev/null || \
            echo "⚠️  Some dependencies failed to install"
    fi
    
    if [ -f "requirements.txt" ]; then
        pip install -q -r requirements.txt 2>/dev/null || \
            echo "⚠️  Some dependencies failed to install"
    fi
    
    echo -e "${GREEN}[✓]${NC} Python dependencies ready"
}

select_chimera_version() {
    echo ""
    echo "Select Chimera Version:"
    echo "  1) V4.0 - Freelance Engine"
    echo "  2) V5.0 - Self-Learning AI"
    echo "  3) V6.0 - Neural Prediction"
    echo "  4) V7.0 - Quantum Computing"
    echo "  5) V8.0 - Transcendent Intelligence (Recommended)"
    echo ""
    read -p "Enter choice [1-5] (default: 5): " choice
    
    case $choice in
        1) export CHIMERA_VERSION="4.0";;
        2) export CHIMERA_VERSION="5.0";;
        3) export CHIMERA_VERSION="6.0";;
        4) export CHIMERA_VERSION="7.0";;
        5|"") export CHIMERA_VERSION="8.0";;
        *) 
            echo "Invalid choice, using V8.0"
            export CHIMERA_VERSION="8.0"
            ;;
    esac
    
    echo -e "${GREEN}[✓]${NC} Selected Chimera V${CHIMERA_VERSION}"
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

run_chimera_consolidation() {
    echo ""
    echo -e "${PURPLE}[🧬 CHIMERA]${NC} Starting consolidation..."
    echo ""
    
    # Make sure script is executable
    chmod +x automation/chimera_consolidate.sh
    
    # Run consolidation
    bash automation/chimera_consolidate.sh
}

post_consolidation_summary() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  CONSOLIDATION COMPLETE                        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "📊 Generated Reports:"
    [ -f "audit_report.json" ] && echo "  ✓ audit_report.json"
    [ -f "chimera_analysis.json" ] && echo "  ✓ chimera_analysis.json"
    [ -f "CHIMERA_CONSOLIDATION_REPORT.md" ] && echo "  ✓ CHIMERA_CONSOLIDATION_REPORT.md"
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
    echo "  1. Review CHIMERA_CONSOLIDATION_REPORT.md"
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
        select_chimera_version
        install_python_deps
        run_pre_consolidation_checks
    else
        # Non-interactive mode (for CI/CD)
        export CHIMERA_VERSION="${1:-8.0}"
    fi
    
    run_chimera_consolidation
    post_consolidation_summary
}

# Run main
main "$@"
