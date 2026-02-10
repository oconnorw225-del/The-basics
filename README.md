# the-basics

Automated consolidation of best parts from:
- ndax-quantum-engine
- quantum-engine-dashb
- shadowforge-ai-trader
- repository-web-app
- The-new-ones

## How To Use

### Consolidate Code (Pull from Source Repos)

1. Go to your repository's **Actions** tab.
2. Select **Consolidate Best Parts** from the workflows list.
3. Click **Run workflow** to consolidate your code.
4. Review and use your unified repo!

### Push Changes Back to Source Repos

1. Make your changes in this consolidated repository.
2. Go to the **Actions** tab.
3. Select **Push Changes to Source Repositories** from the workflows list.
4. Click **Run workflow**.
5. Choose to push to "all" repos or specify specific repos (comma-separated).
6. The workflow will push the relevant changes back to the main branches of source repositories.

## Contents
- `/api` — consolidated APIs
- `/backend` — backend logic
- `/frontend` — UI components
- `/docs` — documentation
- `/tests` — test suites
- `/automation` — scripts for consolidation and push-back
- `/backups` — archived original sources

## File Mapping for Push-Back

When pushing back to source repositories, files are mapped as follows:

- **ndax-quantum-engine**: Gets `api/` and `backend/` content
- **quantum-engine-dashb**: Gets `frontend/` → `src/` and `workflows/` → `.github/workflows/`
- **shadowforge-ai-trader**: Gets `api/`, `backend/`, `wizzard_tools/`, and `config/` content
- **repository-web-app**: Gets `frontend/` → `src/` and `workflows/` → `.github/workflows/`
- **The-new-ones**: Gets `new_additions/` content

## Manual Push-Back (Alternative)

You can also use the push-back script manually:

```bash
# Set your GitHub Personal Access Token
export GH_PAT=your_github_token

# Push to all repositories
bash automation/push-back.sh all

# Or push to specific repositories
bash automation/push-back.sh "ndax-quantum-engine,shadowforge-ai-trader"
```
