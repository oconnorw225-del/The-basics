# Cleanup Stale Branches Workflow

## Overview

The **Cleanup Stale Branches** GitHub Action workflow automates the deletion of specific stale branches listed in the `DELETE_BRANCHES.sh` file, eliminating the need for manual branch cleanup.

## Location

- **Workflow File**: `.github/workflows/cleanup-stale-branches.yml`
- **Branch List Source**: `DELETE_BRANCHES.sh`
- **Documentation**: `docs/BRANCH_CLEANUP.md`

## How to Use

### Step 1: Navigate to the Workflow

1. Go to the repository on GitHub
2. Click on the **Actions** tab
3. Select **Cleanup Stale Branches** from the workflow list

### Step 2: Run the Workflow

1. Click the **Run workflow** button
2. Configure the inputs:

   - **Dry run mode**: 
     - `true` (default): Preview what would be deleted without making changes
     - `false`: Allow actual deletion (requires confirm_deletion=true)
   
   - **Confirm deletion**: 
     - `false` (default): Safety check prevents deletion
     - `true`: Required along with dry_run=false to actually delete branches

3. Click **Run workflow** to start

### Step 3: Review Results

After the workflow completes:

1. Click on the workflow run to view details
2. Check the **Summary** tab for:
   - Configuration used
   - Branches found vs. already deleted
   - Protected branches (never deleted)
   - Deletion results and statistics
3. Review the job logs for detailed information

## Usage Scenarios

### Scenario 1: Preview (Dry Run)

**Default behavior** - See what would be deleted without making changes:

```
Inputs:
  dry_run: true (default)
  confirm_deletion: false (default)
```

**Result**: Lists all branches that would be deleted, no actual deletions occur.

### Scenario 2: Actually Delete Branches

To actually delete the stale branches:

```
Inputs:
  dry_run: false
  confirm_deletion: true
```

**Result**: Branches are deleted from the remote repository.

### Scenario 3: Safety Test

Attempting to delete with only one safety check:

```
Inputs:
  dry_run: false
  confirm_deletion: false
```

**Result**: No branches deleted - both safety checks must pass.

## Safety Features

1. **Dual Confirmation Required**: 
   - Both `dry_run=false` AND `confirm_deletion=true` must be set to delete branches

2. **Dry-run by Default**: 
   - Always defaults to preview mode

3. **Protected Branches**: 
   - `main` and `master` branches are never deleted

4. **Graceful Error Handling**: 
   - Missing branches don't fail the workflow
   - Each branch deletion is independent

5. **Comprehensive Logging**: 
   - Detailed output of all actions taken
   - Clear indication of success/failure for each branch

## Branches Targeted for Deletion

The workflow targets the following 29 specific branches:

**Redundant Merge/Cleanup Branches:**
- consolidate/no-clone
- copilot/cleanup-and-merge-branches
- copilot/merge-all-changes
- copilot/merge-feature-branches-into-main
- copilot/remove-copilot-branches

**Redundant Setup Branches:**
- copilot/setup-codespace-structure
- copilot/setup-directory-structure
- copilot/setup-github-pages-status
- copilot/setup-repo-structure

**Redundant Fix Branches:**
- copilot/fix-clone-repo-issue
- copilot/fix-railpack-error
- copilot/fix-unexpected-token-error
- copilot/fix-unexpected-token-error-again

**Other Redundant Branches:**
- copilot/resolve-issue
- oconnorw225-del-patch-1

**Consolidated Branches:**
- copilot/add-apis-to-repo
- copilot/add-complete-codebase
- copilot/add-may-atonamus-solvency-data
- copilot/add-quantum-dashboard-frontend
- copilot/integrate-related-repositories
- copilot/optimize-synchronization-automation
- copilot/prepare-deployment-for-rainway
- copilot/start-paper-and-live-trading
- copilot/update-authentication-workflow
- copilot/update-consolidation-script
- copilot/consolidate-repository-scripts
- copilot/enhance-synchronization-and-integration
- copilot/merge-unmerged-branches

**Dependabot Branches:**
- dependabot/npm_and_yarn/npm_and_yarn-92f289d509

## Workflow Output

The workflow provides detailed output including:

### Summary Statistics
- Total branches in deletion list
- Branches found on remote
- Branches already deleted
- Branches protected

### Detailed Lists
- Branches ready for deletion
- Branches already deleted (expandable)
- Protected branches (expandable)

### Deletion Results (when not in dry-run)
- Successfully deleted branches
- Failed deletions with reasons
- Summary counts

## Permissions

The workflow requires:
- `contents: write` - To delete remote branches

This is automatically provided by the `GITHUB_TOKEN`.

## Troubleshooting

### Workflow Won't Delete Branches

**Check:**
1. Both `dry_run` is set to `false`
2. Both `confirm_deletion` is set to `true`
3. You have write permissions to the repository

### Branch Deletion Failed

**Possible Reasons:**
1. Branch is protected by repository rules
2. Branch has already been deleted
3. Insufficient permissions
4. Network/GitHub API issues

**Solution:** Check the workflow logs for specific error messages.

### Can't Find the Workflow

**Check:**
1. The workflow file exists at `.github/workflows/cleanup-stale-branches.yml`
2. You're looking in the **Actions** tab of the correct repository
3. You have at least read access to the repository

## Related Files

- **Workflow**: `.github/workflows/cleanup-stale-branches.yml`
- **Branch List**: `DELETE_BRANCHES.sh`
- **Documentation**: `docs/BRANCH_CLEANUP.md`
- **Alternative Cleanup**: `automation/cleanup-branches.sh` (dynamic, criteria-based cleanup)

## Comparison with Other Cleanup Methods

### This Workflow vs. DELETE_BRANCHES.sh Script

| Feature | Workflow | Script |
|---------|----------|--------|
| Execution | GitHub UI | Command line |
| Branch selection | Fixed list | Fixed list |
| Dry-run default | Yes | Yes |
| Safety checks | Dual (dry_run + confirm) | Single (yes/no) |
| Detailed reporting | GitHub Actions summary | Console output |
| Automation ready | Yes | Manual |

### This Workflow vs. automation/cleanup-branches.sh

| Feature | Cleanup Stale Branches | Dynamic Cleanup |
|---------|----------------------|-----------------|
| Branch selection | Fixed list (29 branches) | Dynamic (copilot/* branches) |
| Criteria | Specific branches | Merged or stale (30+ days) |
| Configuration | Workflow inputs | Environment variables |
| Use case | One-time cleanup | Regular maintenance |

## Best Practices

1. **Always start with dry-run**: Review what will be deleted before proceeding
2. **Check branch status first**: Ensure branches are truly no longer needed
3. **Document deletions**: Keep notes on why branches were removed
4. **Regular cleanup**: Run periodically to keep repository clean
5. **Backup important work**: Ensure all valuable work is merged to main before cleanup

## Support

For issues or questions:
1. Check the workflow logs for detailed error messages
2. Review the `docs/BRANCH_CLEANUP.md` documentation
3. Open an issue in the repository

## Version History

- **v1.0** (2025-12-12): Initial release with 29 stale branches
