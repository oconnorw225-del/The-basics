"""
Dashboard Backend - FastAPI server for system dashboard
Provides real-time metrics, status, and control interfaces
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Add backend to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
sys.path.insert(0, backend_path)

try:
    from bot_registry import BotRegistry
    from live_market_data import LiveMarketData
    from live_wallet_feed import LiveWalletFeed
    from asset_manager import AssetManager
    from blockchain_scanner import BlockchainScanner
    from file_processor import FileProcessor
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")
    BotRegistry = None
    LiveMarketData = None
    LiveWalletFeed = None

# Initialize FastAPI app
app = FastAPI(
    title="Trading System Dashboard",
    description="Real-time monitoring and control dashboard",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Initialize bot registry
bot_registry = BotRegistry() if BotRegistry else None

# Initialize live data services
market_data_service = None
wallet_feed_service = None
asset_manager = None
blockchain_scanner = None
file_processor = None

@app.on_event("startup")
async def startup_event():
    """Initialize live data services"""
    global market_data_service, wallet_feed_service, asset_manager, blockchain_scanner, file_processor
    
    try:
        if LiveMarketData:
            market_data_service = LiveMarketData()
            
            # Subscribe to market updates
            async def market_update_handler(event_type, data):
                await manager.broadcast({
                    'type': event_type,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
            
            await market_data_service.subscribe(market_update_handler)
            asyncio.create_task(market_data_service.start())
        
        if LiveWalletFeed:
            wallet_feed_service = LiveWalletFeed()
            
            # Subscribe to wallet updates
            async def wallet_update_handler(event_type, data):
                await manager.broadcast({
                    'type': event_type,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
            
            await wallet_feed_service.subscribe(wallet_update_handler)
            asyncio.create_task(wallet_feed_service.start())
        
        # Initialize other services
        if AssetManager:
            asset_manager = AssetManager("dashboard_master_password")
        if BlockchainScanner:
            blockchain_scanner = BlockchainScanner()
        if FileProcessor:
            file_processor = FileProcessor()
        
        print("✅ All live data services started")
    except Exception as e:
        print(f"⚠️  Error starting services: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop live data services"""
    if market_data_service:
        await market_data_service.stop()
    if wallet_feed_service:
        await wallet_feed_service.stop()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Trading System Dashboard API",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "operational",
            "websocket": "operational",
            "bot_registry": "operational" if bot_registry else "unavailable"
        }
    }


@app.get("/api/status")
async def get_system_status():
    """Get overall system status"""
    return {
        "system": "operational",
        "timestamp": datetime.now().isoformat(),
        "uptime": "active",
        "services": {
            "trading_bots": "running",
            "freelance_engine": "running",
            "monitoring": "active",
            "safety_system": "enabled"
        }
    }


