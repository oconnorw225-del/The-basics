#!/bin/bash

# Security Audit Script
# Scans project aggregation directory for sensitive information
# in both current files and git history

set -e  # Exit on error

# Define paths
AGGREGATION_DIR="project_aggregation"
REPORT_FILE="security_audit_report.txt"

# Define sensitive keywords and patterns
KEYWORDS=(
    "API_KEY"
    "SECRET"
    "PASSWORD"
    "PRIVATE_KEY"
    "Mnemonic"
    "SeedPhrase"
)

# Define regex patterns for crypto addresses
ETH_PATTERN="0x[a-fA-F0-9]{40}"
BECH32_PATTERN="bc1[a-zA-Z0-9]{25,39}"

echo "=========================================="
echo "Security Audit Script"
echo "=========================================="
echo ""

# Check if aggregation directory exists
if [ ! -d "$AGGREGATION_DIR" ]; then
    echo "Error: Aggregation directory '$AGGREGATION_DIR' does not exist."
    echo "Please run aggregate-projects.sh first."
    exit 1
fi

# Initialize report file
echo "Security Audit Report" > "$REPORT_FILE"
echo "=====================" >> "$REPORT_FILE"
echo "Generated: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "Starting security audit..."
echo ""

# Section 1: Scan current files
echo "1. Scanning current files for sensitive keywords..." | tee -a "$REPORT_FILE"
echo "=================================================" | tee -a "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for keyword in "${KEYWORDS[@]}"; do
    echo "  Searching for: $keyword"
    echo "### Keyword: $keyword" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # Search for keyword in current files, excluding .git and node_modules
    grep -r -i -n "$keyword" "$AGGREGATION_DIR" \
        --exclude-dir=.git \
        --exclude-dir=node_modules \
        --exclude-dir=dist \
        --exclude-dir=build \
        --exclude="*.log" \
        2>/dev/null | head -100 >> "$REPORT_FILE" || echo "  No matches found for $keyword" >> "$REPORT_FILE"
    
    echo "" >> "$REPORT_FILE"
done

# Scan for Ethereum addresses
echo "  Searching for: Ethereum addresses (0x...)"
echo "### Pattern: Ethereum Address ($ETH_PATTERN)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

grep -r -E -n "$ETH_PATTERN" "$AGGREGATION_DIR" \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=dist \
    --exclude-dir=build \
    --exclude="*.log" \
    2>/dev/null | head -100 >> "$REPORT_FILE" || echo "  No Ethereum addresses found" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"

# Scan for Bech32 addresses
echo "  Searching for: Bitcoin Bech32 addresses (bc1...)"
echo "### Pattern: Bitcoin Bech32 Address ($BECH32_PATTERN)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

grep -r -E -n "$BECH32_PATTERN" "$AGGREGATION_DIR" \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=dist \
    --exclude-dir=build \
    --exclude="*.log" \
    2>/dev/null | head -100 >> "$REPORT_FILE" || echo "  No Bech32 addresses found" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Section 2: Scan git history
echo "" | tee -a "$REPORT_FILE"
echo "2. Scanning Git History for sensitive keywords..." | tee -a "$REPORT_FILE"
echo "=================================================" | tee -a "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Get absolute path for report file
REPORT_FILE_ABS="$(pwd)/$REPORT_FILE"

# Find all git repositories in aggregation directory
find "$AGGREGATION_DIR" -name ".git" -type d | while read -r git_dir; do
    repo_path=$(dirname "$git_dir")
    repo_name=$(basename "$repo_path")
    
    echo "  Scanning repository: $repo_name"
    echo "### Repository: $repo_name" >> "$REPORT_FILE_ABS"
    echo "" >> "$REPORT_FILE_ABS"
    
    # Change to repo directory
    pushd "$repo_path" > /dev/null
    
    # Get git log output once for efficiency
    # Note: Limiting to first 10000 lines to manage memory usage for large repositories
    echo "    Fetching git history..."
    git_log_output=$(git log --all -p --max-count=500 2>/dev/null || echo "")
    
    # Scan for each keyword in git history
    for keyword in "${KEYWORDS[@]}"; do
        echo "    Searching git history for: $keyword"
        echo "#### Keyword: $keyword" >> "$REPORT_FILE_ABS"
        
        # Search git log output for keyword
        echo "$git_log_output" | grep -i -n "$keyword" | head -20 >> "$REPORT_FILE_ABS" 2>/dev/null || echo "No matches found" >> "$REPORT_FILE_ABS"
        
        echo "" >> "$REPORT_FILE_ABS"
    done
    
    # Scan for Ethereum addresses in git history
    echo "    Searching git history for: Ethereum addresses"
    echo "#### Pattern: Ethereum Address" >> "$REPORT_FILE_ABS"
    
    echo "$git_log_output" | grep -E -n "$ETH_PATTERN" | head -20 >> "$REPORT_FILE_ABS" 2>/dev/null || echo "No matches found" >> "$REPORT_FILE_ABS"
    echo "" >> "$REPORT_FILE_ABS"
    
    # Scan for Bech32 addresses in git history
    echo "    Searching git history for: Bitcoin Bech32 addresses"
    echo "#### Pattern: Bitcoin Bech32 Address" >> "$REPORT_FILE_ABS"
    
    echo "$git_log_output" | grep -E -n "$BECH32_PATTERN" | head -20 >> "$REPORT_FILE_ABS" 2>/dev/null || echo "No matches found" >> "$REPORT_FILE_ABS"
    echo "" >> "$REPORT_FILE_ABS"
    
    echo "---" >> "$REPORT_FILE_ABS"
    echo "" >> "$REPORT_FILE_ABS"
    
    # Return to previous directory
    popd > /dev/null
done

# Summary
echo "" >> "$REPORT_FILE"
echo "=========================================" >> "$REPORT_FILE"
echo "Audit Complete" >> "$REPORT_FILE"
echo "=========================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Please review the findings above and take appropriate action" >> "$REPORT_FILE"
echo "to secure any exposed credentials or sensitive information." >> "$REPORT_FILE"

echo ""
echo "=========================================="
echo "Security audit complete!"
echo "Report file: $REPORT_FILE"
echo "=========================================="
echo ""
echo "Please review the report for any security concerns."
