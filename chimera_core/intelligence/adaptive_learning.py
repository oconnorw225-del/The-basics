"""
Adaptive Learning System - Critical Gap #3 (ML Pipeline)
Fast-learning AI system that adapts to market conditions
Uses experience replay and pattern recognition
"""

import logging
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import json

logger = logging.getLogger(__name__)


@dataclass
class Experience:
    """Single learning experience"""
    timestamp: datetime
    context: Dict[str, Any]  # Market state, indicators, etc.
    action: str  # What action was taken
    outcome: Dict[str, Any]  # Result of the action
    success: bool  # Was it profitable/successful?
    reward: float  # Quantified reward (e.g., profit)
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'action': self.action,
            'outcome': self.outcome,
            'success': self.success,
            'reward': self.reward
        }


class AdaptiveIntelligence:
    """Lightweight adaptive learning system"""
    
    def __init__(self, db=None):
        self.db = db
        self.short_term_memory: deque = deque(maxlen=1000)  # Recent experiences
        self.long_term_patterns: Dict[str, List] = {}  # Learned patterns
        self.action_success_rates: Dict[str, Dict] = {}  # Track success by action
        self.context_patterns: Dict[str, int] = {}  # Frequency of contexts
        
    async def learn_from_experience(self, experience: Experience):
        """Learn from a single experience"""
        # Add to short-term memory
        self.short_term_memory.append(experience)
        
        # Update action success rates
        action = experience.action
        if action not in self.action_success_rates:
            self.action_success_rates[action] = {
                'total': 0,
                'successful': 0,
                'total_reward': 0.0
            }
        
        self.action_success_rates[action]['total'] += 1
        if experience.success:
            self.action_success_rates[action]['successful'] += 1
        self.action_success_rates[action]['total_reward'] += experience.reward
        
        # Extract and store patterns
        pattern_key = self._context_to_pattern(experience.context)
        self.context_patterns[pattern_key] = self.context_patterns.get(pattern_key, 0) + 1
        
        # Store in database if available
        if self.db:
            try:
                await self.db.log_event(
                    'learning',
                    'adaptive_ai',
                    'info',
                    f"Learned from {action}: {'success' if experience.success else 'failure'}",
                    metadata=experience.to_dict()
                )
            except:
                pass
        
        logger.debug(f"📚 Learned from {action}: reward={experience.reward:.4f}")
    
    async def decide_action(self, context: Dict[str, Any]) -> Tuple[str, float]:
        """
        Decide on an action based on current context
        Returns: (action, confidence)
        """
        # Pattern matching
        pattern = self._context_to_pattern(context)
        
        # Check if we've seen similar patterns
        if pattern in self.context_patterns:
            # We have experience with this pattern
            relevant_experiences = [
                exp for exp in self.short_term_memory
                if self._context_to_pattern(exp.context) == pattern
            ]
            
            if relevant_experiences:
                # Use historical success rate
                successful = sum(1 for exp in relevant_experiences if exp.success)
                confidence = successful / len(relevant_experiences)
                
                # Find best action for this pattern
                action_rewards = {}
                for exp in relevant_experiences:
                    if exp.action not in action_rewards:
                        action_rewards[exp.action] = []
                    action_rewards[exp.action].append(exp.reward)
                
                if action_rewards:
                    best_action = max(
                        action_rewards.items(),
                        key=lambda x: sum(x[1]) / len(x[1])
                    )[0]
                    
                    return best_action, confidence
        
        # No clear pattern - use overall success rates
        if self.action_success_rates:
            best_action = max(
                self.action_success_rates.items(),
                key=lambda x: x[1]['successful'] / max(x[1]['total'], 1)
            )[0]
            
            stats = self.action_success_rates[best_action]
            confidence = stats['successful'] / max(stats['total'], 1)
            
            return best_action, confidence
        
        # No experience yet - conservative approach
        return 'wait', 0.0
    
    def _context_to_pattern(self, context: Dict[str, Any]) -> str:
        """Convert context to pattern key"""
        # Simplified pattern extraction
        # In production, this would use more sophisticated feature extraction
        pattern_parts = []
        
        if 'price' in context:
            # Bucket price into ranges
            price = context['price']
            price_range = int(price / 1000) * 1000
            pattern_parts.append(f"price_{price_range}")
        
        if 'hour' in context:
            pattern_parts.append(f"hour_{context['hour']}")
        
        if 'day_of_week' in context:
            pattern_parts.append(f"dow_{context['day_of_week']}")
        
        return "|".join(pattern_parts) if pattern_parts else "unknown"
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        total_experiences = len(self.short_term_memory)
        successful = sum(1 for exp in self.short_term_memory if exp.success)
        
        return {
            'short_term_experiences': total_experiences,
            'success_rate': successful / max(total_experiences, 1),
            'patterns_learned': len(self.context_patterns),
            'actions_tracked': len(self.action_success_rates),
            'total_reward': sum(exp.reward for exp in self.short_term_memory)
        }
    
    async def save_state(self, filepath: str):
        """Save learning state to file"""
        state = {
            'short_term_memory': [exp.to_dict() for exp in self.short_term_memory],
            'long_term_patterns': self.long_term_patterns,
            'action_success_rates': self.action_success_rates,
            'context_patterns': self.context_patterns
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(state, f)
        
        logger.info(f"💾 Learning state saved to {filepath}")
    
    async def load_state(self, filepath: str):
        """Load learning state from file"""
        with open(filepath, 'rb') as f:
            state = pickle.load(f)
        
        # Reconstruct experiences
        self.short_term_memory = deque(maxlen=1000)
        for exp_dict in state.get('short_term_memory', []):
            exp = Experience(
                timestamp=datetime.fromisoformat(exp_dict['timestamp']),
                context=exp_dict['context'],
                action=exp_dict['action'],
                outcome=exp_dict['outcome'],
                success=exp_dict['success'],
                reward=exp_dict['reward']
            )
            self.short_term_memory.append(exp)
        
        self.long_term_patterns = state.get('long_term_patterns', {})
        self.action_success_rates = state.get('action_success_rates', {})
        self.context_patterns = state.get('context_patterns', {})
        
        logger.info(f"📚 Learning state loaded from {filepath}")
