#!/bin/bash

# aggregate-projects.sh
# Script to clone multiple repositories and generate a project summary

set -e  # Exit on error

# Define color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Define the target directory
AGGREGATION_DIR="project_aggregation"
SUMMARY_FILE="project_summary.md"

# Parse command line arguments
FORCE_MODE=false
if [[ "$1" == "--force" || "$1" == "-f" || "$1" == "--yes" || "$1" == "-y" ]]; then
    FORCE_MODE=true
fi

# Define repositories to clone
REPOS=(
    "oconnorw225-del/ndax-quantum-engine"
    "oconnorw225-del/The-basics"
    "oconnorw225-del/The-new-ones"
    "oconnorw225-del/Cons_path-"
    "oconnorw225-del/shadowforge-ai-trader"
    "oconnorw225-del/quantum-engine-dashb"
    "oconnorw225-del/Cons_path"
    "oconnorw225-del/repository-web-app"
    "oconnorw225-del/Trader-bot-"
)

echo -e "${GREEN}=== Repository Aggregation Script ===${NC}"
echo ""

# Create aggregation directory if it doesn't exist
if [ -d "$AGGREGATION_DIR" ]; then
    echo -e "${YELLOW}Warning: $AGGREGATION_DIR already exists.${NC}"
    
    if [ "$FORCE_MODE" = true ]; then
        echo -e "${YELLOW}Force mode enabled. Removing existing $AGGREGATION_DIR...${NC}"
        rm -rf "$AGGREGATION_DIR"
    else
        read -p "Do you want to remove it and start fresh? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Removing existing $AGGREGATION_DIR...${NC}"
            rm -rf "$AGGREGATION_DIR"
        else
            echo -e "${RED}Aborting. Please remove or backup the existing directory first.${NC}"
            echo -e "${YELLOW}Or run with --force flag to automatically overwrite.${NC}"
            exit 1
        fi
    fi
fi

echo -e "${GREEN}Creating $AGGREGATION_DIR directory...${NC}"
mkdir -p "$AGGREGATION_DIR"

# Initialize summary file
echo "# Project Aggregation Summary" > "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "Generated on: $(date)" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "---" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# Clone each repository
for repo in "${REPOS[@]}"; do
    repo_name=$(basename "$repo")
    echo ""
    echo -e "${GREEN}Cloning $repo...${NC}"
    
    if git clone "https://github.com/$repo.git" "$AGGREGATION_DIR/$repo_name" 2>&1; then
        echo -e "${GREEN}✓ Successfully cloned $repo_name${NC}"
        
        # Add to summary
        echo "## $repo_name" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        echo "**Repository:** https://github.com/$repo" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        echo "**Directory Structure:**" >> "$SUMMARY_FILE"
        echo '```' >> "$SUMMARY_FILE"
        
        # Generate directory tree (limit depth to 3 levels)
        if command -v tree &> /dev/null; then
            tree -L 3 -I 'node_modules|.git|__pycache__|*.pyc' "$AGGREGATION_DIR/$repo_name" >> "$SUMMARY_FILE"
        else
            # Fallback if tree is not available
            (cd "$AGGREGATION_DIR/$repo_name" && find . -maxdepth 3 -type d ! -path '*/node_modules/*' ! -path '*/.git/*' ! -path '*/__pycache__/*' | sort) >> "$SUMMARY_FILE"
        fi
        
        echo '```' >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        echo "---" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
    else
        echo -e "${RED}✗ Failed to clone $repo_name${NC}"
        echo "## $repo_name" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        echo "**Status:** ❌ Failed to clone" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
        echo "---" >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
    fi
done

echo ""
echo -e "${GREEN}=== Aggregation Complete ===${NC}"
echo -e "${GREEN}Repositories cloned to: $AGGREGATION_DIR${NC}"
echo -e "${GREEN}Summary generated: $SUMMARY_FILE${NC}"
echo ""
echo -e "${YELLOW}Note: You may want to add '$AGGREGATION_DIR/' to .gitignore${NC}"
echo ""
echo -e "${YELLOW}Usage: $0 [--force|-f|--yes|-y]${NC}"
echo -e "${YELLOW}  --force, -f, --yes, -y: Skip confirmation prompts and overwrite existing directories${NC}"
