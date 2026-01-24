#!/bin/bash
set -euo pipefail

# Project Aggregation and Summary Tool
# Clones or updates a list of repositories into a local 'project_aggregation' folder.
# NOTE: If you need to clone private repos, set GITHUB_PAT in the environment to a PAT with minimal scope.

WORKDIR="project_aggregation"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

# Repositories to aggregate. Edit this list as needed.
REPOS=(
  "https://github.com/oconnorw225-del/ndax-quantum-engine.git"
  "https://github.com/oconnorw225-del/The-basics.git"
  "https://github.com/oconnorw225-del/The-new-ones.git"
  "https://github.com/oconnorw225-del/Cons_path-.git"
  "https://github.com/oconnorw225-del/shadowforge-ai-trader.git"
  "https://github.com/oconnorw225-del/quantum-engine-dashb.git"
  "https://github.com/oconnorw225-del/Cons_path.git"
  "https://github.com/oconnorw225-del/repository-web-app.git"
  "https://github.com/oconnorw225-del/Trader-bot-.git"
)

# Helper to clone or update
clone_or_update() {
  local url="$1"
  local name
  name=$(basename "$url" .git)
  if [ -d "$name" ]; then
    echo "Updating $name..."
    (cd "$name" && git pull --ff-only || true)
  else
    echo "Cloning $name..."
    if [ -n "${GITHUB_PAT-}" ]; then
      # Use PAT for private repo access if set
      auth_url=$(echo "$url" | sed -E "s#https://#https://${GITHUB_PAT}@#")
      git clone "$auth_url"
      # remove credentials from the remote after cloning
      (cd "$name" && git remote set-url origin "$(echo $url)")
    else
      git clone "$url"
    fi
  fi
}

for repo in "${REPOS[@]}"; do
  clone_or_update "$repo"
done

# Generate a short summary file
SUMMARY_FILE="project_summary.md"
echo "# Project Portfolio Summary" > "$SUMMARY_FILE"
echo "Generated on: $(date)" >> "$SUMMARY_FILE"

echo "\n## Repositories\n" >> "$SUMMARY_FILE"
for repo in "${REPOS[@]}"; do
  name=$(basename "$repo" .git)
  echo "Processing $name..."
  echo "### $name" >> "$SUMMARY_FILE"
  echo '```' >> "$SUMMARY_FILE"
  if [ -d "$name" ]; then
    tree -L 2 "$name" -I '.git|node_modules|dist|build' >> "$SUMMARY_FILE" || ls -la "$name" >> "$SUMMARY_FILE"
  else
    echo "(not present)" >> "$SUMMARY_FILE"
  fi
  echo '```' >> "$SUMMARY_FILE"
  echo "" >> "$SUMMARY_FILE"
done

echo "Aggregation complete. Summary at: $(pwd)/$SUMMARY_FILE"
