#!/usr/bin/env python3
"""
Live Market Data Service
Real-time market data aggregation from multiple sources
"""

import asyncio
import aiohttp
import json
import websockets
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveMarketData:
    """Real-time market data aggregator"""
    
    def __init__(self):
        self.price_cache = {}
        self.subscribers = []
        self.ws_connections = {}
        self.running = False
        
        # API endpoints
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.coinmarketcap_base = "https://pro-api.coinmarketcap.com/v1"
        self.binance_ws = "wss://stream.binance.com:9443/ws"
        
    async def start(self):
        """Start all live data feeds"""
        self.running = True
        
        tasks = [
            self.fetch_coingecko_prices(),
            self.monitor_binance_stream(),
            self.fetch_market_metrics(),
            self.calculate_indicators(),
        ]
        
        await asyncio.gather(*tasks)
    
    async def stop(self):
        """Stop all feeds"""
        self.running = False
        
        # Close WebSocket connections
        for ws in self.ws_connections.values():
            await ws.close()
    
    async def fetch_coingecko_prices(self):
        """Fetch live prices from CoinGecko"""
        while self.running:
            try:
                async with aiohttp.ClientSession() as session:
                    # Top 250 coins by market cap
                    url = f"{self.coingecko_base}/coins/markets"
                    params = {
                        'vs_currency': 'usd',
                        'order': 'market_cap_desc',
                        'per_page': 250,
                        'page': 1,
                        'sparkline': True,
                        'price_change_percentage': '1h,24h,7d,30d'
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for coin in data:
                                symbol = coin['symbol'].upper()
                                
                                self.price_cache[symbol] = {
                                    'price': coin['current_price'],
                                    'market_cap': coin['market_cap'],
                                    'volume_24h': coin['total_volume'],
                                    'change_1h': coin.get('price_change_percentage_1h_in_currency'),
                                    'change_24h': coin.get('price_change_percentage_24h'),
                                    'change_7d': coin.get('price_change_percentage_7d_in_currency'),
                                    'change_30d': coin.get('price_change_percentage_30d_in_currency'),
                                    'high_24h': coin['high_24h'],
                                    'low_24h': coin['low_24h'],
                                    'sparkline': coin.get('sparkline_in_7d', {}).get('price', []),
                                    'timestamp': datetime.now().isoformat(),
                                    'source': 'coingecko'
                                }
                            
                            # Notify subscribers
                            await self.notify_subscribers('price_update', self.price_cache)
                            
                            logger.info(f"Updated prices for {len(data)} coins")
                
                # Update every 30 seconds (CoinGecko rate limit)
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error fetching CoinGecko prices: {e}")
                await asyncio.sleep(60)
    
    async def monitor_binance_stream(self):
        """Monitor Binance WebSocket for real-time updates"""
        symbols = ['btcusdt', 'ethusdt', 'bnbusdt', 'adausdt', 'dogeusdt']
        stream_names = [f"{s}@ticker" for s in symbols]
        
        while self.running:
            try:
                stream_url = f"{self.binance_ws}/{'/' .join(stream_names)}"
                
                async with websockets.connect(stream_url) as websocket:
                    self.ws_connections['binance'] = websocket
                    
                    while self.running:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if 'e' in data and data['e'] == '24hrTicker':
                            symbol = data['s'].replace('USDT', '')
                            
                            self.price_cache[symbol] = {
                                'price': float(data['c']),
                                'volume_24h': float(data['v']),
                                'change_24h': float(data['P']),
                                'high_24h': float(data['h']),
                                'low_24h': float(data['l']),
                                'bid': float(data['b']),
                                'ask': float(data['a']),
                                'trades': int(data['n']),
                                'timestamp': datetime.now().isoformat(),
                                'source': 'binance'
                            }
                            
                            # Notify subscribers
                            await self.notify_subscribers('price_update', {symbol: self.price_cache[symbol]})
                
            except Exception as e:
                logger.error(f"Binance WebSocket error: {e}")
                await asyncio.sleep(5)
    
    async def fetch_market_metrics(self):
        """Fetch overall market metrics"""
        while self.running:
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{self.coingecko_base}/global"
                    
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            global_data = data['data']
                            
                            metrics = {
                                'total_market_cap': global_data['total_market_cap']['usd'],
                                'total_volume': global_data['total_volume']['usd'],
                                'btc_dominance': global_data['market_cap_percentage']['btc'],
                                'eth_dominance': global_data['market_cap_percentage']['eth'],
                                'active_cryptocurrencies': global_data['active_cryptocurrencies'],
                                'markets': global_data['markets'],
                                'market_cap_change_24h': global_data['market_cap_change_percentage_24h_usd'],
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            # Notify subscribers
                            await self.notify_subscribers('market_metrics', metrics)
                            
                            logger.info(f"Updated market metrics: ${metrics['total_market_cap']:,.0f}")
                
                # Update every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error fetching market metrics: {e}")
                await asyncio.sleep(300)
    
    async def calculate_indicators(self):
        """Calculate technical indicators"""
        while self.running:
            try:
                for symbol, data in self.price_cache.items():
                    if 'sparkline' in data and len(data['sparkline']) > 0:
                        prices = data['sparkline']
                        
                        # Calculate RSI
                        rsi = self._calculate_rsi(prices)
                        
                        # Calculate MACD
                        macd, signal = self._calculate_macd(prices)
                        
                        # Calculate Bollinger Bands
                        upper, middle, lower = self._calculate_bollinger_bands(prices)
                        
                        # Update cache
                        self.price_cache[symbol]['indicators'] = {
                            'rsi': rsi,
                            'macd': macd,
                            'macd_signal': signal,
                            'bollinger_upper': upper,
                            'bollinger_middle': middle,
                            'bollinger_lower': lower,
                            'timestamp': datetime.now().isoformat()
                        }
                
                # Calculate every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error calculating indicators: {e}")
                await asyncio.sleep(60)
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [c if c > 0 else 0 for c in changes]
        losses = [-c if c < 0 else 0 for c in changes]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def _calculate_macd(self, prices: List[float]) -> tuple:
        """Calculate MACD indicator"""
        if len(prices) < 26:
            return 0.0, 0.0
        
        # Simple moving averages (normally EMA)
        ema12 = sum(prices[-12:]) / 12
        ema26 = sum(prices[-26:]) / 26
        
        macd = ema12 - ema26
        signal = macd * 0.9  # Simplified
        
        return round(macd, 2), round(signal, 2)
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20) -> tuple:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return 0.0, 0.0, 0.0
        
        recent = prices[-period:]
        middle = sum(recent) / period
        
        variance = sum((p - middle) ** 2 for p in recent) / period
        std_dev = variance ** 0.5
        
        upper = middle + (2 * std_dev)
        lower = middle - (2 * std_dev)
        
        return round(upper, 2), round(middle, 2), round(lower, 2)
    
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Get current price data for symbol"""
        return self.price_cache.get(symbol.upper())
    
    async def get_all_prices(self) -> Dict:
        """Get all cached prices"""
        return self.price_cache
    
    async def subscribe(self, callback):
        """Subscribe to real-time updates"""
        self.subscribers.append(callback)
    
    async def notify_subscribers(self, event_type: str, data: Dict):
        """Notify all subscribers of updates"""
        for callback in self.subscribers:
            try:
                await callback(event_type, data)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
    
    async def get_trending_coins(self, limit: int = 10) -> List[Dict]:
        """Get trending coins by volume and price change"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.coingecko_base}/search/trending"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['coins'][:limit]
        except Exception as e:
            logger.error(f"Error fetching trending coins: {e}")
        
        return []
    
    async def get_market_fear_greed_index(self) -> Optional[Dict]:
        """Get Fear & Greed Index"""
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://api.alternative.me/fng/"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'value': int(data['data'][0]['value']),
                            'classification': data['data'][0]['value_classification'],
                            'timestamp': data['data'][0]['timestamp']
                        }
        except Exception as e:
            logger.error(f"Error fetching fear/greed index: {e}")
        
        return None

if __name__ == "__main__":
    async def main():
        market_data = LiveMarketData()
        
        # Subscribe to updates
        async def print_update(event_type, data):
            if event_type == 'price_update' and 'BTC' in data:
                print(f"BTC Price: ${data['BTC']['price']:,.2f}")
        
        await market_data.subscribe(print_update)
        
        # Start feeds
        await market_data.start()
    
    asyncio.run(main())
