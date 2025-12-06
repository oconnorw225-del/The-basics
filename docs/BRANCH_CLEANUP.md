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

- Copilot branches that have been merged into main
- Copilot branches that are older than 30 days and haven't been updated
- Copilot branches that address issues already resolved

### What Gets Kept?

- The `main` branch (protected)
- Active development branches
- The current cleanup branch until merged

## Cleanup Process

The cleanup is performed by the script `automation/cleanup-branches.sh` which:

1. Lists all remote Copilot branches
2. Checks each branch's merge status and last update time
3. Deletes branches that meet the cleanup criteria
4. Provides a summary of deleted branches

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
