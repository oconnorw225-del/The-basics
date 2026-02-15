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
except ImportError:
    BotRegistry = None

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
