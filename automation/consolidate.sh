#!/bin/bash

# Copy entire contents of ndax-quantum-engine
cp -r source/ndax-quantum-engine/* . 2>/dev/null || true

# Copy from quantum-engine-dashb
cp -r source/quantum-engine-dashb/src/* frontend/ 2>/dev/null || true
cp -r source/quantum-engine-dashb/.github/workflows/* workflows/ 2>/dev/null

# Copy entire contents of shadowforge-ai-trader
cp -r source/shadowforge-ai-trader/* . 2>/dev/null || true

# Copy from repository-web-app
cp -r source/repository-web-app/src/* frontend/ 2>/dev/null || true
cp -r source/repository-web-app/.github/workflows/* workflows/ 2>/dev/null || true

# Add The-new-ones repository to new_additions directory
mkdir -p new_additions
cp -r source/The-new-ones/* new_additions/ 2>/dev/null || true

# Note: wizzard_tools and config from shadowforge-ai-trader are already copied to root
# via the full repository copy above (line 11), ensuring better visibility and access
