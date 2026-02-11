#!/bin/bash
# Restore workflow configurations
# Re-enables critical workflows that may have been disabled

set -e

echo "🔄 Restoring workflow configurations..."

WORKFLOW_DIR=".github/workflows"

# Function to re-enable workflows
restore_workflow() {
    local disabled_file="$1"
    local enabled_file="${disabled_file%.disabled}"
    
    if [ -f "$disabled_file" ]; then
        echo "  ✓ Re-enabling: $(basename $enabled_file)"
        cp "$disabled_file" "$enabled_file"
    fi
}

# Check if workflow directory exists
if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "  ⚠ Workflow directory not found: $WORKFLOW_DIR"
    exit 0
fi

cd "$WORKFLOW_DIR"

# Count disabled workflows using glob pattern
shopt -s nullglob
disabled_files=(*.disabled)
DISABLED_COUNT=${#disabled_files[@]}

if [ "$DISABLED_COUNT" -eq 0 ]; then
    echo "  ℹ No disabled workflows found"
    exit 0
fi

echo "  Found $DISABLED_COUNT disabled workflows"

# Re-enable critical workflows only (not all)
# unified-system.yml - Main system deployment
if [ -f "unified-system.yml.disabled" ]; then
    echo "  ⚠ Found disabled unified-system workflow (keeping disabled for safety)"
    echo "  To enable, manually remove .disabled extension after review"
fi

# Other workflows can be listed here if needed

echo "✓ Workflow restoration completed"
echo ""
echo "Note: Critical workflows remain disabled for safety."
echo "Review and manually enable workflows as needed."
