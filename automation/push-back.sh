#!/bin/bash
set -e

# Push-back script: Distributes consolidated code back to source repositories
# This script maps consolidated files back to their original source repositories

echo "========================================"
echo "Push-back to Source Repositories Script"
echo "========================================"

# Check if GH_PAT is set
if [ -z "$GH_PAT" ]; then
  echo "ERROR: GH_PAT environment variable is not set"
  echo "Please set it with: export GH_PAT=your_github_token"
  exit 1
fi

# Get target repos from command line argument or use "all"
TARGET_REPOS="${1:-all}"
WORKSPACE_DIR="${GITHUB_WORKSPACE:-.}"
TMP_DIR="/tmp/push-back-$(date +%s)"

mkdir -p "$TMP_DIR"

echo "Target repositories: $TARGET_REPOS"
echo "Workspace directory: $WORKSPACE_DIR"
echo "Temporary directory: $TMP_DIR"
echo ""

# Function to push to a repository
push_to_repo() {
  local repo_name=$1
  local repo_url=$2
  local copy_commands=$3
  
  echo "----------------------------------------"
  echo "Processing: $repo_name"
  echo "----------------------------------------"
  
  local repo_dir="$TMP_DIR/$repo_name"
  
  # Clone the repository
  echo "Cloning $repo_name..."
  git clone "https://x-access-token:${GH_PAT}@github.com/oconnorw225-del/${repo_name}.git" "$repo_dir"
  
  cd "$repo_dir"
  
  # Checkout or create main branch
  if git rev-parse --verify main >/dev/null 2>&1; then
    git checkout main
  else
    echo "Main branch doesn't exist, creating it..."
    git checkout -b main
  fi
  
  # Execute copy commands
  echo "Copying files..."
  eval "$copy_commands"
  
  # Configure git
  git config user.email "ci-bot@example.com"
  git config user.name "CI Bot"
  
  # Commit and push if there are changes
  git add .
  
  if git diff --staged --quiet; then
    echo "No changes to push to $repo_name"
  else
    echo "Committing changes to $repo_name..."
    git commit -m "Update from consolidated repository (automated push-back)"
    
    echo "Pushing to $repo_name main branch..."
    git push origin main
    
    echo "✓ Successfully pushed to $repo_name"
  fi
  
  cd "$WORKSPACE_DIR"
  echo ""
}

# Push to ndax-quantum-engine
if [ "$TARGET_REPOS" = "all" ] || [[ "$TARGET_REPOS" == *"ndax-quantum-engine"* ]]; then
  push_to_repo "ndax-quantum-engine" \
    "https://github.com/oconnorw225-del/ndax-quantum-engine.git" \
    "cp -r $WORKSPACE_DIR/api/* . 2>/dev/null || true; cp -r $WORKSPACE_DIR/backend/* . 2>/dev/null || true"
fi

# Push to quantum-engine-dashb
if [ "$TARGET_REPOS" = "all" ] || [[ "$TARGET_REPOS" == *"quantum-engine-dashb"* ]]; then
  push_to_repo "quantum-engine-dashb" \
    "https://github.com/oconnorw225-del/quantum-engine-dashb.git" \
    "mkdir -p src .github/workflows; cp -r $WORKSPACE_DIR/frontend/* src/ 2>/dev/null || true; cp -r $WORKSPACE_DIR/workflows/* .github/workflows/ 2>/dev/null || true"
fi

# Push to shadowforge-ai-trader
if [ "$TARGET_REPOS" = "all" ] || [[ "$TARGET_REPOS" == *"shadowforge-ai-trader"* ]]; then
  push_to_repo "shadowforge-ai-trader" \
    "https://github.com/oconnorw225-del/shadowforge-ai-trader.git" \
    "cp -r $WORKSPACE_DIR/api/* . 2>/dev/null || true; cp -r $WORKSPACE_DIR/backend/* . 2>/dev/null || true; [ -d \"$WORKSPACE_DIR/wizzard_tools\" ] && cp -r $WORKSPACE_DIR/wizzard_tools/* . 2>/dev/null || true; [ -d \"$WORKSPACE_DIR/config\" ] && cp -r $WORKSPACE_DIR/config/* . 2>/dev/null || true"
fi

# Push to repository-web-app
if [ "$TARGET_REPOS" = "all" ] || [[ "$TARGET_REPOS" == *"repository-web-app"* ]]; then
  push_to_repo "repository-web-app" \
    "https://github.com/oconnorw225-del/repository-web-app.git" \
    "mkdir -p src .github/workflows; cp -r $WORKSPACE_DIR/frontend/* src/ 2>/dev/null || true; cp -r $WORKSPACE_DIR/workflows/* .github/workflows/ 2>/dev/null || true"
fi

# Push to The-new-ones
if [ "$TARGET_REPOS" = "all" ] || [[ "$TARGET_REPOS" == *"The-new-ones"* ]]; then
  push_to_repo "The-new-ones" \
    "https://github.com/oconnorw225-del/The-new-ones.git" \
    "[ -d \"$WORKSPACE_DIR/new_additions\" ] && cp -r $WORKSPACE_DIR/new_additions/* . 2>/dev/null || true"
fi

# Cleanup
echo "Cleaning up temporary directory..."
rm -rf "$TMP_DIR"

echo "========================================"
echo "Push-back completed!"
echo "========================================"
