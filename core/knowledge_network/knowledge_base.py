"""
Knowledge Base - Shared AI intelligence across all bots
"""
import json
import time
from pathlib import Path
from typing import Dict, List

class KnowledgeBase:
    def __init__(self, storage_path="data/knowledge/shared_memory.json"):
        self.storage_path = storage_path
        Path(storage_path).parent.mkdir(parents=True, exist_ok=True)
        self.knowledge = self._load()
        self.subscribers = []
    
    def _load(self):
        """Load knowledge from storage"""
        if Path(self.storage_path).exists():
            with open(self.storage_path) as f:
                return json.load(f)
        
        # Initialize empty knowledge base
        return {
            "patterns": [],
            "strategies": [],
            "risk_assessments": [],
            "metadata": {
                "created": time.time(),
                "version": "1.0.0"
            }
        }
    
    def _save(self):
        """Persist knowledge to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def add_pattern(self, pattern: Dict, source_bot: str):
        """
        Add learned pattern to knowledge base
        Pattern will be shared with all bots
        """
        entry = {
            "pattern": pattern,
            "source": source_bot,
            "timestamp": time.time(),
            "validated": False,
            "confirmations": 1
        }
        
        self.knowledge["patterns"].append(entry)
        self._save()
        
        # Broadcast to all connected bots
        self.broadcast({"type": "new_pattern", "data": entry})
        
        print(f"✓ Pattern added from {source_bot}")
        return entry
    
    def validate_pattern(self, pattern_id: int, bot_id: str):
        """Bot confirms a pattern (consensus mechanism)"""
        if pattern_id < len(self.knowledge["patterns"]):
            self.knowledge["patterns"][pattern_id]["confirmations"] += 1
            
            # Mark as validated if 3+ bots confirm
            if self.knowledge["patterns"][pattern_id]["confirmations"] >= 3:
                self.knowledge["patterns"][pattern_id]["validated"] = True
                print(f"✓ Pattern {pattern_id} validated by consensus")
            
            self._save()
    
    def broadcast(self, data: Dict):
        """Send to all connected bots"""
        for subscriber in self.subscribers:
            subscriber.receive(data)
    
    def subscribe(self, bot):
        """Bot subscribes to knowledge updates"""
        self.subscribers.append(bot)
        print(f"✓ Bot subscribed to knowledge network")
    
    def query(self, query_type: str):
        """Query knowledge base"""
        if query_type == "patterns":
            return [p for p in self.knowledge["patterns"] if p.get("validated")]
        elif query_type == "strategies":
            return self.knowledge["strategies"]
        elif query_type == "all":
            return self.knowledge
        return []
    
    def get_stats(self):
        """Get knowledge base statistics"""
        return {
            "total_patterns": len(self.knowledge["patterns"]),
            "validated_patterns": len([p for p in self.knowledge["patterns"] if p.get("validated")]),
            "total_strategies": len(self.knowledge["strategies"]),
            "subscribers": len(self.subscribers)
        }
