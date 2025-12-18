"""
Sync Engine - Real-time synchronization between bots
"""
import asyncio
import json
import time
from typing import Dict, Set

class SyncEngine:
    def __init__(self):
        self.connected_bots: Set[str] = set()
        self.message_queue = []
        self.sync_interval = 5  # seconds
    
    async def connect_bot(self, bot_id: str):
        """Connect a bot to the sync network"""
        self.connected_bots.add(bot_id)
        print(f"✓ {bot_id} connected to sync network")
        
        # Send current state to new bot
        await self.sync_bot(bot_id)
    
    async def disconnect_bot(self, bot_id: str):
        """Disconnect bot"""
        if bot_id in self.connected_bots:
            self.connected_bots.remove(bot_id)
            print(f"✓ {bot_id} disconnected")
    
    async def broadcast_message(self, message: Dict, sender: str):
        """Broadcast message to all bots except sender"""
        message["timestamp"] = time.time()
        message["sender"] = sender
        
        # Add to queue
        self.message_queue.append(message)
        
        # Send to all bots
        for bot_id in self.connected_bots:
            if bot_id != sender:
                await self.send_to_bot(bot_id, message)
    
    async def send_to_bot(self, bot_id: str, message: Dict):
        """Send message to specific bot"""
        # In production, this would use WebSocket or similar
        print(f"→ Sent to {bot_id}: {message['type']}")
    
    async def sync_bot(self, bot_id: str):
        """Sync bot with current knowledge"""
        print(f"Syncing {bot_id}...")
    
    async def run_sync_loop(self):
        """Continuous sync loop"""
        while True:
            await asyncio.sleep(self.sync_interval)
            
            if self.connected_bots:
                print(f"Sync: {len(self.connected_bots)} bots connected")
    
    def get_status(self):
        """Get sync status"""
        return {
            "connected_bots": list(self.connected_bots),
            "message_queue_size": len(self.message_queue),
            "sync_interval": self.sync_interval
        }
