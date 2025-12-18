#!/bin/bash
# Mega Setup for 'the-basics' GitHub repo with full automation

set -e

REPO_NAME="the-basics"

# Create structure
mkdir -p $REPO_NAME/{api,backend,frontend,docs,tests,automation,.github/workflows}

# Create automation script
cat <<'EOF' > $REPO_NAME/automation/consolidate.sh
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
chmod +x $REPO_NAME/automation/consolidate.sh

# Create workflow file
cat <<'EOF' > $REPO_NAME/.github/workflows/consolidate.yml
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

# Optional: README
cat <<'EOF' > $REPO_NAME/README.md
# the-basics

Automated consolidation of best parts from:
- ndax-quantum-engine
- quantum-engine-dashb
- shadowforge-ai-trader
- repository-web-app
- The-new-ones

## How To Use

1. Push this structure to GitHub.
2. Go to Actions > Consolidate Best Parts > Run workflow.
3. Review and use your unified repo!

## Contents
- `/api` — consolidated APIs
- `/backend` — backend logic
- `/frontend` — UI components
- `/docs` — documentation
- `/tests` — test suites
- `/automation` — scripts for consolidation
- `/backups` — archived original sources
EOF

echo "Setup complete! Now: "
echo "  1. Create a new GitHub repo named 'the-basics' (public, empty)."
echo "  2. cd the-basics; git init; git remote add origin <url>; git add .; git commit -m 'Automated setup'; git push -u origin main"
echo "  3. Go to the repo's Actions tab, select 'Consolidate Best Parts' and click 'Run workflow'."
echo "All source repos will be backed up and the best parts consolidated automatically!"
