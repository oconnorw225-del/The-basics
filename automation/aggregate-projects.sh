#!/bin/bash

# Script to aggregate multiple projects into a single directory
# and generate a summary of their structures

set -euo pipefail  # Exit on error, unset variables, and pipeline failures

# Define the aggregation directory
AGGREGATION_DIR="project_aggregation"

# List of repositories to clone
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
    "https://github.com/oconnorw225-del/stunning-funicular.git"
)

echo "=========================================="
echo "Project Aggregation Script"
echo "=========================================="
echo ""

# Create the aggregation directory if it doesn't exist
if [ ! -d "$AGGREGATION_DIR" ]; then
    echo "Creating aggregation directory: $AGGREGATION_DIR"
    mkdir -p "$AGGREGATION_DIR"
else
    echo "Aggregation directory already exists: $AGGREGATION_DIR"
fi

cd "$AGGREGATION_DIR"

# Clone or pull each repository
echo ""
echo "Cloning/Updating repositories..."
echo ""

for repo in "${REPOS[@]}"; do
    # Extract the repo name from the URL
    repo_name=$(basename "$repo" .git)
    
    echo "Processing: $repo_name"
    
    if [ -d "$repo_name" ]; then
        echo "  Repository exists, pulling latest changes..."
        cd "$repo_name"
        git pull --ff-only --quiet || echo "  Warning: Failed to pull $repo_name (may require manual merge)"
        cd ..
    else
        echo "  Cloning repository..."
        git clone --quiet "$repo" || echo "  Warning: Failed to clone $repo_name"
    fi
    
    echo "  Done."
    echo ""
done

cd ..

# Generate project summary
SUMMARY_FILE="$AGGREGATION_DIR/project_summary.md"
echo "Generating project summary..."

cat > "$SUMMARY_FILE" << 'EOF'
# Project Aggregation Summary

This file contains a directory structure overview of all aggregated projects.

---

EOF

# Add directory structure for each repository
for repo in "${REPOS[@]}"; do
    repo_name=$(basename "$repo" .git)
    repo_path="$AGGREGATION_DIR/$repo_name"
    
    if [ -d "$repo_path" ]; then
        echo "## $repo_name" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        echo '```' >> "$SUMMARY_FILE"
        
        # Check if tree command is available
        if command -v tree &> /dev/null; then
            tree -I '.git|node_modules' -L 3 "$repo_path" >> "$SUMMARY_FILE" 2>/dev/null || echo "Error generating tree for $repo_name" >> "$SUMMARY_FILE"
        else
            # Fallback: use find command if tree is not available
            echo "$repo_path/" >> "$SUMMARY_FILE"
            find "$repo_path" -type d \( -name '.git' -o -name 'node_modules' \) -prune -o -type f -print | \
                sed "s|$repo_path/||" | sed 's/^/  /' | head -100 >> "$SUMMARY_FILE" 2>/dev/null || \
                echo "Error listing files for $repo_name" >> "$SUMMARY_FILE"
        fi
        
        echo '```' >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        echo "---" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
    fi
done

echo ""
echo "=========================================="
echo "Project aggregation complete!"
echo "Summary file: $SUMMARY_FILE"
echo "=========================================="
