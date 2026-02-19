#!/bin/bash
# Bot Public API - Bash Example
# Shows how to access public platform information using curl

echo "🤖 Bot Public API - Bash Example"
echo "================================================================"

BASE_URL="${API_BASE_URL:-http://localhost:8000}"

echo ""
echo "📋 Platform Information:"
curl -s "$BASE_URL/api/public/platform" | python3 -m json.tool 2>/dev/null || echo "⚠️ API not running or error"

echo ""
echo ""
echo "📦 Products:"
curl -s "$BASE_URL/api/public/products" | python3 -m json.tool 2>/dev/null || echo "⚠️ API not running or error"

echo ""
echo ""
echo "🎯 Capabilities:"
curl -s "$BASE_URL/api/public/capabilities" | python3 -m json.tool 2>/dev/null || echo "⚠️ API not running or error"

echo ""
echo ""
echo "🔐 Access Levels:"
curl -s "$BASE_URL/api/public/access-levels" | python3 -m json.tool 2>/dev/null || echo "⚠️ API not running or error"

echo ""
echo ""
echo "🔌 Public Endpoints (Summary):"
curl -s "$BASE_URL/api/public/endpoints" | python3 -c "
import sys, json
data = json.load(sys.stdin)
endpoints = data.get('endpoints', [])
print(f'Total: {len(endpoints)} public endpoints')
for ep in endpoints[:5]:
    print(f'  • {ep[\"method\"]} {ep[\"path\"]} - {ep[\"description\"]}')
if len(endpoints) > 5:
    print(f'  ... and {len(endpoints) - 5} more')
" 2>/dev/null || echo "⚠️ API not running or error"

echo ""
echo ""
echo "📚 Documentation Links:"
curl -s "$BASE_URL/api/public/documentation" | python3 -m json.tool 2>/dev/null || echo "⚠️ API not running or error"

echo ""
echo "================================================================"
echo "✅ Example complete"
echo ""
echo "Note: Set API_BASE_URL environment variable to use different base URL"
echo "Example: API_BASE_URL=http://example.com ./examples/bot_public_api_example.sh"
