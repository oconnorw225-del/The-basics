"""
Wallet Manager - Load and manage generated wallets
"""
import json
import os
from pathlib import Path

class WalletManager:
    def __init__(self, wallets_file="data/wallets/wallets.json"):
        self.wallets_file = wallets_file
        self.wallets = self._load_wallets()
    
    def _load_wallets(self):
        """Load wallets from JSON"""
        if not os.path.exists(self.wallets_file):
            return []
        
        with open(self.wallets_file) as f:
            return json.load(f)
    
    def get_wallet(self, bot_id):
        """Get wallet for specific bot"""
        for wallet in self.wallets:
            if wallet['id'] == bot_id or wallet['label'] == f"TradingBot-{bot_id}":
                return wallet
        return None
    
    def get_all_addresses(self):
        """Get all wallet addresses"""
        addresses = []
        for wallet in self.wallets:
            addresses.append({
                "bot": wallet['label'],
                "eth": wallet['ethereum']['address'],
                "btc": wallet['bitcoin']['address'],
                "sol": wallet['solana']['address']
            })
        return addresses
    
    def check_balance(self, bot_id):
        """Check wallet balance (placeholder)"""
        # In production, connect to blockchain APIs
        return {
            "eth": 0.0,
            "btc": 0.0,
            "sol": 0.0
        }
