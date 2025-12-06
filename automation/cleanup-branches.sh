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
DRY_RUN=${DRY_RUN:-false}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Function to check if branch is merged into main
is_merged() {
    local branch=$1
    # Check if the branch has been merged into main
    git fetch origin main >/dev/null 2>&1
    if git merge-base --is-ancestor "origin/$branch" origin/main 2>/dev/null; then
        return 0
    fi
    return 1
}

# Get list of all copilot branches
echo "Fetching remote branches..."
git fetch --all --prune >/dev/null 2>&1

echo ""
echo "Analyzing Copilot branches..."
echo ""

# Arrays to track branches
declare -a branches_to_delete
declare -a branches_merged
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
    else
        # For now, we'll be conservative and only delete merged branches
        echo -e "${YELLOW}INFO:${NC} Branch '$branch' is not merged - keeping it"
    fi
done < <(git ls-remote --heads origin | grep 'refs/heads/copilot/' | awk '{print $2}')

# Display summary
echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "Protected branches: ${#branches_protected[@]}"
for branch in "${branches_protected[@]}"; do
    echo -e "  ${GREEN}✓${NC} $branch"
done

echo ""
echo "Merged branches to delete: ${#branches_merged[@]}"
for branch in "${branches_merged[@]}"; do
    echo -e "  ${RED}✗${NC} $branch"
done

echo ""
echo "Total branches to delete: ${#branches_to_delete[@]}"

# Perform deletion
if [ ${#branches_to_delete[@]} -eq 0 ]; then
    echo ""
    echo -e "${GREEN}No branches to delete. Repository is clean!${NC}"
    exit 0
fi

echo ""
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}DRY RUN MODE - No branches will be deleted${NC}"
    echo "To actually delete branches, run: DRY_RUN=false bash automation/cleanup-branches.sh"
else
    echo -e "${RED}WARNING: This will delete ${#branches_to_delete[@]} remote branches!${NC}"
    echo ""
    
    # Delete branches
    echo "Deleting branches..."
    for branch in "${branches_to_delete[@]}"; do
        echo -n "  Deleting $branch... "
        if git push origin --delete "$branch" >/dev/null 2>&1; then
            echo -e "${GREEN}done${NC}"
        else
            echo -e "${RED}failed${NC}"
        fi
    done
fi

echo ""
echo "=========================================="
echo "Cleanup complete!"
echo "=========================================="
