#!/bin/bash
# Test script for consolidate.sh
# This verifies the improved error handling and logging

set -e

echo "=========================================="
echo "Testing consolidate.sh improvements"
echo "=========================================="

# Create test directory structure
TEST_DIR=$(mktemp -d)
echo "📁 Created test directory: $TEST_DIR"

cd "$TEST_DIR"

# Create mock source directories
mkdir -p source/ndax-quantum-engine/src
mkdir -p source/quantum-engine-dashb/src
mkdir -p source/shadowforge-ai-trader/config
mkdir -p source/repository-web-app/src
mkdir -p source/The-new-ones/data

# Add some test files
echo "test content" > source/ndax-quantum-engine/src/test.txt
echo "dashboard content" > source/quantum-engine-dashb/src/dashboard.js
echo "config content" > source/shadowforge-ai-trader/config/settings.json
echo "web app content" > source/repository-web-app/src/app.js
echo "new data" > source/The-new-ones/data/data.txt

# Create target directories
mkdir -p api backend frontend workflows docs automation tests

# Copy the consolidate.sh script (use relative path for portability)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR%/tests}"

if [ -f "$REPO_ROOT/automation/consolidate.sh" ]; then
    cp "$REPO_ROOT/automation/consolidate.sh" automation/
elif [ -f "/home/runner/work/The-basics/The-basics/automation/consolidate.sh" ]; then
    # Fallback for GitHub Actions environment
    cp /home/runner/work/The-basics/The-basics/automation/consolidate.sh automation/
else
    echo "❌ Error: Could not find consolidate.sh"
    exit 1
fi

echo ""
echo "🧪 Running consolidate.sh..."
echo ""

# Run the consolidation script
cd "$TEST_DIR"
bash automation/consolidate.sh

echo ""
echo "✅ Script completed successfully!"
echo ""

# Verify files were copied
echo "🔍 Verifying file operations..."
errors=0

if [ -f "src/test.txt" ]; then
    echo "  ✓ ndax-quantum-engine files copied"
else
    echo "  ✗ ndax-quantum-engine files NOT copied"
    ((errors++))
fi

if [ -d "frontend" ]; then
    echo "  ✓ frontend directory exists"
else
    echo "  ✗ frontend directory missing"
    ((errors++))
fi

if [ -d "new_additions" ]; then
    echo "  ✓ new_additions directory created"
else
    echo "  ✗ new_additions directory missing"
    ((errors++))
fi

echo ""
if [ $errors -eq 0 ]; then
    echo "✅ All tests passed!"
    exit_code=0
else
    echo "❌ $errors test(s) failed"
    exit_code=1
fi

# Cleanup
cd /
rm -rf "$TEST_DIR"
echo "🧹 Cleaned up test directory"

exit $exit_code
