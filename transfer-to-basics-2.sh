#!/bin/bash

# Transfer files from The-basics to basics-2 repository
# This script extracts files that would be deleted by PR #94 and prepares them for transfer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASICS_2_DIR="${BASICS_2_DIR:-../basics-2}"
EXPORT_DIR="${EXPORT_DIR:-./basics-2-export}"

echo "=========================================="
echo "Transfer Files to basics-2 Repository"
echo "=========================================="
echo ""
echo "This script will:"
echo "1. Extract files from main branch that were deleted in PR #94"
echo "2. Create a directory structure for basics-2"
echo "3. Copy all deleted files and workflows"
echo "4. Prepare the basics-2 repository structure"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "ERROR: Not in a git repository"
    exit 1
fi

# Get the list of deleted files from PR #94
echo "Step 1: Analyzing PR #94 changes..."
git fetch origin main:main 2>/dev/null || true

# Find the reset commit
RESET_COMMIT=$(git log --all --grep="Reset repository" --format="%H" | head -1)
if [ -z "$RESET_COMMIT" ]; then
    echo "ERROR: Could not find the reset commit from PR #94"
    exit 1
fi

echo "Found reset commit: $RESET_COMMIT"

# Get the parent commit (state before reset)
# The reset commit is grafted, so we'll use main branch instead
PARENT_COMMIT="main"
echo "Using main branch as source (state before reset)"

# Create export directory
echo ""
echo "Step 2: Creating export directory: $EXPORT_DIR"
rm -rf "$EXPORT_DIR"
mkdir -p "$EXPORT_DIR"

# Get list of deleted files
echo ""
echo "Step 3: Extracting list of deleted files..."
git diff --name-status "$PARENT_COMMIT" "$RESET_COMMIT" | awk '$1 == "D" {print $2}' > "$EXPORT_DIR/deleted_files.txt"

DELETED_COUNT=$(wc -l < "$EXPORT_DIR/deleted_files.txt")
echo "Found $DELETED_COUNT files to transfer"

# Extract each deleted file from the parent commit
echo ""
echo "Step 4: Extracting files from main branch (before PR #94)..."
EXTRACTED=0
FAILED=0

while IFS= read -r file; do
    # Get the directory path
    dir=$(dirname "$file")
    
    # Create directory structure in export
    mkdir -p "$EXPORT_DIR/$dir"
    
    # Extract the file from the parent commit
    if git show "$PARENT_COMMIT:$file" > "$EXPORT_DIR/$file" 2>/dev/null; then
        EXTRACTED=$((EXTRACTED + 1))
        if [ $((EXTRACTED % 20)) -eq 0 ]; then
            echo "  Extracted $EXTRACTED/$DELETED_COUNT files..."
        fi
    else
        FAILED=$((FAILED + 1))
        echo "  WARNING: Could not extract: $file"
    fi
done < "$EXPORT_DIR/deleted_files.txt"

echo ""
echo "Extraction complete:"
echo "  - Successfully extracted: $EXTRACTED files"
echo "  - Failed: $FAILED files"

# Create README for basics-2
echo ""
echo "Step 5: Creating README for basics-2..."
cat > "$EXPORT_DIR/README.md" << 'EOF'
# basics-2

This repository contains the legacy files and workflows from The-basics repository that were removed in PR #94.

## Origin

These files were extracted from The-basics repository (https://github.com/oconnorw225-del/The-basics) before the repository was reset to a Project Chimera monorepo structure.

## Contents

This repository includes:
- GitHub workflows (.github/workflows/)
- Configuration files (.dockerignore, .eslintrc.json, etc.)
- Documentation files (various .md files)
- Backend and frontend code
- Automation scripts
- And other legacy files

## Transfer Date

Files transferred: $(date +"%Y-%m-%d %H:%M:%S")

## Original Repository

- Repository: oconnorw225-del/The-basics
- PR #94: Reset repository to Project Chimera monorepo structure
- Files preserved from commit: $(git rev-parse --short $PARENT_COMMIT)

## Structure

The directory structure mirrors the original repository layout before the reset.
EOF

# Create .gitignore for basics-2
cat > "$EXPORT_DIR/.gitignore" << 'EOF'
# Node
node_modules/
npm-debug.log*

# Python
__pycache__/
*.py[cod]
*.so
.Python
*.egg-info/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
EOF

# Create instructions file
cat > "$EXPORT_DIR/TRANSFER_INSTRUCTIONS.md" << 'EOF'
# Transfer Instructions for basics-2

## Steps to Create basics-2 Repository

### Option 1: Using GitHub Web Interface

1. Go to https://github.com/new
2. Repository name: `basics-2`
3. Description: "Legacy files from The-basics repository (preserved from PR #94)"
4. Choose Public or Private
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

### Option 2: Using GitHub CLI

```bash
gh repo create oconnorw225-del/basics-2 --public --description "Legacy files from The-basics repository"
```

## Transfer the Files

Once basics-2 repository is created, run these commands:

```bash
cd basics-2-export

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Transfer legacy files from The-basics PR #94"

# Add remote (replace with your actual repository URL)
git remote add origin https://github.com/oconnorw225-del/basics-2.git

# Push to main branch
git branch -M main
git push -u origin main
```

## Verify the Transfer

After pushing:
1. Visit https://github.com/oconnorw225-del/basics-2
2. Verify all files are present
3. Check that workflows are in .github/workflows/
4. Review the README.md

## Files Transferred

Total files: $(wc -l < deleted_files.txt)

Key directories:
- .github/workflows/ - GitHub Actions workflows
- Backend and frontend code directories
- Documentation files
- Configuration files
- Automation scripts

## Next Steps

After successful transfer:
1. Update PR #94 description to reference basics-2 repository
2. Add a link in The-basics README pointing to basics-2
3. Close PR #94 or merge as intended

## Cleanup

Once you've verified the transfer is successful, you can delete this export directory:
```bash
rm -rf basics-2-export
```
EOF

echo ""
echo "=========================================="
echo "Export Complete!"
echo "=========================================="
echo ""
echo "Files have been exported to: $EXPORT_DIR"
echo ""
echo "Next steps:"
echo "1. Review the exported files in: $EXPORT_DIR"
echo "2. Create the basics-2 repository on GitHub"
echo "3. Follow instructions in: $EXPORT_DIR/TRANSFER_INSTRUCTIONS.md"
echo ""
echo "Quick commands:"
echo "  cd $EXPORT_DIR"
echo "  cat TRANSFER_INSTRUCTIONS.md"
echo ""
