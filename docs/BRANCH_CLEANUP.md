# Branch Cleanup Documentation

## Overview

This document explains the Copilot branches in this repository and the cleanup strategy.

## What are Copilot Branches?

Copilot branches are automatically created by GitHub Copilot when making code changes through the Copilot interface. Each Copilot session creates a new branch with the naming pattern `copilot/<task-description>`.

## Current Copilot Branches

As of the cleanup date, the following Copilot branches existed:

1. `copilot/add-apis-to-repo`
2. `copilot/add-complete-codebase`
3. `copilot/add-may-atonamus-solvency-data`
4. `copilot/cleanup-and-merge-branches`
5. `copilot/enhance-synchronization-and-integration`
6. `copilot/fix-clone-repo-issue`
7. `copilot/fix-railpack-error`
8. `copilot/fix-unexpected-token-error`
9. `copilot/fix-unexpected-token-error-again`
10. `copilot/integrate-related-repositories`
11. `copilot/merge-all-changes`
12. `copilot/optimize-synchronization-automation`
13. `copilot/prepare-deployment-for-rainway`
14. `copilot/remove-copilot-branches` (current cleanup branch)
15. `copilot/resolve-issue`
16. `copilot/setup-codespace-structure`
17. `copilot/setup-directory-structure`
18. `copilot/setup-github-pages-status`
19. `copilot/setup-repo-structure`
20. `copilot/update-authentication-workflow`
21. `copilot/update-consolidation-script`

## Are These Branches Relevant to the Build?

**No.** The CI workflow (`blank.yml`) only runs on the `main` branch for:
- Push events to main
- Pull requests to main
- Manual workflow dispatch

These Copilot branches do not affect the build process unless they are merged into main.

## Cleanup Strategy

### Why Clean Up?

- **Repository cleanliness**: Too many stale branches make the repository harder to navigate
- **Performance**: Reduces the size of repository metadata
- **Clarity**: Makes it easier to identify active development branches

### What Gets Deleted?

The cleanup script uses the following criteria:

1. **Merged branches**: Copilot branches that have been successfully merged into main
2. **Stale branches**: Branches with no commits in the last 30 days (configurable)

### What Gets Kept?

- The `main` branch (protected)
- Active development branches (updated within 30 days)
- The current cleanup branch until merged
- Any branch explicitly in the protected list

## Cleanup Process

The cleanup is performed by the script `automation/cleanup-branches.sh` which:

1. Lists all remote Copilot branches
2. Checks each branch's merge status and last commit date
3. Marks branches for deletion if they are:
   - Already merged into main, OR
   - Haven't been updated in more than 30 days (configurable)
4. Deletes marked branches (unless in dry-run mode)
5. Provides a detailed summary of actions taken

### Configuration Options

- `DRY_RUN`: Set to `true` to see what would be deleted without actually deleting (default: `true`)
- `STALE_DAYS`: Number of days of inactivity before a branch is considered stale (default: `30`)

**Examples:**

```bash
# Dry run with default 30 day threshold
DRY_RUN=true bash automation/cleanup-branches.sh

# Actually delete branches older than 60 days
STALE_DAYS=60 DRY_RUN=false bash automation/cleanup-branches.sh

# More aggressive cleanup - delete branches older than 14 days
STALE_DAYS=14 DRY_RUN=false bash automation/cleanup-branches.sh
```

## Future Branch Management

**Best Practices:**
1. Merge Copilot branches into main via Pull Requests
2. Delete branches after merging
3. Run periodic cleanup (recommended: monthly)
4. Use descriptive branch names for manual branches

## Manual Cleanup Commands

If you need to manually delete a specific Copilot branch:

```bash
# Delete remote branch
git push origin --delete copilot/<branch-name>

# Delete local tracking reference
git fetch --prune
```

To delete all merged Copilot branches at once:

```bash
# Use the cleanup script
bash automation/cleanup-branches.sh
```
