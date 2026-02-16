#!/usr/bin/env python3
"""
Live Wallet Feed Service
Real-time wallet activity monitoring across multiple chains
"""

import asyncio
import aiohttp
import websockets
import json
from datetime import datetime
from typing import Dict, List, Optional, Set
import logging
from web3 import Web3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveWalletFeed:
    """Real-time wallet activity monitor"""
    
    def __init__(self, infura_key: str = None, alchemy_key: str = None):
        self.monitored_wallets: Set[str] = set()
        self.wallet_data = {}
        self.transaction_history = {}
        self.subscribers = []
        self.running = False
        
        # WebSocket endpoints
        self.infura_key = infura_key or "YOUR_INFURA_KEY"
        self.alchemy_key = alchemy_key or "YOUR_ALCHEMY_KEY"
        
        self.eth_ws = f"wss://mainnet.infura.io/ws/v3/{self.infura_key}"
        self.bsc_ws = "wss://bsc-ws-node.nariox.org:443"
        
        # Web3 connections
        self.w3_eth = None
        self.w3_bsc = None
        
    async def start(self):
        """Start wallet monitoring"""
        self.running = True
        
        # Initialize Web3 connections
        try:
            self.w3_eth = Web3(Web3.WebsocketProvider(self.eth_ws))
            logger.info(f"Connected to Ethereum: {self.w3_eth.is_connected()}")
        except Exception as e:
            logger.error(f"Error connecting to Ethereum: {e}")
        
        tasks = [
            self.monitor_ethereum_wallets(),
            self.monitor_bsc_wallets(),
            self.fetch_wallet_balances(),
            self.scan_pending_transactions(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
    
    def add_wallet(self, address: str, label: str = None):
        """Add wallet to monitoring"""
        address = address.lower()
        self.monitored_wallets.add(address)
        
        if address not in self.wallet_data:
            self.wallet_data[address] = {
                'address': address,
                'label': label or f"Wallet {len(self.monitored_wallets)}",
                'balances': {},
                'transactions': [],
                'last_activity': None,
                'added_at': datetime.now().isoformat()
            }
        
        logger.info(f"Added wallet {address[:10]}... to monitoring")
    
    def remove_wallet(self, address: str):
        """Remove wallet from monitoring"""
        address = address.lower()
        self.monitored_wallets.discard(address)
        logger.info(f"Removed wallet {address[:10]}...")
    
    async def monitor_ethereum_wallets(self):
        """Monitor Ethereum wallets via WebSocket"""
        while self.running:
            try:
                async with websockets.connect(self.eth_ws) as websocket:
                    # Subscribe to new blocks
                    subscription = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "eth_subscribe",
                        "params": ["newHeads"]
                    }
                    await websocket.send(json.dumps(subscription))
                    
                    # Listen for new blocks
                    while self.running:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if 'params' in data:
                            block_data = data['params']['result']
                            block_number = int(block_data['number'], 16)
                            
                            # Check transactions in this block
                            await self.check_block_transactions('ethereum', block_number)
                        
                        await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Ethereum WebSocket error: {e}")
                await asyncio.sleep(5)
    
    async def monitor_bsc_wallets(self):
        """Monitor BSC wallets"""
        while self.running:
            try:
                # Use HTTP polling for BSC (more reliable than WebSocket)
                async with aiohttp.ClientSession() as session:
                    for address in self.monitored_wallets:
                        url = f"https://api.bscscan.com/api"
                        params = {
                            'module': 'account',
                            'action': 'txlist',
                            'address': address,
                            'startblock': 0,
                            'endblock': 99999999,
                            'page': 1,
                            'offset': 10,
                            'sort': 'desc'
                        }
                        
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                if data['status'] == '1':
                                    transactions = data['result']
                                    await self.process_transactions('bsc', address, transactions)
                
                # Check every 15 seconds
                await asyncio.sleep(15)
                
            except Exception as e:
                logger.error(f"BSC monitoring error: {e}")
                await asyncio.sleep(15)
    
    async def check_block_transactions(self, chain: str, block_number: int):
        """Check transactions in a block for monitored wallets"""
        try:
            if chain == 'ethereum' and self.w3_eth and self.w3_eth.is_connected():
                block = await asyncio.to_thread(
                    self.w3_eth.eth.get_block,
                    block_number,
                    full_transactions=True
                )
                
                for tx in block['transactions']:
                    # Check if transaction involves monitored wallets
                    from_addr = tx.get('from', '').lower()
                    to_addr = tx.get('to', '').lower() if tx.get('to') else ''
                    
                    if from_addr in self.monitored_wallets or to_addr in self.monitored_wallets:
                        tx_data = {
                            'hash': tx['hash'].hex(),
                            'from': from_addr,
                            'to': to_addr,
                            'value': Web3.from_wei(tx['value'], 'ether'),
                            'gas': tx['gas'],
                            'gasPrice': Web3.from_wei(tx['gasPrice'], 'gwei'),
                            'block': block_number,
                            'timestamp': datetime.now().isoformat(),
                            'chain': chain,
                            'status': 'pending'
                        }
                        
                        # Notify subscribers
                        await self.notify_subscribers('new_transaction', tx_data)
                        
                        # Store transaction
                        wallet = from_addr if from_addr in self.monitored_wallets else to_addr
                        if wallet in self.wallet_data:
                            self.wallet_data[wallet]['transactions'].insert(0, tx_data)
                            self.wallet_data[wallet]['last_activity'] = datetime.now().isoformat()
                        
                        logger.info(f"New transaction: {tx_data['hash'][:10]}...")
        
        except Exception as e:
            logger.error(f"Error checking block transactions: {e}")
    
    async def process_transactions(self, chain: str, address: str, transactions: List[Dict]):
        """Process transaction list for wallet"""
        for tx in transactions:
            tx_data = {
                'hash': tx.get('hash'),
                'from': tx.get('from', '').lower(),
                'to': tx.get('to', '').lower(),
                'value': float(tx.get('value', 0)) / 1e18,  # Wei to ETH/BNB
                'gas': int(tx.get('gasUsed', 0)),
                'gasPrice': float(tx.get('gasPrice', 0)) / 1e9,  # Wei to Gwei
                'block': int(tx.get('blockNumber', 0)),
                'timestamp': datetime.fromtimestamp(int(tx.get('timeStamp', 0))).isoformat(),
                'chain': chain,
                'status': 'confirmed'
            }
            
            # Check if new transaction
            if address in self.wallet_data:
                existing = self.wallet_data[address]['transactions']
                if not any(t.get('hash') == tx_data['hash'] for t in existing):
                    self.wallet_data[address]['transactions'].insert(0, tx_data)
                    self.wallet_data[address]['last_activity'] = tx_data['timestamp']
                    
                    # Notify subscribers
                    await self.notify_subscribers('new_transaction', tx_data)
    
    async def fetch_wallet_balances(self):
        """Fetch balances for all monitored wallets"""
        while self.running:
            try:
                async with aiohttp.ClientSession() as session:
                    for address in self.monitored_wallets:
                        # Ethereum balance
                        eth_balance = await self.get_eth_balance(session, address)
                        
                        # BSC balance
                        bsc_balance = await self.get_bsc_balance(session, address)
                        
                        # ERC20 token metadata
                        token_metadata = await self.get_token_metadata(session, address, 'ethereum')
                        
                        # Update wallet data
                        if address in self.wallet_data:
                            self.wallet_data[address]['balances'] = {
                                'ETH': eth_balance,
                                'BNB': bsc_balance,
                                'tokens': token_metadata,
                                'updated_at': datetime.now().isoformat()
                            }
                            
                            # Notify subscribers
                            await self.notify_subscribers('balance_update', {
                                'address': address,
                                'balances': self.wallet_data[address]['balances']
                            })
                
                # Update every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error fetching balances: {e}")
                await asyncio.sleep(30)
    
    async def get_eth_balance(self, session: aiohttp.ClientSession, address: str) -> float:
        """Get Ethereum balance"""
        try:
            url = f"https://api.etherscan.io/api"
            params = {
                'module': 'account',
                'action': 'balance',
                'address': address,
                'tag': 'latest'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['status'] == '1':
                        return float(data['result']) / 1e18
        except Exception as e:
            logger.error(f"Error getting ETH balance: {e}")
        
        return 0.0
    
    async def get_bsc_balance(self, session: aiohttp.ClientSession, address: str) -> float:
        """Get BSC balance"""
        try:
            url = f"https://api.bscscan.com/api"
            params = {
                'module': 'account',
                'action': 'balance',
                'address': address,
                'tag': 'latest'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['status'] == '1':
                        return float(data['result']) / 1e18
        except Exception as e:
            logger.error(f"Error getting BNB balance: {e}")
        
        return 0.0
    
    async def get_token_balances(self, session: aiohttp.ClientSession, address: str, chain: str) -> List[Dict]:
        """Get ERC20/BEP20 token balances"""
        try:
            if chain == 'ethereum':
                url = f"https://api.etherscan.io/api"
            else:
                url = f"https://api.bscscan.com/api"
            
            params = {
                'module': 'account',
                'action': 'tokentx',
                'address': address,
                'startblock': 0,
                'endblock': 99999999,
                'page': 1,
                'offset': 100,
                'sort': 'desc'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data['status'] == '1':
                        tokens = {}
                        for tx in data['result']:
                            symbol = tx.get('tokenSymbol')
                            if symbol not in tokens:
                                tokens[symbol] = {
                                    'symbol': symbol,
                                    'name': tx.get('tokenName'),
                                    'contract': tx.get('contractAddress'),
                                    'balance': 0,
                                    'decimals': int(tx.get('tokenDecimal', 18))
                                }
                        
                        return list(tokens.values())
        except Exception as e:
            logger.error(f"Error getting token balances: {e}")
        
        return []
    
    async def scan_pending_transactions(self):
        """Scan mempool for pending transactions"""
        while self.running:
            try:
                if self.w3_eth and self.w3_eth.is_connected():
                    # Get pending transactions (if supported)
                    pass
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error scanning pending transactions: {e}")
                await asyncio.sleep(5)
    
    async def subscribe(self, callback):
        """Subscribe to wallet feed updates"""
        self.subscribers.append(callback)
    
    async def notify_subscribers(self, event_type: str, data: Dict):
        """Notify all subscribers"""
        for callback in self.subscribers:
            try:
                await callback(event_type, data)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
    
    def get_wallet_data(self, address: str) -> Optional[Dict]:
        """Get data for specific wallet"""
        return self.wallet_data.get(address.lower())
    
    def get_all_wallets(self) -> Dict:
        """Get all wallet data"""
        return self.wallet_data

if __name__ == "__main__":
    async def main():
        feed = LiveWalletFeed()
        
        # Add test wallet
        feed.add_wallet("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", "Test Wallet")
        
        # Subscribe to updates
        async def print_update(event_type, data):
            print(f"{event_type}: {data}")
        
        await feed.subscribe(print_update)
        
        # Start monitoring
        await feed.start()
    
    asyncio.run(main())
