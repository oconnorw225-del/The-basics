#!/bin/bash

# security-audit.sh
# Script to scan for sensitive keywords in current files and git history

set -e  # Exit on error

# Define color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Define output file
REPORT_FILE="security_audit_report.txt"

# Define sensitive keywords to search for
SENSITIVE_KEYWORDS=(
    "API_KEY"
    "SECRET"
    "PRIVATE_KEY"
    "Mnemonic"
    "PASSWORD"
    "TOKEN"
    "CREDENTIAL"
    "AWS_SECRET"
    "GITHUB_TOKEN"
    "API_SECRET"
)

echo -e "${GREEN}=== Security Audit Script ===${NC}"
echo ""

# Initialize report file
cat > "$REPORT_FILE" << EOF
╔════════════════════════════════════════════════════════════════════════╗
║                    SECURITY AUDIT REPORT                               ║
╚════════════════════════════════════════════════════════════════════════╝

Generated on: $(date)
Repository: $(git config --get remote.origin.url 2>/dev/null || echo "Unknown")
Current branch: $(git branch --show-current 2>/dev/null || echo "Unknown")

════════════════════════════════════════════════════════════════════════

EOF

echo -e "${BLUE}Scanning for sensitive keywords...${NC}"
echo "Keywords: ${SENSITIVE_KEYWORDS[*]}"
echo ""

# Section 1: Current Files Scan
echo -e "${YELLOW}[1/2] Scanning current files...${NC}"
cat >> "$REPORT_FILE" << EOF
SECTION 1: CURRENT FILES SCAN
════════════════════════════════════════════════════════════════════════

Searching for sensitive keywords in current working directory...

EOF

found_current=0

for keyword in "${SENSITIVE_KEYWORDS[@]}"; do
    echo -ne "  Searching for '$keyword'...\r"
    
    # Use grep to search for keyword in current files, excluding common directories
    if grep -rIn --exclude-dir={.git,node_modules,__pycache__,.venv,venv,dist,build} \
              --exclude="*.log" \
              --exclude="$REPORT_FILE" \
              "$keyword" . 2>/dev/null > /tmp/current_scan_$$.tmp; then
        
        echo "Found '$keyword' in current files:" >> "$REPORT_FILE"
        cat /tmp/current_scan_$$.tmp >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        count=$(wc -l < /tmp/current_scan_$$.tmp)
        echo -e "  ${RED}✗ Found '$keyword' in $count location(s)${NC}"
        found_current=$((found_current + count))
        
        rm /tmp/current_scan_$$.tmp
    fi
done

if [ $found_current -eq 0 ]; then
    echo -e "  ${GREEN}✓ No sensitive keywords found in current files${NC}"
    echo "✓ No sensitive keywords found in current files." >> "$REPORT_FILE"
else
    echo -e "  ${RED}⚠ Found $found_current potential issue(s) in current files${NC}"
    echo "" >> "$REPORT_FILE"
    echo "⚠ TOTAL: $found_current potential issue(s) found in current files" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "════════════════════════════════════════════════════════════════════════" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Section 2: Git History Scan
echo ""
echo -e "${YELLOW}[2/2] Scanning git history (including deleted files)...${NC}"
cat >> "$REPORT_FILE" << EOF
SECTION 2: GIT HISTORY SCAN (Including Deleted Files)
════════════════════════════════════════════════════════════════════════

Searching for sensitive keywords in git commit history...
This includes files that may have been committed and then deleted.

EOF

found_history=0

if [ -d .git ]; then
    for keyword in "${SENSITIVE_KEYWORDS[@]}"; do
        echo -ne "  Searching history for '$keyword'...\r"
        
        # Search git log for the keyword in all commits
        if git log --all -p -S"$keyword" --pretty=format:"%H|%an|%ae|%ad|%s" --date=iso 2>/dev/null > /tmp/history_scan_$$.tmp; then
            
            if [ -s /tmp/history_scan_$$.tmp ]; then
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$REPORT_FILE"
                echo "Keyword: '$keyword'" >> "$REPORT_FILE"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$REPORT_FILE"
                echo "" >> "$REPORT_FILE"
                
                # Parse and format the results
                while IFS='|' read -r commit author email date message; do
                    if [ -n "$commit" ]; then
                        echo "Commit: $commit" >> "$REPORT_FILE"
                        echo "Author: $author <$email>" >> "$REPORT_FILE"
                        echo "Date: $date" >> "$REPORT_FILE"
                        echo "Message: $message" >> "$REPORT_FILE"
                        echo "" >> "$REPORT_FILE"
                        
                        found_history=$((found_history + 1))
                    fi
                done < /tmp/history_scan_$$.tmp
                
                # Get the actual diff for these commits
                git log --all -p -S"$keyword" --oneline 2>/dev/null | head -100 >> "$REPORT_FILE"
                echo "" >> "$REPORT_FILE"
                
                count=$(grep -c "^Commit:" /tmp/history_scan_$$.tmp || echo 0)
                echo -e "  ${RED}⚠ Found '$keyword' in $count commit(s)${NC}"
            fi
            
            rm -f /tmp/history_scan_$$.tmp
        fi
    done
    
    if [ $found_history -eq 0 ]; then
        echo -e "  ${GREEN}✓ No sensitive keywords found in git history${NC}"
        echo "✓ No sensitive keywords found in git history." >> "$REPORT_FILE"
    else
        echo -e "  ${RED}⚠ Found references in $found_history commit(s)${NC}"
        echo "" >> "$REPORT_FILE"
        echo "⚠ TOTAL: Found references in $found_history commit(s)" >> "$REPORT_FILE"
    fi
else
    echo -e "  ${YELLOW}⚠ Not a git repository, skipping history scan${NC}"
    echo "⚠ Not a git repository, skipping history scan." >> "$REPORT_FILE"
fi

# Summary
echo "" >> "$REPORT_FILE"
echo "════════════════════════════════════════════════════════════════════════" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
cat >> "$REPORT_FILE" << EOF
SUMMARY
════════════════════════════════════════════════════════════════════════

Current Files Issues: $found_current
Git History References: $found_history

EOF

if [ $found_current -gt 0 ] || [ $found_history -gt 0 ]; then
    cat >> "$REPORT_FILE" << EOF
⚠ RECOMMENDATION:
  - Review all findings above carefully
  - Remove any sensitive data from current files
  - If secrets were committed to history, consider rotating those credentials
  - Use environment variables or secret management tools for sensitive data
  - Consider using tools like 'git-filter-branch' or 'BFG Repo-Cleaner' to
    remove sensitive data from git history if necessary

EOF
else
    cat >> "$REPORT_FILE" << EOF
✓ RESULT: No obvious sensitive keywords found in current files or git history.

Note: This is a basic scan and may not catch all security issues.
Always follow security best practices and never commit sensitive data.

EOF
fi

cat >> "$REPORT_FILE" << EOF
════════════════════════════════════════════════════════════════════════
End of Report
════════════════════════════════════════════════════════════════════════
EOF

# Display results
echo ""
echo -e "${GREEN}=== Security Audit Complete ===${NC}"
echo -e "${GREEN}Report generated: $REPORT_FILE${NC}"
echo ""

if [ $found_current -gt 0 ] || [ $found_history -gt 0 ]; then
    echo -e "${RED}⚠ SECURITY ALERT: Potential sensitive data found!${NC}"
    echo -e "${YELLOW}Please review $REPORT_FILE for details.${NC}"
else
    echo -e "${GREEN}✓ No obvious security issues detected.${NC}"
fi

echo ""
