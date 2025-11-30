# the-basics

Automated consolidation of best parts from:
- ndax-quantum-engine
- quantum-engine-dashb
- shadowforge-ai-trader
- repository-web-app
- The-new-ones

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
#!/bin/bash
# Codespace setup script for 'the-basics' GitHub repo

set -e

# In a Codespace, we are already inside the repository directory.
# This script will create the necessary structure and files.

echo "Creating directory structure..."
mkdir -p ./api ./backend ./frontend ./docs ./tests ./automation ./.github/workflows

# --- Create automation script ---
echo "Creating consolidation script..."
cat <<'EOF' > ./automation/consolidate.sh
#!/bin/bash
cp -r source/ndax-quantum-engine/api/* api/ 2>/dev/null || true
cp -r source/quantum-engine-dashb/src/* frontend/ 2>/dev/null || true
cp -r source/shadowforge-ai-trader/strategy/* backend/ 2>/dev/null || true
cp -r source/repository-web-app/src/* frontend/ 2>/dev/null || true
cp -r source/ndax-quantum-engine/docs/* docs/ 2>/dev/null || true
cp -r source/quantum-engine-dashb/.github/workflows/* workflows/ 2>/dev/null || true
cp -r source/repository-web-app/.github/workflows/* workflows/ 2>/dev/null || true
cp -r source/shadowforge-ai-trader/tests/* tests/ 2>/dev/null || true
EOF
chmod +x ./automation/consolidate.sh

# --- Create workflow file ---
echo "Creating GitHub Actions workflow..."
cat <<'EOF' > ./.github/workflows/consolidate.yml
name: Consolidate Best Parts

on:
  workflow_dispatch:

jobs:
  consolidate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout the-basics repository
        uses: actions/checkout@v4

      - name: Clone source repositories
        run: |
          mkdir source
          git clone https://github.com/oconnorw225-del/ndax-quantum-engine.git source/ndax-quantum-engine
          git clone https://github.com/oconnorw225-del/quantum-engine-dashb.git source/quantum-engine-dashb
          git clone https://github.com/oconnorw225-del/shadowforge-ai-trader.git source/shadowforge-ai-trader
          git clone https://github.com/oconnorw225-del/repository-web-app.git source/repository-web-app
          git clone https://github.com/oconnorw225-del/The-new-ones.git source/The-new-ones

      - name: Archive backups
        run: |
          mkdir backups
          tar czf backups/ndax-quantum-engine.tar.gz -C source ndax-quantum-engine
          tar czf backups/quantum-engine-dashb.tar.gz -C source quantum-engine-dashb
          tar czf backups/shadowforge-ai-trader.tar.gz -C source shadowforge-ai-trader
          tar czf backups/repository-web-app.tar.gz -C source/repository-web-app
          tar czf backups/The-new-ones.tar.gz -C source/The-new-ones

      - name: Setup directory structure
        run: |
          mkdir -p api backend frontend workflows docs automation tests

      - name: Run consolidation script
        run: |
          bash automation/consolidate.sh

      - name: Commit consolidated code
        run: |
          git config --global user.email "ci-bot@example.com"
          git config --global user.name "CI Bot"
          git add .
          git diff --staged --quiet || git commit -m "Automated consolidation of best parts"
          git push
EOF

# --- Create README file ---
echo "Creating README.md..."
cat <<'EOF' > ./README.md
# the-basics

Automated consolidation of best parts from:
- ndax-quantum-engine
- quantum-engine-dashb
- shadowforge-ai-trader
- repository-web-app
- The-new-ones

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
EOF

# --- Git operations to commit and push the files ---
echo "Adding files to Git..."
git add .

echo "Committing files..."
git commit -m "Automated initial setup of consolidation workflow"

echo "Pushing files to GitHub..."
git push origin main

echo ""
echo "✅ Setup complete! The files have been pushed to your 'the-basics' repository."
echo "You can now go to the repository's 'Actions' tab to run the workflow."
