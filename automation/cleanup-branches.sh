#!/bin/bash

# cleanup-branches.sh
# Script to clean up old Copilot branches from the repository

set -e

echo "=========================================="
echo "Copilot Branch Cleanup Script"
echo "=========================================="
echo ""

# Configuration
PROTECTED_BRANCHES=("main" "copilot/remove-copilot-branches")
DRY_RUN=${DRY_RUN:-true}
# Days since last commit to consider a branch stale
STALE_DAYS=${STALE_DAYS:-30}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if branch is protected
is_protected() {
    local branch=$1
    for protected in "${PROTECTED_BRANCHES[@]}"; do
        if [[ "$branch" == "$protected" ]]; then
            return 0
        fi
    done
    return 1
}

# Function to get days since last commit on a branch
days_since_last_commit() {
    local branch=$1
    local last_commit_date=$(git log -1 --format=%ct "origin/$branch" 2>/dev/null)
    
    # If git log fails or returns nothing, skip this branch (don't delete unknown branches)
    if [ -z "$last_commit_date" ]; then
        echo "-1"  # Return -1 to indicate error
        return
    fi
    
    local current_date=$(date +%s)
    local days_diff=$(( (current_date - last_commit_date) / 86400 ))
    echo $days_diff
}

# Function to check if branch is merged into main (best effort with shallow clones)
is_merged() {
    local branch=$1
    # Try to check if branch is merged
    if git fetch origin main >/dev/null 2>&1; then
        if git merge-base --is-ancestor "origin/$branch" origin/main 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

echo "Fetching remote branches..."
git fetch --all --prune >/dev/null 2>&1

echo ""
echo "Analyzing Copilot branches..."
echo "  Branches older than ${STALE_DAYS} days will be marked for deletion"
echo ""

# Arrays to track branches
declare -a branches_to_delete
declare -a branches_merged
declare -a branches_stale
declare -a branches_active
declare -a branches_protected

# Get all copilot branches except the current cleanup branch
while IFS= read -r ref; do
    branch=$(echo "$ref" | sed 's|refs/heads/||')
    
    # Skip if protected
    if is_protected "$branch"; then
        branches_protected+=("$branch")
        continue
    fi
    
    # Check if merged
    if is_merged "$branch"; then
        branches_merged+=("$branch")
        branches_to_delete+=("$branch")
        echo -e "${GREEN}✓${NC} $branch (merged into main)"
        continue
    fi
    
    # Check if stale (not updated in STALE_DAYS days)
    days_old=$(days_since_last_commit "$branch")
    
    # Skip if we couldn't determine the age (error case)
    if [ $days_old -eq -1 ]; then
        echo -e "${RED}⚠${NC} $branch (unable to determine age - keeping for safety)"
        branches_active+=("$branch")
        continue
    fi
    
    if [ $days_old -gt $STALE_DAYS ]; then
        branches_stale+=("$branch")
        branches_to_delete+=("$branch")
        echo -e "${YELLOW}⏰${NC} $branch (${days_old} days old - stale)"
    else
        branches_active+=("$branch")
        echo -e "${BLUE}ℹ${NC} $branch (${days_old} days old - active, keeping)"
    fi
done < <(git ls-remote --heads origin | grep 'refs/heads/copilot/' | awk '{print $2}')

# Display summary
echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}Protected branches: ${#branches_protected[@]}${NC}"
for branch in "${branches_protected[@]}"; do
    echo -e "  ${GREEN}✓${NC} $branch"
done

echo ""
echo -e "${GREEN}Merged branches (safe to delete): ${#branches_merged[@]}${NC}"
for branch in "${branches_merged[@]}"; do
    echo -e "  ${GREEN}✓${NC} $branch"
done

echo ""
echo -e "${YELLOW}Stale branches (>$STALE_DAYS days, will delete): ${#branches_stale[@]}${NC}"
for branch in "${branches_stale[@]}"; do
    echo -e "  ${YELLOW}⏰${NC} $branch"
done

echo ""
echo -e "${BLUE}Active branches (keeping): ${#branches_active[@]}${NC}"
for branch in "${branches_active[@]}"; do
    echo -e "  ${BLUE}ℹ${NC} $branch"
done

echo ""
echo "=========================================="
echo -e "Total branches to delete: ${RED}${#branches_to_delete[@]}${NC}"
echo "=========================================="

# Perform deletion
if [ ${#branches_to_delete[@]} -eq 0 ]; then
    echo ""
    echo -e "${GREEN}No branches to delete. Repository is clean!${NC}"
    exit 0
fi

echo ""
if [ "$DRY_RUN" = "true" ]; then
    echo -e "${YELLOW}DRY RUN MODE - No branches will be deleted${NC}"
    echo ""
    echo "Branches that would be deleted:"
    for branch in "${branches_to_delete[@]}"; do
        echo "  - $branch"
    done
    echo ""
    echo "To actually delete these branches, run:"
    echo "  DRY_RUN=false bash automation/cleanup-branches.sh"
    echo ""
    echo "To adjust the staleness threshold (default 30 days):"
    echo "  STALE_DAYS=60 DRY_RUN=false bash automation/cleanup-branches.sh"
else
    echo -e "${RED}WARNING: This will delete ${#branches_to_delete[@]} remote branches!${NC}"
    echo ""
    
    # Delete branches
    echo "Deleting branches..."
    deleted=0
    failed=0
    
    for branch in "${branches_to_delete[@]}"; do
        echo -n "  Deleting $branch... "
        if git push origin --delete "$branch" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ deleted${NC}"
            ((deleted++))
        else
            echo -e "${RED}✗ failed${NC}"
            ((failed++))
        fi
    done
    
    echo ""
    echo "Results:"
    echo -e "  ${GREEN}Deleted: $deleted${NC}"
    if [ $failed -gt 0 ]; then
        echo -e "  ${RED}Failed: $failed${NC}"
    fi
fi

echo ""
echo "=========================================="
echo "Cleanup complete!"
echo "=========================================="
