#!/usr/bin/env python3
"""
Crash Detection and Recovery
Handles unexpected failures and automatic recovery
"""

import os
import signal
import time
import psutil
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum


class RecoveryStrategy(Enum):
    """Recovery strategies"""
    RESTART = "restart"
    RESTART_WITH_BACKOFF = "restart_with_backoff"
    FAILOVER = "failover"
    CIRCUIT_BREAKER = "circuit_breaker"
    NONE = "none"


class CrashHandler:
    """
    Crash detection and recovery system.
    Handles unexpected failures and implements recovery strategies.
    """
    
    def __init__(
        self,
        logger=None,
        process_manager=None,
        max_crash_retries: int = 3,
        retry_backoff_base: float = 2.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 300
    ):
        """
        Initialize crash handler.
        
        Args:
            logger: Logger instance
            process_manager: Process manager instance
            max_crash_retries: Maximum crash recovery attempts
            retry_backoff_base: Base for exponential backoff
            circuit_breaker_threshold: Crashes before circuit opens
            circuit_breaker_timeout: Circuit breaker timeout (seconds)
        """
        self.logger = logger
        self.process_manager = process_manager
        self.max_crash_retries = max_crash_retries
        self.retry_backoff_base = retry_backoff_base
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        
        # Crash tracking
        self.crash_history: Dict[str, List[datetime]] = {}
        self.retry_counts: Dict[str, int] = {}
        self.circuit_open: Dict[str, datetime] = {}
        
        # Recovery strategies per process
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        
        # Checkpoint storage
        self.checkpoint_dir = Path(".unified-system/checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Notification callbacks
        self.notification_callbacks: List[Callable] = []
    
    def register_process(
        self,
        process_name: str,
        strategy: RecoveryStrategy = RecoveryStrategy.RESTART_WITH_BACKOFF
    ):
        """
        Register a process for crash recovery.
        
        Args:
            process_name: Process name
            strategy: Recovery strategy to use
        """
        self.recovery_strategies[process_name] = strategy
        self.crash_history[process_name] = []
        self.retry_counts[process_name] = 0
        
        if self.logger:
            self.logger.info(
                f"Registered crash recovery for {process_name} "
                f"with strategy: {strategy.value}"
            )
    
    def handle_crash(
        self,
        process_name: str,
        exit_code: Optional[int] = None,
        error: Optional[Exception] = None
    ) -> Dict[str, Any]:
        """
        Handle a process crash.
        
        Args:
            process_name: Name of crashed process
            exit_code: Process exit code
            error: Exception that caused crash
            
        Returns:
            Recovery result
        """
        if self.logger:
            self.logger.error(
                f"Process crashed: {process_name} "
                f"(exit code: {exit_code}, error: {error})"
            )
        
        # Record crash
        crash_time = datetime.utcnow()
        self.crash_history[process_name].append(crash_time)
        
        # Notify handlers
        self._notify_crash(process_name, exit_code, error)
        
        # Check circuit breaker
        if self._should_open_circuit(process_name):
            if self.logger:
                self.logger.warning(
                    f"Circuit breaker opened for {process_name} "
                    f"due to repeated crashes"
                )
            
            self.circuit_open[process_name] = crash_time
            
            return {
                'recovered': False,
                'reason': 'circuit_breaker_open',
                'retry_after': self.circuit_breaker_timeout
            }
        
        # Get recovery strategy
        strategy = self.recovery_strategies.get(
            process_name,
            RecoveryStrategy.RESTART_WITH_BACKOFF
        )
        
        # Attempt recovery
        return self._execute_recovery(process_name, strategy)
    
    def _should_open_circuit(self, process_name: str) -> bool:
        """
        Check if circuit breaker should open.
        
        Args:
            process_name: Process name
            
        Returns:
            True if circuit should open
        """
        if process_name not in self.crash_history:
            return False
        
        # Count recent crashes (last 5 minutes)
        recent_crashes = [
            crash_time
            for crash_time in self.crash_history[process_name]
            if (datetime.utcnow() - crash_time).total_seconds() < 300
        ]
        
        return len(recent_crashes) >= self.circuit_breaker_threshold
    
    def _execute_recovery(
        self,
        process_name: str,
        strategy: RecoveryStrategy
    ) -> Dict[str, Any]:
        """
        Execute recovery strategy.
        
        Args:
            process_name: Process name
            strategy: Recovery strategy
            
        Returns:
            Recovery result
        """
        if strategy == RecoveryStrategy.NONE:
            return {
                'recovered': False,
                'reason': 'no_recovery_strategy'
            }
        
        if strategy == RecoveryStrategy.RESTART:
            return self._restart_immediate(process_name)
        
        if strategy == RecoveryStrategy.RESTART_WITH_BACKOFF:
            return self._restart_with_backoff(process_name)
        
        if strategy == RecoveryStrategy.CIRCUIT_BREAKER:
            if self._is_circuit_closed(process_name):
                return self._restart_immediate(process_name)
            else:
                return {
                    'recovered': False,
                    'reason': 'circuit_breaker_open'
                }
        
        return {
            'recovered': False,
            'reason': 'unknown_strategy'
        }
    
    def _restart_immediate(self, process_name: str) -> Dict[str, Any]:
        """
        Restart process immediately.
        
        Args:
            process_name: Process name
            
        Returns:
            Recovery result
        """
        if not self.process_manager:
            return {
                'recovered': False,
                'reason': 'no_process_manager'
            }
        
        if self.logger:
            self.logger.info(f"Attempting immediate restart of {process_name}")
        
        # Restore from checkpoint if available
        self._restore_checkpoint(process_name)
        
        # Restart process
        success = self.process_manager.start_process(process_name)
        
        if success:
            if self.logger:
                self.logger.info(f"Successfully restarted {process_name}")
            
            return {
                'recovered': True,
                'strategy': 'immediate_restart'
            }
        else:
            return {
                'recovered': False,
                'reason': 'restart_failed'
            }
    
    def _restart_with_backoff(self, process_name: str) -> Dict[str, Any]:
        """
        Restart process with exponential backoff.
        
        Args:
            process_name: Process name
            
        Returns:
            Recovery result
        """
        retry_count = self.retry_counts.get(process_name, 0)
        
        if retry_count >= self.max_crash_retries:
            if self.logger:
                self.logger.error(
                    f"Max retries exceeded for {process_name}, giving up"
                )
            
            return {
                'recovered': False,
                'reason': 'max_retries_exceeded',
                'retry_count': retry_count
            }
        
        # Calculate backoff delay
        delay = self.retry_backoff_base ** retry_count
        
        if self.logger:
            self.logger.info(
                f"Waiting {delay:.1f}s before restart attempt "
                f"{retry_count + 1}/{self.max_crash_retries} for {process_name}"
            )
        
        time.sleep(delay)
        
        # Increment retry count
        self.retry_counts[process_name] = retry_count + 1
        
        # Attempt restart
        return self._restart_immediate(process_name)
    
    def _is_circuit_closed(self, process_name: str) -> bool:
        """
        Check if circuit breaker is closed.
        
        Args:
            process_name: Process name
            
        Returns:
            True if circuit is closed
        """
        if process_name not in self.circuit_open:
            return True
        
        open_time = self.circuit_open[process_name]
        elapsed = (datetime.utcnow() - open_time).total_seconds()
        
        if elapsed >= self.circuit_breaker_timeout:
            # Close circuit
            del self.circuit_open[process_name]
            if self.logger:
                self.logger.info(f"Circuit breaker closed for {process_name}")
            return True
        
        return False
    
    def save_checkpoint(self, process_name: str, state: Dict[str, Any]):
        """
        Save process state checkpoint.
        
        Args:
            process_name: Process name
            state: State data to save
        """
        checkpoint_file = self.checkpoint_dir / f"{process_name}.json"
        
        try:
            import json
            with open(checkpoint_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.utcnow().isoformat(),
                    'state': state
                }, f, indent=2)
            
            if self.logger:
                self.logger.debug(f"Saved checkpoint for {process_name}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save checkpoint: {e}")
    
    def _restore_checkpoint(self, process_name: str) -> Optional[Dict[str, Any]]:
        """
        Restore process state from checkpoint.
        
        Args:
            process_name: Process name
            
        Returns:
            Restored state or None
        """
        checkpoint_file = self.checkpoint_dir / f"{process_name}.json"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            import json
            with open(checkpoint_file) as f:
                data = json.load(f)
            
            if self.logger:
                self.logger.info(f"Restored checkpoint for {process_name}")
            
            return data.get('state')
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to restore checkpoint: {e}")
            return None
    
    def reset_retry_count(self, process_name: str):
        """
        Reset retry count for a process.
        
        Args:
            process_name: Process name
        """
        self.retry_counts[process_name] = 0
    
    def _notify_crash(
        self,
        process_name: str,
        exit_code: Optional[int],
        error: Optional[Exception]
    ):
        """
        Notify crash handlers.
        
        Args:
            process_name: Process name
            exit_code: Exit code
            error: Exception
        """
        crash_data = {
            'process_name': process_name,
            'exit_code': exit_code,
            'error': str(error) if error else None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        for callback in self.notification_callbacks:
            try:
                callback(crash_data)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Crash notification failed: {e}")
    
    def add_notification_callback(self, callback: Callable):
        """
        Add crash notification callback.
        
        Args:
            callback: Notification function
        """
        self.notification_callbacks.append(callback)
    
    def get_crash_statistics(self) -> Dict[str, Any]:
        """
        Get crash statistics.
        
        Returns:
            Statistics dict
        """
        stats = {}
        
        for process_name in self.crash_history:
            crashes = self.crash_history[process_name]
            
            stats[process_name] = {
                'total_crashes': len(crashes),
                'retry_count': self.retry_counts.get(process_name, 0),
                'circuit_open': process_name in self.circuit_open,
                'last_crash': crashes[-1].isoformat() if crashes else None
            }
        
        return stats


def create_crash_handler(
    logger=None,
    process_manager=None,
    max_retries: int = 3
) -> CrashHandler:
    """
    Factory function to create crash handler.
    
    Args:
        logger: Logger instance
        process_manager: Process manager instance
        max_retries: Maximum retry attempts
        
    Returns:
        CrashHandler instance
    """
    return CrashHandler(
        logger=logger,
        process_manager=process_manager,
        max_crash_retries=max_retries
    )
