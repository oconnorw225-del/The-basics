#!/bin/bash
cp -r source/ndax-quantum-engine/api/* api/ 2>/dev/null || true
cp -r source/quantum-engine-dashb/src/* frontend/ 2>/dev/null || true
cp -r source/shadowforge-ai-trader/strategy/* backend/ 2>/dev/null || true
cp -r source/repository-web-app/src/* frontend/ 2>/dev/null || true
cp -r source/ndax-quantum-engine/docs/* docs/ 2>/dev/null || true
cp -r source/quantum-engine-dashb/.github/workflows/* workflows/ 2>/dev/null || true
cp -r source/repository-web-app/.github/workflows/* workflows/ 2>/dev/null || true
cp -r source/shadowforge-ai-trader/tests/* tests/ 2>/dev/null || true