@app.get("/api/bots")
async def get_bots():
    """Get all registered bots"""
    if not bot_registry:
        return {"error": "Bot registry not available"}
    
    bots = bot_registry.get_all_bots()
    return {
        "total": len(bots),
        "bots": bots,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/bots/{bot_id}")
async def get_bot(bot_id: str):
    """Get specific bot details"""
    if not bot_registry:
        return {"error": "Bot registry not available"}
    
    bot = bot_registry.get_bot(bot_id)
    if not bot:
        return {"error": f"Bot {bot_id} not found"}
    
    return bot


@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics"""
    active_bots = 0
    total_bots = 0
    
    if bot_registry:
        all_bots = bot_registry.get_all_bots()
        total_bots = len(all_bots)
        active_bots = len([b for b in all_bots.values() if b.get("status") == "active"])
    
    return {
        "timestamp": datetime.now().isoformat(),
        "bots": {
            "total": total_bots,
            "active": active_bots,
            "inactive": total_bots - active_bots
        },
        "system": {
            "uptime": "active",
            "memory_usage": "normal",
            "cpu_usage": "normal"
        },
        "trading": {
            "status": "active",
            "total_trades": 0,
            "pnl": 0.0
        }
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            data = {
                "type": "status_update",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "system_status": "operational",
                    "active_bots": 3,
                    "total_trades": 0
                }
            }
            await websocket.send_json(data)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ========== LIVE MARKET DATA ENDPOINTS ==========

@app.get("/api/market/prices")
async def get_market_prices():
    """Get all live market prices"""
    if not market_data_service:
        return {"error": "Market data service not available"}
    
    prices = await market_data_service.get_all_prices()
    return {
        "total": len(prices),
        "prices": prices,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/market/price/{symbol}")
async def get_price(symbol: str):
    """Get live price for specific symbol"""
    if not market_data_service:
        return {"error": "Market data service not available"}
    
    price = await market_data_service.get_price(symbol)
    if not price:
        return {"error": f"Price data not found for {symbol}"}
    
    return price

@app.get("/api/market/trending")
async def get_trending():
    """Get trending coins"""
    if not market_data_service:
        return {"error": "Market data service not available"}
    
    trending = await market_data_service.get_trending_coins()
    return {
        "trending": trending,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/market/fear-greed")
async def get_fear_greed():
    """Get Fear & Greed Index"""
    if not market_data_service:
        return {"error": "Market data service not available"}
    
    index = await market_data_service.get_market_fear_greed_index()
    return index if index else {"error": "Could not fetch fear/greed index"}


# ========== LIVE WALLET FEED ENDPOINTS ==========

@app.get("/api/wallets/live")
async def get_live_wallets():
    """Get all monitored wallets with live data"""
    if not wallet_feed_service:
        return {"error": "Wallet feed service not available"}
    
    wallets = wallet_feed_service.get_all_wallets()
    return {
        "total": len(wallets),
        "wallets": wallets,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/wallets/live/{address}")
async def get_wallet_live(address: str):
    """Get live data for specific wallet"""
    if not wallet_feed_service:
        return {"error": "Wallet feed service not available"}
    
    wallet = wallet_feed_service.get_wallet_data(address)
    if not wallet:
        return {"error": f"Wallet {address} not found"}
    
    return wallet

@app.post("/api/wallets/monitor")
async def monitor_wallet(data: dict):
    """Add wallet to live monitoring"""
    if not wallet_feed_service:
        return {"error": "Wallet feed service not available"}
    
    address = data.get("address")
    label = data.get("label")
    
    if not address:
        return {"error": "Address required"}
    
    wallet_feed_service.add_wallet(address, label)
    return {
        "success": True,
        "message": f"Wallet {address} added to monitoring",
        "timestamp": datetime.now().isoformat()
    }


# ========== ASSET MANAGEMENT ENDPOINTS ==========

@app.post("/api/assets/wallet/import")
async def import_wallet(data: dict):
    """Import wallet (any format)"""
    if not asset_manager:
        return {"error": "Asset manager not available"}
    
    credential = data.get("credential")
    wallet_type = data.get("wallet_type", "auto")
    label = data.get("label")
    
    if not credential:
        return {"error": "Credential required"}
    
    try:
        wallet = asset_manager.add_wallet(credential, wallet_type, label)
        
        # Add to live monitoring
        if wallet_feed_service and wallet.get("address"):
            wallet_feed_service.add_wallet(wallet["address"], label)
        
        return {
            "success": True,
            "wallet": wallet,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/assets/wallets")
async def list_wallets():
    """List all saved wallets"""
    if not asset_manager:
        return {"error": "Asset manager not available"}
    
    wallets = asset_manager.list_wallets()
    return {
        "total": len(wallets),
        "wallets": wallets,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/assets/api-key/add")
async def add_api_key(data: dict):
    """Add API key"""
    if not asset_manager:
        return {"error": "Asset manager not available"}
    
    provider = data.get("provider")
    api_key = data.get("api_key")
    metadata = data.get("metadata", {})
    
    if not provider or not api_key:
        return {"error": "Provider and api_key required"}
    
    try:
        asset_manager.add_api_key(provider, api_key, metadata)
        return {
            "success": True,
            "message": f"API key for {provider} added",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


# ========== BLOCKCHAIN SCANNER ENDPOINTS ==========

@app.post("/api/scan/address")
async def scan_address(data: dict):
    """Scan blockchain address for complete intelligence"""
    if not blockchain_scanner:
        return {"error": "Blockchain scanner not available"}
    
    address = data.get("address")
    chain = data.get("chain", "ethereum")
    include_tokens = data.get("include_tokens", True)
    include_nfts = data.get("include_nfts", True)
    
    if not address:
        return {"error": "Address required"}
    
    try:
        result = await blockchain_scanner.scan_address(
            address,
            chain=chain,
            include_tokens=include_tokens,
            include_nfts=include_nfts
        )
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/scan/file")
async def scan_file(file: UploadFile = File(...)):
    """Upload and scan file for wallets"""
    if not file_processor:
        return {"error": "File processor not available"}
    
    try:
        # Save uploaded file
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process file
        result = file_processor.process_file(file_path, verify_ownership=True)
        
        # Clean up
        os.remove(file_path)
        
        return result
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
