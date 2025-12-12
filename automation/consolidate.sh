#!/bin/bash

# Repository Consolidation Script
# This script is designed to run within the GitHub Actions workflow (consolidate.yml)
# The workflow first clones source repositories into the source/ directory
# This script then copies the best parts from each repository

# Enhanced with:
# - Error handling that doesn't exit on failures
# - Continuous run mode support
# - Timestamped logging
# - Summary reporting

# Configuration
CONTINUOUS_MODE=false
SLEEP_INTERVAL=86400  # Default: 24 hours (86400 seconds)
LOG_FILE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters for summary
TOTAL_OPERATIONS=0
SUCCESSFUL_OPERATIONS=0
FAILED_OPERATIONS=0

# Function to log with timestamp
log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} - ${message}"
    if [ -n "$LOG_FILE" ]; then
        echo "${timestamp} - ${message}" | sed 's/\x1b\[[0-9;]*m//g' >> "$LOG_FILE"
    fi
}

# Function to copy with error handling
safe_copy() {
    local source="$1"
    local destination="$2"
    local description="$3"
    
    TOTAL_OPERATIONS=$((TOTAL_OPERATIONS + 1))
    
    if [ -d "$source" ] || [ -f "$source" ]; then
        if cp -r "$source" "$destination" 2>/dev/null; then
            log "${GREEN}✅ SUCCESS${NC}: $description"
            SUCCESSFUL_OPERATIONS=$((SUCCESSFUL_OPERATIONS + 1))
            return 0
        else
            log "${RED}❌ FAILED${NC}: $description - Copy operation failed"
            FAILED_OPERATIONS=$((FAILED_OPERATIONS + 1))
            return 1
        fi
    else
        log "${YELLOW}⚠️  SKIPPED${NC}: $description - Source not found: $source"
        FAILED_OPERATIONS=$((FAILED_OPERATIONS + 1))
        return 1
    fi
}

# Function to run consolidation
run_consolidation() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Starting Repository Consolidation${NC}"
    log "${GREEN}========================================${NC}"
    
    # Reset counters
    TOTAL_OPERATIONS=0
    SUCCESSFUL_OPERATIONS=0
    FAILED_OPERATIONS=0
    
    # Copy entire contents of ndax-quantum-engine
    safe_copy "source/ndax-quantum-engine/." "." "ndax-quantum-engine (full repository)"
    
    # Copy from quantum-engine-dashb
    safe_copy "source/quantum-engine-dashb/src/." "frontend/" "quantum-engine-dashb frontend"
    safe_copy "source/quantum-engine-dashb/.github/workflows/." ".github/workflows/" "quantum-engine-dashb workflows"
    
    # Copy entire contents of shadowforge-ai-trader
    safe_copy "source/shadowforge-ai-trader/." "." "shadowforge-ai-trader (full repository)"
    
    # Copy from repository-web-app
    safe_copy "source/repository-web-app/src/." "frontend/" "repository-web-app frontend"
    safe_copy "source/repository-web-app/.github/workflows/." ".github/workflows/" "repository-web-app workflows"
    
    # Add The-new-ones repository to new_additions directory
    mkdir -p new_additions
    safe_copy "source/The-new-ones/." "new_additions/" "The-new-ones to new_additions"
    
    # Print summary
    log "${GREEN}========================================${NC}"
    log "${GREEN}Consolidation Summary${NC}"
    log "${GREEN}========================================${NC}"
    log "Total operations: $TOTAL_OPERATIONS"
    log "${GREEN}Successful: $SUCCESSFUL_OPERATIONS${NC}"
    log "${RED}Failed/Skipped: $FAILED_OPERATIONS${NC}"
    
    if [ $SUCCESSFUL_OPERATIONS -gt 0 ]; then
        log "${GREEN}✅ Consolidation completed with $SUCCESSFUL_OPERATIONS successful operations${NC}"
        return 0
    else
        log "${RED}❌ Consolidation completed but all operations failed${NC}"
        return 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --continuous)
            CONTINUOUS_MODE=true
            shift
            ;;
        --interval)
            SLEEP_INTERVAL="$2"
            shift 2
            ;;
        --log-file)
            LOG_FILE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --continuous         Enable continuous run mode"
            echo "  --interval SECONDS   Set sleep interval for continuous mode (default: 86400)"
            echo "  --log-file FILE      Write logs to specified file"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                              # Run once"
            echo "  $0 --continuous                 # Run continuously with default interval"
            echo "  $0 --continuous --interval 3600 # Run every hour"
            exit 0
            ;;
        *)
            log "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
if [ "$CONTINUOUS_MODE" = true ]; then
    log "${YELLOW}Running in CONTINUOUS mode with interval: ${SLEEP_INTERVAL}s${NC}"
    
    while true; do
        run_consolidation
        log "${YELLOW}Waiting ${SLEEP_INTERVAL} seconds before next run...${NC}"
        sleep "$SLEEP_INTERVAL"
    done
else
    # Single run mode
    run_consolidation
    exit $?
fi
