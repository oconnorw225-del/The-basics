#!/bin/bash
# One-command initialization

REPO_NAME="the-basics"
GITHUB_USER="oconnorw225-del"

echo "🚀 Initializing The Chimera..."

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI not found. Install it from: https://cli.github.com/"
    echo "📝 Manual steps:"
    echo "   1. Create repo 'the-basics' on GitHub"
    echo "   2. Run: git init && git add . && git commit -m 'Initial Chimera setup'"
    echo "   3. Run: git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git"
    echo "   4. Run: git push -u origin main"
    exit 1
fi

# Auto-create repo if it doesn't exist
echo "🔍 Checking if repo exists..."
if ! gh repo view "$GITHUB_USER/$REPO_NAME" &>/dev/null; then
    echo "📦 Creating repository..."
    gh repo create "$GITHUB_USER/$REPO_NAME" --public --description "Automated consolidation - The Chimera Project" --confirm
fi

# Initialize and push
echo "📤 Pushing code..."
git init
git add .
git commit -m "🎯 Initial Chimera setup - Automated consolidation system\n\n- 24/7 scheduled consolidation (every 6 hours)\n- Continuous health monitoring (every 30 minutes)\n- Automated backups with retention policy\n- Smart error handling and validation\n- Self-healing architecture"

git branch -M main
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git" 2>/dev/null || git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
git push -u origin main --force
echo "✅ Repository initialized!"
echo "🌐 View at: https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
echo "🎯 Next: The workflows will run automatically!"
echo "   - Consolidation: Every 6 hours"
echo "   - Health checks: Every 30 minutes"
echo ""
echo "🔧 Manual trigger:"
echo "   gh workflow run consolidate-live.yml"
