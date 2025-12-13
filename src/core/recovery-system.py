#!/usr/bin/env python3
"""
recovery-system.py - System State Persistence and Auto-Recovery

Provides checkpoint/restore functionality, database connection recovery,
API retry logic, and transaction rollback handling for The-basics system.
"""

import json
import os
import sys
import time
import pickle
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import wraps
import asyncio
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RecoverySystem')


@dataclass
class Checkpoint:
    """System checkpoint state"""
    timestamp: str
    state_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self):
        return asdict(self)


class RecoverySystem:
    """
    Comprehensive recovery system for handling crashes, connection failures,
    and state restoration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.checkpoint_dir = Path(self.config.get(
            'checkpoint_dir',
            '.unified-system/checkpoints'
        ))
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_db = self.checkpoint_dir / 'state.db'
        self.max_checkpoints = self.config.get('max_checkpoints', 10)
        self.retry_attempts = self.config.get('retry_attempts', 3)
        self.retry_delay = self.config.get('retry_delay', 5)
        
        self._init_database()
        logger.info("RecoverySystem initialized")
    
    def _init_database(self):
        """Initialize SQLite database for state persistence"""
        conn = sqlite3.connect(str(self.state_db))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                state_type TEXT NOT NULL,
                data TEXT NOT NULL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recovery_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                recovery_type TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Recovery database initialized")
    
    def create_checkpoint(self, state_type: str, data: Dict[str, Any], 
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a checkpoint of current system state
        
        Args:
            state_type: Type of state being saved (e.g., 'trading', 'ai_job', 'system')
            data: State data to checkpoint
            metadata: Optional metadata about the checkpoint
        
        Returns:
            bool: Success status
        """
        try:
            checkpoint = Checkpoint(
                timestamp=datetime.now().isoformat(),
                state_type=state_type,
                data=data,
                metadata=metadata or {}
            )
            
            conn = sqlite3.connect(str(self.state_db))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO checkpoints (timestamp, state_type, data, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                checkpoint.timestamp,
                checkpoint.state_type,
                json.dumps(checkpoint.data),
                json.dumps(checkpoint.metadata)
            ))
            
            conn.commit()
            checkpoint_id = cursor.lastrowid
            conn.close()
            
            # Clean up old checkpoints
            self._cleanup_old_checkpoints(state_type)
            
            logger.info(f"Checkpoint created: {state_type} (ID: {checkpoint_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def restore_checkpoint(self, state_type: str, 
                          timestamp: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Restore system state from checkpoint
        
        Args:
            state_type: Type of state to restore
            timestamp: Specific timestamp to restore (None = latest)
        
        Returns:
            Dict with restored state data or None if not found
        """
        try:
            conn = sqlite3.connect(str(self.state_db))
            cursor = conn.cursor()
            
            if timestamp:
                cursor.execute('''
                    SELECT data, metadata FROM checkpoints
                    WHERE state_type = ? AND timestamp = ?
                    ORDER BY created_at DESC LIMIT 1
                ''', (state_type, timestamp))
            else:
                cursor.execute('''
                    SELECT data, metadata FROM checkpoints
                    WHERE state_type = ?
                    ORDER BY created_at DESC LIMIT 1
                ''', (state_type,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                data = json.loads(result[0])
                metadata = json.loads(result[1]) if result[1] else {}
                
                self._log_recovery(state_type, 'checkpoint_restore', 'success', 
                                  f"Restored from checkpoint")
                
                logger.info(f"Checkpoint restored: {state_type}")
                return {
                    'data': data,
                    'metadata': metadata
                }
            else:
                logger.warning(f"No checkpoint found for: {state_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to restore checkpoint: {e}")
            logger.error(traceback.format_exc())
            self._log_recovery(state_type, 'checkpoint_restore', 'failed', str(e))
            return None
    
    def _cleanup_old_checkpoints(self, state_type: str):
        """Remove old checkpoints beyond max_checkpoints limit"""
        try:
            conn = sqlite3.connect(str(self.state_db))
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM checkpoints
                WHERE id IN (
                    SELECT id FROM checkpoints
                    WHERE state_type = ?
                    ORDER BY created_at DESC
                    LIMIT -1 OFFSET ?
                )
            ''', (state_type, self.max_checkpoints))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted > 0:
                logger.debug(f"Cleaned up {deleted} old checkpoints for {state_type}")
                
        except Exception as e:
            logger.error(f"Checkpoint cleanup failed: {e}")
    
    def _log_recovery(self, recovery_type: str, action: str, status: str, details: str):
        """Log recovery actions"""
        try:
            conn = sqlite3.connect(str(self.state_db))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO recovery_log (timestamp, recovery_type, status, details)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                f"{recovery_type}:{action}",
                status,
                details
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to log recovery action: {e}")
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with exponential backoff retry logic
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function
        
        Returns:
            Function result or raises last exception
        """
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Retry successful on attempt {attempt + 1}")
                    self._log_recovery('retry', func.__name__, 'success', 
                                      f"Succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                delay = self.retry_delay * (2 ** attempt)
                
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.retry_attempts - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
        
        # All retries failed
        self._log_recovery('retry', func.__name__, 'failed', 
                          f"All {self.retry_attempts} attempts failed: {last_exception}")
        raise last_exception
    
    async def async_retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """Async version of retry_with_backoff"""
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                result = await func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Async retry successful on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                delay = self.retry_delay * (2 ** attempt)
                
                logger.warning(f"Async attempt {attempt + 1} failed: {e}")
                
                if attempt < self.retry_attempts - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
        
        raise last_exception
    
    def with_transaction_rollback(self, func: Callable, connection) -> Any:
        """
        Execute database operation with automatic rollback on failure
        
        Args:
            func: Function that performs database operations
            connection: Database connection object
        
        Returns:
            Function result
        """
        try:
            # Start transaction
            if hasattr(connection, 'begin'):
                connection.begin()
            
            result = func(connection)
            
            # Commit transaction
            if hasattr(connection, 'commit'):
                connection.commit()
            
            logger.debug("Transaction committed successfully")
            return result
            
        except Exception as e:
            # Rollback on error
            if hasattr(connection, 'rollback'):
                connection.rollback()
                logger.warning(f"Transaction rolled back due to error: {e}")
            
            self._log_recovery('transaction', func.__name__, 'rollback', str(e))
            raise
    
    def get_recovery_log(self, limit: int = 50) -> list:
        """Get recent recovery log entries"""
        try:
            conn = sqlite3.connect(str(self.state_db))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, recovery_type, status, details
                FROM recovery_log
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            logs = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'timestamp': log[0],
                    'type': log[1],
                    'status': log[2],
                    'details': log[3]
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Failed to get recovery log: {e}")
            return []
    
    def get_checkpoint_history(self, state_type: str, limit: int = 10) -> list:
        """Get checkpoint history for a specific state type"""
        try:
            conn = sqlite3.connect(str(self.state_db))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, metadata, created_at
                FROM checkpoints
                WHERE state_type = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (state_type, limit))
            
            checkpoints = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'timestamp': cp[0],
                    'metadata': json.loads(cp[1]) if cp[1] else {},
                    'created_at': cp[2]
                }
                for cp in checkpoints
            ]
            
        except Exception as e:
            logger.error(f"Failed to get checkpoint history: {e}")
            return []


