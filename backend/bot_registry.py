#!/usr/bin/env python3
"""
Bot Registry - Central registration and discovery system for all bots
Tracks bot status, health, and capabilities
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Hardcoded path for GitHub Actions compatibility
BASE_PATH = "/home/runner/work/The-basics/The-basics"
REGISTRY_FILE = os.path.join(BASE_PATH, "backend", "bot_registry.json")


class BotRegistry:
    """Central registry for all trading and freelance bots"""
    
    def __init__(self):
        self.bots = {}
        self.load_registry()
    
    def load_registry(self):
        """Load existing registry from file"""
        if os.path.exists(REGISTRY_FILE):
            try:
                with open(REGISTRY_FILE, 'r') as f:
                    self.bots = json.load(f)
            except Exception as e:
                print(f"Error loading registry: {e}")
                self.bots = {}
        else:
            self.initialize_default_bots()
    
    def save_registry(self):
        """Save registry to file"""
        try:
            os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
            with open(REGISTRY_FILE, 'w') as f:
                json.dump(self.bots, f, indent=2)
        except Exception as e:
            print(f"Error saving registry: {e}")
    
    def initialize_default_bots(self):
        """Initialize with default bot configurations"""
        self.bots = {
            "ndax_bot": {
                "name": "NDAX Trading Bot",
                "type": "trading",
                "status": "inactive",
                "port": 9000,
                "health_endpoint": "/health",
                "capabilities": ["spot_trading", "market_orders", "limit_orders"],
                "last_seen": None
            },
            "quantum_bot": {
                "name": "Quantum Bot",
                "type": "trading",
                "status": "inactive",
                "port": None,
                "health_endpoint": None,
                "capabilities": ["quantum_strategies", "pattern_recognition"],
                "last_seen": None
            },
            "shadowforge_bot": {
                "name": "ShadowForge Bot",
                "type": "trading",
                "status": "inactive",
                "port": None,
                "health_endpoint": None,
                "capabilities": ["ai_trading", "ml_predictions"],
                "last_seen": None
            }
        }
        self.save_registry()
    
    def register_bot(self, bot_id: str, config: Dict) -> bool:
        """Register a new bot or update existing registration"""
        try:
            self.bots[bot_id] = {
                **config,
                "registered_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self.save_registry()
            return True
        except Exception as e:
            print(f"Error registering bot {bot_id}: {e}")
            return False
    
    def update_status(self, bot_id: str, status: str, health_data: Optional[Dict] = None):
        """Update bot status and health data"""
        if bot_id in self.bots:
            self.bots[bot_id]["status"] = status
            self.bots[bot_id]["last_seen"] = datetime.now().isoformat()
            if health_data:
                self.bots[bot_id]["health"] = health_data
            self.save_registry()
    
    def get_bot(self, bot_id: str) -> Optional[Dict]:
        """Get bot configuration"""
        return self.bots.get(bot_id)
    
    def get_all_bots(self) -> Dict:
        """Get all registered bots"""
        return self.bots
    
    def get_active_bots(self) -> List[str]:
        """Get list of active bot IDs"""
        return [
            bot_id for bot_id, config in self.bots.items()
            if config.get("status") == "active"
        ]
    
    def get_bots_by_type(self, bot_type: str) -> Dict:
        """Get all bots of a specific type"""
        return {
            bot_id: config for bot_id, config in self.bots.items()
            if config.get("type") == bot_type
        }


if __name__ == "__main__":
    # Initialize and test registry
    registry = BotRegistry()
    print("Bot Registry initialized")
    print(f"Registered bots: {len(registry.get_all_bots())}")
    for bot_id, config in registry.get_all_bots().items():
        print(f"  - {bot_id}: {config['name']} ({config['status']})")
