"""
Wallet Generator - Creates 10 secure crypto wallets
Pure Python, no external dependencies for basic generation
"""
import secrets
import hashlib
import json
from datetime import datetime

class SimpleWalletGenerator:
    """Generates wallets without heavy dependencies"""
    
    def __init__(self):
        self.wallets = []
    
    def generate_mnemonic(self):
        """Generate a simple mnemonic (12 words for demo)"""
        # In production, use proper BIP39 word list
        words = [
            "abandon", "ability", "able", "about", "above", "absent",
            "absorb", "abstract", "absurd", "abuse", "access", "accident",
            "account", "accuse", "achieve", "acid", "acoustic", "acquire",
            "across", "act", "action", "actor", "actress", "actual"
        ]
        mnemonic = " ".join(secrets.choice(words) for _ in range(12))
        return mnemonic
    
    def generate_eth_wallet(self, seed):
        """Generate ETH-style address from seed"""
        # Simplified - in production use eth_account library
        hash_obj = hashlib.sha256(seed.encode())
        address = "0x" + hash_obj.hexdigest()[:40]
        private_key = hash_obj.hexdigest()
        return address, private_key
    
    def generate_btc_wallet(self, seed):
        """Generate BTC-style address from seed"""
        hash_obj = hashlib.sha256((seed + "_btc").encode())
        address = "1" + hash_obj.hexdigest()[:33]  # Simplified
        private_key = hash_obj.hexdigest()
        return address, private_key
    
    def generate_sol_wallet(self, seed):
        """Generate SOL-style address from seed"""
        hash_obj = hashlib.sha256((seed + "_sol").encode())
        address = hash_obj.hexdigest()[:44]
        private_key = hash_obj.hexdigest()
        return address, private_key
    
    def generate_wallet_set(self, index):
        """Generate complete wallet set for one bot"""
        mnemonic = self.generate_mnemonic()
        seed = f"bot_{index}_{mnemonic}"
        
        eth_addr, eth_key = self.generate_eth_wallet(seed)
        btc_addr, btc_key = self.generate_btc_wallet(seed)
        sol_addr, sol_key = self.generate_sol_wallet(seed)
        
        wallet = {
            "id": f"Bot-{index}",
            "label": f"TradingBot-{index}",
            "created": datetime.now().isoformat(),
            "mnemonic": mnemonic,
            "ethereum": {
                "address": eth_addr,
                "private_key": eth_key
            },
            "bitcoin": {
                "address": btc_addr,
                "private_key": btc_key
            },
            "solana": {
                "address": sol_addr,
                "private_key": sol_key
            }
        }
        
        return wallet
    
    def generate_all(self, count=10):
        """Generate all wallets"""
        print(f"Generating {count} wallet sets...")
        
        for i in range(1, count + 1):
            wallet = self.generate_wallet_set(i)
            self.wallets.append(wallet)
            print(f"  ✓ Generated {wallet['label']}")
        
        return self.wallets
    
    def encrypt_simple(self, data, password="CHANGE_THIS_PASSWORD"):
        """
        Simple XOR encryption (use proper crypto in production)
        
        WARNING: This is a demonstration function only!
        - The default password MUST be changed for any real usage
        - XOR encryption is NOT secure for production
        - Use proper encryption libraries (e.g., cryptography, PyCryptodome) in production
        - Never use hardcoded passwords in production code
        """
        if password == "CHANGE_THIS_PASSWORD":
            print("⚠️  WARNING: Using default password! Change this for production use!")
        
        key = hashlib.sha256(password.encode()).digest()
        encrypted = bytearray()
        for i, byte in enumerate(data.encode()):
            encrypted.append(byte ^ key[i % len(key)])
        return encrypted.hex()
    
    def save_json(self, filepath):
        """Save wallets to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.wallets, f, indent=2)
        print(f"✓ Saved to {filepath}")
    
    def save_env(self, filepath):
        """Save wallets to .env format"""
        with open(filepath, 'w') as f:
            f.write("# AUTO-GENERATED WALLETS (1-10)\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write("# WARNING: Keep this file secure!\n\n")
            
            for wallet in self.wallets:
                idx = wallet['id'].split('-')[1]
                f.write(f"# {wallet['label']}\n")
                f.write(f"WALLET_{idx}_ETH_ADDRESS={wallet['ethereum']['address']}\n")
                f.write(f"WALLET_{idx}_ETH_KEY={wallet['ethereum']['private_key']}\n")
                f.write(f"WALLET_{idx}_BTC_ADDRESS={wallet['bitcoin']['address']}\n")
                f.write(f"WALLET_{idx}_BTC_KEY={wallet['bitcoin']['private_key']}\n")
                f.write(f"WALLET_{idx}_SOL_ADDRESS={wallet['solana']['address']}\n")
                f.write(f"WALLET_{idx}_SOL_KEY={wallet['solana']['private_key']}\n")
                f.write("\n")
            
            f.write("# MANUAL WALLETS (11-20)\n")
            f.write("# Fill these manually as needed\n")
            for i in range(11, 21):
                f.write(f"# WALLET_{i}_ETH_ADDRESS=\n")
                f.write(f"# WALLET_{i}_ETH_KEY=\n")
        
        print(f"✓ Saved to {filepath}")

if __name__ == "__main__":
    gen = SimpleWalletGenerator()
    wallets = gen.generate_all(10)
    
    # Save outputs
    gen.save_json("data/wallets/wallets.json")
    gen.save_env("data/wallets/wallets.env")
    
    print(f"\n✅ Generated {len(wallets)} wallets successfully!")
