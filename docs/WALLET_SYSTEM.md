# Wallet System

## Overview
Auto-generated wallet system for 10 trading bots.

## Quick Start

1. **Generate wallets**:
   ```bash
   bash scripts/setup_wallet_system.sh
   ```

2. **Check generated wallets**:
   ```bash
   cat data/wallets/wallets.json
   ```

3. **Load wallet in bot**:
   ```python
   from core.wallet_system.manager import WalletManager
   
   wm = WalletManager()
   wallet = wm.get_wallet("Bot-1")
   print(wallet['ethereum']['address'])
   ```

## Structure

- **Wallets 1-10**: Auto-generated (ETH + BTC + SOL)
- **Wallets 11-20**: Reserved for manual configuration

## Security

⚠️ **CRITICAL**: 
- Never commit `data/wallets/` to Git
- Keep private keys encrypted
- Use testnet addresses first
- Store backups securely

## Manual Wallets

Edit `config/manual_wallets.json`:
```json
{
  "wallet_11": {
    "eth_address": "0x...",
    "eth_private_key": "encrypted_key"
  }
}
```

## API Usage

```python
# Get all wallet addresses
addresses = wm.get_all_addresses()

# Check balance
balance = wm.check_balance("Bot-1")
```
