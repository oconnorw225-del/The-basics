# Security Audit Guide (Read-Only)

This PR adds safe tooling to aggregate your repositories and produce read-only secret scans. IMPORTANT: These tools are intentionally read-only and will not exfiltrate secrets or perform any cryptocurrency or financial operations.

## What was added
- `automation/aggregate-projects.sh` — clones or updates a configurable list of repositories into `project_aggregation/`.
- `automation/security-audit.sh` — runs `gitleaks` on each cloned repository and the current repo; outputs reports to `reports/`.
- `.github/workflows/run-secret-scan.yml` — a workflow that runs the aggregation and the security audit and uploads the reports as artifacts.

## How to run locally
1. Clone this repository locally.
2. Make the scripts executable: `chmod +x automation/*.sh`
3. Run `./automation/aggregate-projects.sh` to clone/update repos.
4. Run `./automation/security-audit.sh` to generate `reports/` with findings.

## Scanning private repositories
If you need the workflow to scan private repositories during the GitHub Action run, create a repository secret named `GITHUB_PAT` with a minimal PAT that has `repo` scope for the target private repos. Add this secret in: Settings → Secrets and variables → Actions → New repository secret.

**Do not** paste PATs or private keys into issues, PRs, or chat. Only add secrets through GitHub repository settings.

## Handling findings
1. Treat any secret or private key found as COMPROMISED.
2. Immediately rotate or revoke exposed credentials via the vendor's dashboard.
3. If private keys/seed phrases are found, assume they are compromised; create new wallets and manually move funds using hardware wallets or secure software wallets.
4. Remove secrets from git history using `git filter-repo` (recommended) or BFG. Example using `git filter-repo`:

```bash
# Mirror clone
git clone --mirror git@github.com:owner/repo.git
cd repo.git
# Remove files or patterns (customize)
git filter-repo --invert-paths --path filename_or_pattern
# Push cleaned history
git push --force --all
```

5. Add `.gitignore` entries to prevent future leaks, and store secrets only in a secret manager.

## Important notes
- These tools will NOT transfer funds or retrieve private keys. They are auditing utilities only.
- Do not commit `reports/` to the repository if they contain sensitive findings. Download and store them securely instead.
