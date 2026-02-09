#!/bin/bash
set -e  # Exit on error

# Function to copy files with error handling
copy_with_check() {
    local src="$1"
    local dest="$2"
    local desc="$3"
    
    if [ -e "$src" ]; then
        mkdir -p "$dest"
        cp -r "$src"/* "$dest"/ 2>/dev/null || true
        echo "✓ Copied $desc"
    else
        echo "⚠ Warning: $src not found, skipping $desc"
    fi
}

# Copy entire contents of ndax-quantum-engine
echo "Copying ndax-quantum-engine..."
if [ -d "source/ndax-quantum-engine" ]; then
    # Use rsync for more efficient copying (falls back to cp if rsync not available)
    if command -v rsync >/dev/null 2>&1; then
        rsync -a --exclude='.git' source/ndax-quantum-engine/ .
    else
        find source/ndax-quantum-engine -mindepth 1 -maxdepth 1 ! -name '.git' -exec cp -r {} . \;
    fi
    echo "✓ Copied ndax-quantum-engine"
else
    echo "⚠ Warning: ndax-quantum-engine not found"
fi

# Copy from quantum-engine-dashb
echo "Copying quantum-engine-dashb..."
copy_with_check "source/quantum-engine-dashb/src" "frontend/" "quantum-engine-dashb/src"
copy_with_check "source/quantum-engine-dashb/.github/workflows" "workflows/" "quantum-engine-dashb workflows"

# Copy entire contents of shadowforge-ai-trader
echo "Copying shadowforge-ai-trader..."
if [ -d "source/shadowforge-ai-trader" ]; then
    if command -v rsync >/dev/null 2>&1; then
        rsync -a --exclude='.git' source/shadowforge-ai-trader/ .
    else
        find source/shadowforge-ai-trader -mindepth 1 -maxdepth 1 ! -name '.git' -exec cp -r {} . \;
    fi
    echo "✓ Copied shadowforge-ai-trader"
else
    echo "⚠ Warning: shadowforge-ai-trader not found"
fi

# Copy from repository-web-app
echo "Copying repository-web-app..."
copy_with_check "source/repository-web-app/src" "frontend/" "repository-web-app/src"
copy_with_check "source/repository-web-app/.github/workflows" "workflows/" "repository-web-app workflows"

# Add The-new-ones repository to new_additions directory
echo "Copying The-new-ones..."
mkdir -p new_additions
copy_with_check "source/The-new-ones" "new_additions/" "The-new-ones"

echo "✓ Consolidation complete!"

# Note: wizzard_tools and config from shadowforge-ai-trader are already copied to root
# via the full repository copy above, ensuring better visibility and access
