"""
Test wallet generation
"""
import sys
sys.path.append('..')

from core.wallet_system.generator import SimpleWalletGenerator

def test_generation():
    gen = SimpleWalletGenerator()
    wallets = gen.generate_all(10)
    
    assert len(wallets) == 10, "Should generate 10 wallets"
    
    for wallet in wallets:
        assert 'ethereum' in wallet
        assert 'bitcoin' in wallet
        assert 'solana' in wallet
        assert wallet['ethereum']['address'].startswith('0x')
    
    print("✅ All wallet generation tests passed")

if __name__ == "__main__":
    test_generation()
