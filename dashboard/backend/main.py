"""
DASHBOARD BACKEND - FastAPI Server
Real-time WebSocket updates, REST API for bot control.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.bot_registry import bot_registry
from backend.bot_credential_sharing import credential_sharing
from backend.email_notifier import email_notifier
from backend.complete_asset_recovery_system import asset_recovery
from backend.autonomous_sync import autonomous_sync

# Create FastAPI app
app = FastAPI(
    title="Autonomous Bot Dashboard API",
    description="Real-time dashboard API for autonomous bot system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")

manager = ConnectionManager()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Autonomous Bot Dashboard API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "bot_registry": "operational",
            "credential_sharing": "operational",
            "email_notifier": "operational",
            "asset_recovery": "operational"
        }
    }


@app.get("/api/bots")
async def get_bots():
    """Get all registered bots."""
    bots = bot_registry.get_all_bots()
    return {
        "total": len(bots),
        "bots": bots
    }


@app.get("/api/bots/{bot_id}")
async def get_bot(bot_id: str):
    """Get specific bot details."""
    bot = bot_registry.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot


@app.post("/api/bots/{bot_id}/{action}")
async def control_bot(bot_id: str, action: str):
    """Control a bot (start, stop, restart)."""
    if action not in ["start", "stop", "restart"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    bot = bot_registry.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Update bot status
    new_status = "active" if action == "start" else "inactive"
    bot_registry.update_bot_status(bot_id, new_status)
    
    # Broadcast update
    await manager.broadcast({
        "type": "bot_status_update",
        "bot_id": bot_id,
        "status": new_status,
        "action": action,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "success": True,
        "bot_id": bot_id,
        "action": action,
        "new_status": new_status
    }


@app.get("/api/stats")
async def get_stats():
    """Get system statistics."""
    bot_stats = bot_registry.get_registry_stats()
    cred_stats = credential_sharing.get_shared_pool_status()
    recovery_stats = asset_recovery.get_recovery_stats()
    notif_stats = email_notifier.get_notification_stats()
    
    return {
        "bots": bot_stats,
        "credentials": cred_stats,
        "recovery": recovery_stats,
        "notifications": notif_stats,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/credentials")
async def get_credentials():
    """Get credential pool status."""
    return credential_sharing.get_shared_pool_status()


@app.get("/api/recovery")
async def get_recovery_status():
    """Get asset recovery status."""
    return asset_recovery.get_recovery_stats()


@app.get("/api/notifications")
async def get_notifications():
    """Get notification status."""
    pending = email_notifier.get_pending_notifications()
    stats = email_notifier.get_notification_stats()
    
    return {
        "pending": len(pending),
        "pending_list": pending,
        "stats": stats
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    
    try:
        # Send initial data
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to dashboard",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message.get("type") == "subscribe":
                # Subscribe to specific updates
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": message.get("channel"),
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_updates():
    """Background task to broadcast periodic updates."""
    while True:
        try:
            # Get latest stats
            stats = {
                "type": "stats_update",
                "data": {
                    "bots": bot_registry.get_registry_stats(),
                    "credentials": credential_sharing.get_shared_pool_status(),
                    "recovery": asset_recovery.get_recovery_stats(),
                    "notifications": email_notifier.get_notification_stats()
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Broadcast to all connected clients
            await manager.broadcast(stats)
            
            # Wait 5 seconds before next broadcast
            await asyncio.sleep(5)
        
        except Exception as e:
            print(f"Broadcast error: {e}")
            await asyncio.sleep(5)


@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup."""
    asyncio.create_task(broadcast_updates())
    print("🚀 Dashboard API started")
    print("   • WebSocket: ws://localhost:8000/ws")
    print("   • API Docs: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 Dashboard API shutting down")


if __name__ == "__main__":
    import uvicorn
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║            🖥️  AUTONOMOUS BOT DASHBOARD API                 ║
║                                                              ║
║  Starting server...                                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
