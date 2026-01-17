#!/usr/bin/env python3
"""
Detects and recovers from process freezes/hangs
"""

import time
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from enum import Enum


class FreezeType(Enum):
    """Types of freezes"""
    NO_FREEZE = "no_freeze"
    SOFT_FREEZE = "soft_freeze"  # Slow but responding
    HARD_FREEZE = "hard_freeze"  # Completely frozen
    DEADLOCK = "deadlock"        # Thread deadlock


class FreezeDetector:
    """
    Detects and recovers from process freezes and hangs.
    Uses watchdog timers and activity monitoring.
    """
    
    def __init__(
        self,
        logger=None,
        process_manager=None,
        crash_handler=None,
        soft_freeze_threshold: int = 60,
        hard_freeze_threshold: int = 300,
        check_interval: int = 30
    ):
        """
        Initialize freeze detector.
        
        Args:
            logger: Logger instance
            process_manager: Process manager instance
            crash_handler: Crash handler instance
            soft_freeze_threshold: Soft freeze timeout (seconds)
            hard_freeze_threshold: Hard freeze timeout (seconds)
            check_interval: Check interval (seconds)
        """
        self.logger = logger
        self.process_manager = process_manager
        self.crash_handler = crash_handler
        self.soft_freeze_threshold = soft_freeze_threshold
        self.hard_freeze_threshold = hard_freeze_threshold
        self.check_interval = check_interval
        
        # Watchdog timers
        self.watchdogs: Dict[str, Dict[str, Any]] = {}
        
        # Activity tracking
        self.last_activity: Dict[str, datetime] = {}
        
        # Recovery callbacks
        self.recovery_callbacks: Dict[str, Callable] = {}
        
        # Monitoring thread
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.running = False
    
    def register_watchdog(
        self,
        process_name: str,
        timeout: Optional[int] = None,
        auto_recover: bool = True
    ):
        """
        Register a watchdog for a process.
        
        Args:
            process_name: Process name
            timeout: Watchdog timeout (defaults to hard_freeze_threshold)
            auto_recover: Automatically recover on freeze
        """
        if timeout is None:
            timeout = self.hard_freeze_threshold
        
        self.watchdogs[process_name] = {
            'timeout': timeout,
            'auto_recover': auto_recover,
            'last_reset': datetime.utcnow(),
            'freeze_count': 0
        }
        
        self.last_activity[process_name] = datetime.utcnow()
        
        if self.logger:
            self.logger.info(
                f"Registered watchdog for {process_name} "
                f"(timeout: {timeout}s)"
            )
    
    def reset_watchdog(self, process_name: str):
        """
        Reset watchdog timer (called by process to indicate activity).
        
        Args:
            process_name: Process name
        """
        if process_name in self.watchdogs:
            self.watchdogs[process_name]['last_reset'] = datetime.utcnow()
            self.last_activity[process_name] = datetime.utcnow()
    
    def record_activity(self, process_name: str):
        """
        Record process activity.
        
        Args:
            process_name: Process name
        """
        self.last_activity[process_name] = datetime.utcnow()
    
    def check_for_freeze(self, process_name: str) -> FreezeType:
        """
        Check if a process is frozen.
        
        Args:
            process_name: Process name
            
        Returns:
            FreezeType
        """
        if process_name not in self.watchdogs:
            return FreezeType.NO_FREEZE
        
        watchdog = self.watchdogs[process_name]
        now = datetime.utcnow()
        
        # Check time since last reset
        time_since_reset = (now - watchdog['last_reset']).total_seconds()
        
        if time_since_reset > self.hard_freeze_threshold:
            if self.logger:
                self.logger.warning(
                    f"Hard freeze detected for {process_name} "
                    f"({time_since_reset:.0f}s since last activity)"
                )
            return FreezeType.HARD_FREEZE
        
        if time_since_reset > self.soft_freeze_threshold:
            if self.logger:
                self.logger.warning(
                    f"Soft freeze detected for {process_name} "
                    f"({time_since_reset:.0f}s since last activity)"
                )
            return FreezeType.SOFT_FREEZE
        
        return FreezeType.NO_FREEZE
    
    def detect_deadlock(self, process_name: str) -> bool:
        """
        Attempt to detect thread deadlock.
        
        NOTE: This is a simplified deadlock detection mechanism.
        Production systems should implement:
        - Thread stack trace analysis
        - Lock graph construction
        - Resource dependency tracking
        - Integration with debugger tools
        
        Args:
            process_name: Process name
            
        Returns:
            True if deadlock suspected
        """
        # This is a simplified deadlock detection
        # Currently detects based on repeated freeze patterns
        
        freeze_type = self.check_for_freeze(process_name)
        
        if freeze_type == FreezeType.HARD_FREEZE:
            # Check if process is consuming CPU
            # If frozen but using CPU, might be infinite loop
            # If frozen and not using CPU, might be deadlock
            
            if process_name in self.watchdogs:
                # Increment freeze count
                self.watchdogs[process_name]['freeze_count'] += 1
                
                # If multiple consecutive freezes, suspect deadlock
                if self.watchdogs[process_name]['freeze_count'] >= 3:
                    if self.logger:
                        self.logger.error(
                            f"Deadlock suspected in {process_name}"
                        )
                    return True
        else:
            # Reset freeze count on activity
            if process_name in self.watchdogs:
                self.watchdogs[process_name]['freeze_count'] = 0
        
        return False
    
    def recover_from_freeze(
        self,
        process_name: str,
        freeze_type: FreezeType,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Recover from a process freeze.
        
        Args:
            process_name: Process name
            freeze_type: Type of freeze detected
            force: Force termination
            
        Returns:
            Recovery result
        """
        if self.logger:
            self.logger.warning(
                f"Attempting freeze recovery for {process_name} "
                f"(type: {freeze_type.value})"
            )
        
        # Try custom recovery callback first
        if process_name in self.recovery_callbacks:
            try:
                result = self.recovery_callbacks[process_name](freeze_type)
                if result.get('recovered'):
                    return result
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Custom recovery failed: {e}")
        
        # For soft freeze, try gentle recovery
        if freeze_type == FreezeType.SOFT_FREEZE and not force:
            if self.logger:
                self.logger.info(f"Monitoring {process_name} for improvement")
            
            return {
                'recovered': False,
                'action': 'monitoring',
                'reason': 'soft_freeze_wait_and_see'
            }
        
        # For hard freeze or forced recovery, restart process
        if freeze_type in [FreezeType.HARD_FREEZE, FreezeType.DEADLOCK] or force:
            if self.process_manager:
                if self.logger:
                    self.logger.warning(
                        f"Force terminating frozen process: {process_name}"
                    )
                
                # Stop the frozen process
                self.process_manager.stop_process(process_name, timeout=5)
                
                # Use crash handler to restart with recovery logic
                if self.crash_handler:
                    result = self.crash_handler.handle_crash(
                        process_name,
                        exit_code=-1,
                        error=Exception(f"Process frozen: {freeze_type.value}")
                    )
                    
                    if result.get('recovered'):
                        # Reset watchdog
                        if process_name in self.watchdogs:
                            self.watchdogs[process_name]['last_reset'] = datetime.utcnow()
                            self.watchdogs[process_name]['freeze_count'] = 0
                    
                    return result
                else:
                    # Restart directly
                    success = self.process_manager.restart_process(process_name)
                    
                    if success and process_name in self.watchdogs:
                        self.watchdogs[process_name]['last_reset'] = datetime.utcnow()
                        self.watchdogs[process_name]['freeze_count'] = 0
                    
                    return {
                        'recovered': success,
                        'action': 'restart',
                        'freeze_type': freeze_type.value
                    }
        
        return {
            'recovered': False,
            'reason': 'no_recovery_method'
        }
    
    def start_monitoring(self):
        """Start freeze monitoring."""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        if self.logger:
            self.logger.info("Freeze monitoring started")
    
    def stop_monitoring(self):
        """Stop freeze monitoring."""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        if self.logger:
            self.logger.info("Freeze monitoring stopped")
    
    def _monitoring_loop(self):
        """Monitoring loop (runs in separate thread)."""
        while not self.stop_event.is_set():
            try:
                # Check all registered watchdogs
                for process_name in list(self.watchdogs.keys()):
                    freeze_type = self.check_for_freeze(process_name)
                    
                    if freeze_type != FreezeType.NO_FREEZE:
                        watchdog = self.watchdogs[process_name]
                        
                        # Auto-recover if enabled
                        if watchdog['auto_recover']:
                            # Check for deadlock
                            if self.detect_deadlock(process_name):
                                freeze_type = FreezeType.DEADLOCK
                            
                            self.recover_from_freeze(process_name, freeze_type)
            
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"Error in freeze monitoring: {e}",
                        exc_info=True
                    )
            
            # Wait for next check
            self.stop_event.wait(self.check_interval)
    
    def register_recovery_callback(self, process_name: str, callback: Callable):
        """
        Register custom recovery callback for a process.
        
        Args:
            process_name: Process name
            callback: Recovery function
        """
        self.recovery_callbacks[process_name] = callback
    
    def get_freeze_statistics(self) -> Dict[str, Any]:
        """
        Get freeze statistics.
        
        Returns:
            Statistics dict
        """
        stats = {}
        
        for process_name, watchdog in self.watchdogs.items():
            now = datetime.utcnow()
            time_since_reset = (now - watchdog['last_reset']).total_seconds()
            
            stats[process_name] = {
                'time_since_activity': time_since_reset,
                'freeze_count': watchdog['freeze_count'],
                'current_status': self.check_for_freeze(process_name).value,
                'timeout': watchdog['timeout']
            }
        
        return stats


def create_freeze_detector(
    logger=None,
    process_manager=None,
    crash_handler=None,
    auto_start: bool = False
) -> FreezeDetector:
    """
    Factory function to create freeze detector.
    
    Args:
        logger: Logger instance
        process_manager: Process manager instance
        crash_handler: Crash handler instance
        auto_start: Start monitoring immediately
        
    Returns:
        FreezeDetector instance
    """
    detector = FreezeDetector(
        logger=logger,
        process_manager=process_manager,
        crash_handler=crash_handler
    )
    
    if auto_start:
        detector.start_monitoring()
    
    return detector