# Decorator for automatic checkpointing
def auto_checkpoint(state_type: str, recovery_system: Optional[RecoverySystem] = None):
    """Decorator to automatically checkpoint function state"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            rs = recovery_system or RecoverySystem()
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Create checkpoint on success
                rs.create_checkpoint(
                    state_type,
                    {'result': str(result)[:1000]},  # Limit size
                    {'function': func.__name__, 'status': 'success'}
                )
                
                return result
                
            except Exception as e:
                # Create checkpoint on failure
                rs.create_checkpoint(
                    state_type,
                    {'error': str(e)},
                    {'function': func.__name__, 'status': 'failed'}
                )
                raise
        
        return wrapper
    return decorator


if __name__ == '__main__':
    # Test the recovery system
    rs = RecoverySystem()
    
    # Create test checkpoint
    rs.create_checkpoint('test', {'key': 'value'}, {'test': True})
    
    # Restore checkpoint
    restored = rs.restore_checkpoint('test')
    print("Restored:", restored)
    
    # Test retry logic
    attempt_count = 0
    def failing_func():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise Exception(f"Attempt {attempt_count} failed")
        return "Success!"
    
    try:
        result = rs.retry_with_backoff(failing_func)
        print("Retry result:", result)
    except Exception as e:
        print("Retry failed:", e)
    
    # Get logs
    logs = rs.get_recovery_log()
    print(f"Recovery logs: {len(logs)} entries")
