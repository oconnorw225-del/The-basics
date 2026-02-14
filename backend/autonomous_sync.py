"""
AUTONOMOUS SYNC
Syncs bot state across the system for coordination and shared memory.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class AutonomousSync:
    """Synchronizes state across all autonomous bots."""
    
    def __init__(self):
        self.sync_dir = Path("/home/runner/work/The-basics/The-basics/config/sync")
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.sync_dir / "bot_states.json"
        self.shared_memory_file = self.sync_dir / "shared_memory.json"
        
        self.bot_states: Dict[str, Any] = self._load_states()
        self.shared_memory: Dict[str, Any] = self._load_shared_memory()
    
    def _load_states(self) -> Dict[str, Any]:
        """Load bot states."""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {}
    
    def _save_states(self) -> None:
        """Save bot states."""
        self.state_file.write_text(json.dumps(self.bot_states, indent=2))
    
    def _load_shared_memory(self) -> Dict[str, Any]:
        """Load shared memory."""
        if self.shared_memory_file.exists():
            return json.loads(self.shared_memory_file.read_text())
        return {
            "last_sync": datetime.now().isoformat(),
            "data": {}
        }
    
    def _save_shared_memory(self) -> None:
        """Save shared memory."""
        self.shared_memory["last_sync"] = datetime.now().isoformat()
        self.shared_memory_file.write_text(json.dumps(self.shared_memory, indent=2))
    
    def update_bot_state(self, bot_id: str, state: Dict[str, Any]) -> None:
        """Update a bot's state."""
        self.bot_states[bot_id] = {
            **state,
            "last_updated": datetime.now().isoformat()
        }
        self._save_states()
    
    def get_bot_state(self, bot_id: str) -> Optional[Dict]:
        """Get a bot's current state."""
        return self.bot_states.get(bot_id)
    
    def write_to_shared_memory(self, key: str, value: Any, bot_id: str) -> None:
        """Write data to shared memory."""
        self.shared_memory["data"][key] = {
            "value": value,
            "written_by": bot_id,
            "written_at": datetime.now().isoformat()
        }
        self._save_shared_memory()
    
    def read_from_shared_memory(self, key: str) -> Optional[Any]:
        """Read data from shared memory."""
        data = self.shared_memory["data"].get(key)
        return data["value"] if data else None
    
    async def sync_all_bots(self) -> Dict[str, Any]:
        """Sync all bot states."""
        return {
            "synced_bots": len(self.bot_states),
            "shared_memory_keys": len(self.shared_memory["data"]),
            "last_sync": datetime.now().isoformat()
        }


# Global instance
autonomous_sync = AutonomousSync()
