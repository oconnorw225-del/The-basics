#!/bin/bash
set -e

echo "🤖 Setting up Complete Wallet + AI Knowledge System"
echo "===================================================="
echo ""

# Create directory structure
echo "📁 Creating directories..."
mkdir -p core/wallet_system
mkdir -p core/knowledge_network
mkdir -p core/integration
mkdir -p data/wallets
mkdir -p data/knowledge/learning_history
mkdir -p config
mkdir -p scripts
mkdir -p tests

# Generate wallets
echo ""
echo "💰 Generating 10 wallets..."
python3 core/wallet_system/generator.py

# Initialize knowledge base
echo ""
echo "🧠 Initializing AI knowledge network..."
python3 -c "
from core.knowledge_network.knowledge_base import KnowledgeBase
kb = KnowledgeBase()
print('✓ Knowledge base initialized')
"

# Set permissions
echo ""
echo "🔒 Setting secure permissions..."
chmod 600 data/wallets/*
chmod 700 data/wallets

echo ""
echo "✅ SETUP COMPLETE!"
echo ""
echo "Created:"
echo "  ✓ 10 auto-generated wallets (Bot-1 to Bot-10)"
echo "  ✓ AI knowledge network initialized"
echo "  ✓ Secure file permissions set"
echo ""
echo "Files:"
echo "  📄 data/wallets/wallets.json - Wallet data"
echo "  📄 data/wallets/wallets.env - Environment variables"
echo "  📄 data/knowledge/shared_memory.json - AI knowledge base"
echo ""
echo "Next steps:"
echo "  1. Review generated wallets in data/wallets/"
echo "  2. Update config/manual_wallets.json for slots 11-20"
echo "  3. Never commit wallet files to Git!"
echo "  4. Use testnet addresses before mainnet"
echo ""
echo "⚠️  SECURITY WARNING:"
echo "  - Keep data/wallets/ directory secure"
echo "  - Never share private keys"
echo "  - Use encryption for backups"
echo ""
