#!/bin/bash
# Script to delete redundant and lesser functionality branches
# NOTE: This script should be run by a user with appropriate GitHub permissions

echo "=== Deleting Redundant and Lesser Functionality Branches ==="
echo ""
echo "This will delete the following branches from the remote repository:"
echo ""

# Define branches to delete
REDUNDANT_BRANCHES=(
    # Redundant merge/cleanup branches
    "consolidate/no-clone"
    "copilot/cleanup-and-merge-branches"
    "copilot/merge-all-changes"
    "copilot/merge-feature-branches-into-main"
    "copilot/remove-copilot-branches"
    # Redundant setup branches
    "copilot/setup-codespace-structure"
    "copilot/setup-directory-structure"
    "copilot/setup-github-pages-status"
    "copilot/setup-repo-structure"
    # Redundant fix branches
    "copilot/fix-clone-repo-issue"
    "copilot/fix-railpack-error"
    "copilot/fix-unexpected-token-error"
    "copilot/fix-unexpected-token-error-again"
    # Other redundant branches
    "copilot/resolve-issue"
    "oconnorw225-del-patch-1"
    # Branches already merged into enhance-synchronization-and-integration
    "copilot/add-apis-to-repo"
    "copilot/add-complete-codebase"
    "copilot/add-may-atonamus-solvency-data"
    "copilot/add-quantum-dashboard-frontend"
    "copilot/integrate-related-repositories"
    "copilot/optimize-synchronization-automation"
    "copilot/prepare-deployment-for-rainway"
    "copilot/start-paper-and-live-trading"
    "copilot/update-authentication-workflow"
    "copilot/update-consolidation-script"
)

# List branches to be deleted
for branch in "${REDUNDANT_BRANCHES[@]}"; do
    echo "  - $branch"
done

echo ""
read -p "Are you sure you want to delete these branches? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Deletion cancelled."
    exit 0
fi

echo ""
echo "Deleting branches..."

# Delete each branch
for branch in "${REDUNDANT_BRANCHES[@]}"; do
    echo "Deleting: $branch"
    git push origin --delete "$branch" 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ Successfully deleted $branch"
    else
        echo "  ✗ Failed to delete $branch"
    fi
done

echo ""
echo "Branch deletion complete!"
echo ""
echo "Remaining branches with new functionality have been preserved."
