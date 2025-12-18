# AI Knowledge Network

## Overview
Distributed intelligence system where all 10 bots share learned patterns in real-time.

## How It Works

1. **Bot learns pattern**: Bot-1 discovers profitable trading pattern
2. **Adds to knowledge base**: Pattern stored in shared memory
3. **Broadcast to network**: All bots (2-10) receive pattern instantly
4. **Consensus validation**: Pattern marked valid when 3+ bots confirm
5. **Collective learning**: All bots improve together

## Quick Start

```python
from core.knowledge_network.knowledge_base import KnowledgeBase

kb = KnowledgeBase()

# Bot adds learned pattern
pattern = {"type": "bullish_breakout", "confidence": 0.85}
kb.add_pattern(pattern, "Bot-1")

# Other bots query knowledge
patterns = kb.query("patterns")
```

## Real-Time Sync

```python
from core.knowledge_network.sync_engine import SyncEngine

sync = SyncEngine()

# Connect bot to network
await sync.connect_bot("Bot-1")

# Broadcast message
await sync.broadcast_message(
    {"type": "new_pattern", "data": pattern},
    "Bot-1"
)
```

## Consensus Protocol

Patterns require 3+ bot confirmations:
```python
# Bot validates pattern
kb.validate_pattern(pattern_id=0, bot_id="Bot-2")
kb.validate_pattern(pattern_id=0, bot_id="Bot-3")
kb.validate_pattern(pattern_id=0, bot_id="Bot-4")
# Now validated = True
```

## Knowledge Types

- **Patterns**: Trading patterns (breakouts, reversals, etc.)
- **Strategies**: Proven trading strategies
- **Risk Assessments**: Risk analysis data

## Architecture

```
Bot-1 learns pattern
       ↓
Knowledge Base (validates)
       ↓
Sync Engine (broadcasts <100ms)
       ↓
Bot-2, Bot-3, ..., Bot-10 receive
```
