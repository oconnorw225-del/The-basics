# the-basics

Automated consolidation of best parts from:
- ndax-quantum-engine
- quantum-engine-dashb
- shadowforge-ai-trader
- repository-web-app
- The-new-ones

## Railway Deployment 🚀

This repository is configured for automatic deployment on Railway.

### Quick Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/oconnorw225-del/The-basics)

### Configuration Files
- `railway.json` - Railway deployment configuration
- `nixpacks.toml` - Nixpacks build configuration
- `Procfile` - Process definition for web service
- `package.json` - Node.js project metadata
- `server.js` - Main application server

### Environment Variables
No environment variables required for basic deployment.

## How To Use

1. Go to your repository's **Actions** tab.
2. Select **Consolidate Best Parts** from the workflows list.
3. Click **Run workflow** to consolidate your code.
4. Review and use your unified repo!

## Contents
- `/api` — consolidated APIs
- `/backend` — backend logic
- `/frontend` — UI components
- `/docs` — documentation
- `/tests` — test suites
- `/automation` — scripts for consolidation
- `/backups` — archived original sources

## Local Development

```bash
# Start the server
npm start

# Or directly with Node.js
node server.js
```

The server will run on port 3000 by default (or PORT environment variable).

## Branch Management

### About Copilot Branches

This repository contains multiple `copilot/*` branches created by GitHub Copilot during automated development tasks. These branches:

- **Are NOT relevant to the build process** - The CI workflow only runs on the `main` branch
- Represent individual development tasks completed by Copilot
- Most have already been merged into `main` via pull requests
- Should be cleaned up periodically to keep the repository organized

### Cleaning Up Old Branches

To remove old Copilot branches that have been merged:

1. Go to the **Actions** tab in your repository
2. Select **Cleanup Copilot Branches** from the workflows list
3. Click **Run workflow**
4. Choose whether to do a dry run (default) or actually delete branches
5. Review the results

For more information, see [Branch Cleanup Documentation](docs/BRANCH_CLEANUP.md).

### Manual Cleanup

You can also use the cleanup script directly:

```bash
# Dry run (see what would be deleted)
DRY_RUN=true bash automation/cleanup-branches.sh

# Actually delete merged branches
DRY_RUN=false bash automation/cleanup-branches.sh
```
