"""
Test AI knowledge network
"""
import sys
sys.path.append('..')

from core.knowledge_network.knowledge_base import KnowledgeBase

def test_knowledge_base():
    kb = KnowledgeBase(storage_path="/tmp/test_knowledge.json")
    
    # Add pattern
    pattern = {"type": "test", "confidence": 0.9}
    entry = kb.add_pattern(pattern, "Bot-1")
    
    assert entry['source'] == "Bot-1"
    assert entry['confirmations'] == 1
    
    # Validate pattern
    kb.validate_pattern(0, "Bot-2")
    kb.validate_pattern(0, "Bot-3")
    kb.validate_pattern(0, "Bot-4")
    
    assert kb.knowledge['patterns'][0]['validated'] == True
    
    print("✅ All knowledge network tests passed")

if __name__ == "__main__":
    test_knowledge_base()
