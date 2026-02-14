"""
BOT REGISTRY
Central registry for all discovered and registered bots in the system.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class BotRegistry:
    """Central registry for bot management."""
    
    def __init__(self):
        self.config_dir = Path("/home/runner/work/The-basics/The-basics/config")
        self.config_dir.mkdir(exist_ok=True)
        
        self.registry_file = self.config_dir / "bot_registry.json"
        self.registry: Dict[str, Any] = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load bot registry from file."""
        if self.registry_file.exists():
            return json.loads(self.registry_file.read_text())
        return {
            "bots": {},
            "last_updated": datetime.now().isoformat(),
            "total_registered": 0
        }
    
    def _save_registry(self) -> None:
        """Save bot registry to file."""
        self.registry["last_updated"] = datetime.now().isoformat()
        self.registry["total_registered"] = len(self.registry["bots"])
        self.registry_file.write_text(json.dumps(self.registry, indent=2))
    
    def register_bot(
        self,
        bot_id: str,
        name: str,
        bot_type: str,
        file_path: str,
        capabilities: Optional[List[str]] = None,
        config: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Register a new bot in the system.
        
        Args:
            bot_id: Unique identifier for the bot
            name: Human-readable name
            bot_type: Type of bot (trading, monitoring, recovery, etc.)
            file_path: Path to bot file
            capabilities: List of bot capabilities
            config: Bot configuration
            metadata: Additional metadata
            
        Returns:
            Registration result
        """
        if bot_id in self.registry["bots"]:
            print(f"⚠️ Bot {bot_id} already registered, updating...")
        
        self.registry["bots"][bot_id] = {
            "bot_id": bot_id,
            "name": name,
            "type": bot_type,
            "file_path": file_path,
            "capabilities": capabilities or [],
            "config": config or {},
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "status": "registered",
            "last_seen": datetime.now().isoformat()
        }
        
        self._save_registry()
        
        print(f"✅ Registered bot: {name} ({bot_id})")
        
        return self.registry["bots"][bot_id]
    
    def get_bot(self, bot_id: str) -> Optional[Dict]:
        """Get bot information by ID."""
        return self.registry["bots"].get(bot_id)
    
    def get_all_bots(self) -> List[Dict]:
        """Get all registered bots."""
        return list(self.registry["bots"].values())
    
    def get_bots_by_type(self, bot_type: str) -> List[Dict]:
        """Get all bots of a specific type."""
        return [
            bot for bot in self.registry["bots"].values()
            if bot.get("type") == bot_type
        ]
    
    def update_bot_status(self, bot_id: str, status: str) -> bool:
        """Update bot status."""
        if bot_id in self.registry["bots"]:
            self.registry["bots"][bot_id]["status"] = status
            self.registry["bots"][bot_id]["last_seen"] = datetime.now().isoformat()
            self._save_registry()
            return True
        return False
    
    def unregister_bot(self, bot_id: str) -> bool:
        """Unregister a bot."""
        if bot_id in self.registry["bots"]:
            del self.registry["bots"][bot_id]
            self._save_registry()
            print(f"🗑️ Unregistered bot: {bot_id}")
            return True
        return False
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        bots_by_type = {}
        for bot in self.registry["bots"].values():
            bot_type = bot.get("type", "unknown")
            bots_by_type[bot_type] = bots_by_type.get(bot_type, 0) + 1
        
        return {
            "total_bots": len(self.registry["bots"]),
            "bots_by_type": bots_by_type,
            "last_updated": self.registry["last_updated"]
        }


# Global instance
bot_registry = BotRegistry()


def main():
    """Test bot registry."""
    # Register some test bots
    bot_registry.register_bot(
        bot_id="quantum_bot_1",
        name="Quantum Bot",
        bot_type="trading",
        file_path="backend/quantum_bot.py",
        capabilities=["trading", "quantum_analysis"],
        config={"exchange": "NDAX"}
    )
    
    bot_registry.register_bot(
        bot_id="shadowforge_bot_1",
        name="ShadowForge Bot",
        bot_type="ai_trader",
        file_path="backend/shadowforge_bot.py",
        capabilities=["ai_trading", "pattern_recognition"]
    )
    
    # Get stats
    stats = bot_registry.get_registry_stats()
    print(f"\n📊 Registry Stats:")
    print(f"  • Total bots: {stats['total_bots']}")
    print(f"  • Bots by type: {stats['bots_by_type']}")
    
    # Get all bots
    all_bots = bot_registry.get_all_bots()
    print(f"\n🤖 All Registered Bots:")
    for bot in all_bots:
        print(f"  • {bot['name']} ({bot['type']})")


if __name__ == "__main__":
    main()
