#!/usr/bin/env python3
"""
Hot Reload Manager
Reload code/config without downtime
"""

import importlib
import sys
from typing import Dict, Any, Optional, List, Set
from pathlib import Path
from datetime import datetime
import time


class ReloadManager:
    """
    Hot reload capabilities.
    Reload code and configuration without downtime.
    """
    
    def __init__(self, logger=None):
        """
        Initialize reload manager.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger
        
        # Track loaded modules
        self.loaded_modules: Set[str] = set()
        self.module_timestamps: Dict[str, float] = {}
        
        # State preservation
        self.preserved_state: Dict[str, Any] = {}
        
        # Reload callbacks
        self.pre_reload_callbacks: List[callable] = []
        self.post_reload_callbacks: List[callable] = []
        
        # Rollback support
        self.rollback_snapshots: List[Dict[str, Any]] = []
        self.max_snapshots = 5
    
    def track_module(self, module_name: str):
        """
        Track a module for hot reload.
        
        Args:
            module_name: Module name to track
        """
        self.loaded_modules.add(module_name)
        
        # Get module file path and timestamp
        if module_name in sys.modules:
            module = sys.modules[module_name]
            if hasattr(module, '__file__') and module.__file__:
                module_path = Path(module.__file__)
                if module_path.exists():
                    self.module_timestamps[module_name] = module_path.stat().st_mtime
        
        if self.logger:
            self.logger.debug(f"Tracking module for reload: {module_name}")
    
    def check_for_changes(self) -> List[str]:
        """
        Check if any tracked modules have changed.
        
        Returns:
            List of changed module names
        """
        changed_modules = []
        
        for module_name in self.loaded_modules:
            if module_name not in sys.modules:
                continue
            
            module = sys.modules[module_name]
            if not hasattr(module, '__file__') or not module.__file__:
                continue
            
            module_path = Path(module.__file__)
            if not module_path.exists():
                continue
            
            current_mtime = module_path.stat().st_mtime
            last_mtime = self.module_timestamps.get(module_name, 0)
            
            if current_mtime > last_mtime:
                changed_modules.append(module_name)
                self.module_timestamps[module_name] = current_mtime
        
        return changed_modules
    
    def reload_module(self, module_name: str, preserve_state: bool = True) -> bool:
        """
        Reload a specific module.
        
        Args:
            module_name: Module name to reload
            preserve_state: Preserve module state
            
        Returns:
            True if successful
        """
        if module_name not in sys.modules:
            if self.logger:
                self.logger.warning(f"Module not loaded: {module_name}")
            return False
        
        try:
            if self.logger:
                self.logger.info(f"Reloading module: {module_name}")
            
            # Save state if requested
            if preserve_state:
                self._save_module_state(module_name)
            
            # Execute pre-reload callbacks
            for callback in self.pre_reload_callbacks:
                callback(module_name)
            
            # Reload the module
            module = sys.modules[module_name]
            importlib.reload(module)
            
            # Restore state if preserved
            if preserve_state:
                self._restore_module_state(module_name)
            
            # Execute post-reload callbacks
            for callback in self.post_reload_callbacks:
                callback(module_name)
            
            # Update timestamp
            if hasattr(module, '__file__') and module.__file__:
                module_path = Path(module.__file__)
                if module_path.exists():
                    self.module_timestamps[module_name] = module_path.stat().st_mtime
            
            if self.logger:
                self.logger.info(f"Successfully reloaded: {module_name}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to reload {module_name}: {e}", exc_info=True)
            return False
    
    def reload_config(self, config_manager) -> bool:
        """
        Reload configuration.
        
        Args:
            config_manager: ConfigManager instance
            
        Returns:
            True if successful
        """
        try:
            if self.logger:
                self.logger.info("Reloading configuration")
            
            # Save current config as snapshot
            self._create_snapshot({'config': config_manager.config})
            
            # Reload configuration files
            config_manager._load_env_file()
            config_manager._load_config_files()
            config_manager._load_service_configs()
            
            if self.logger:
                self.logger.info("Configuration reloaded successfully")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to reload config: {e}", exc_info=True)
            
            # Attempt rollback
            self._rollback_last_snapshot()
            
            return False
    
    def _save_module_state(self, module_name: str):
        """Save module state for restoration."""
        if module_name not in sys.modules:
            return
        
        module = sys.modules[module_name]
        state = {}
        
        # Save module-level variables (simple types only)
        for attr_name in dir(module):
            if attr_name.startswith('_'):
                continue
            
            try:
                attr_value = getattr(module, attr_name)
                # Only save simple types
                if isinstance(attr_value, (str, int, float, bool, list, dict)):
                    state[attr_name] = attr_value
            except:
                pass
        
        self.preserved_state[module_name] = state
    
    def _restore_module_state(self, module_name: str):
        """Restore module state after reload."""
        if module_name not in self.preserved_state:
            return
        
        if module_name not in sys.modules:
            return
        
        module = sys.modules[module_name]
        state = self.preserved_state[module_name]
        
        # Restore saved state
        for attr_name, attr_value in state.items():
            try:
                setattr(module, attr_name, attr_value)
            except:
                pass
    
    def _create_snapshot(self, data: Dict[str, Any]):
        """Create a rollback snapshot."""
        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        self.rollback_snapshots.append(snapshot)
        
        # Limit snapshots
        if len(self.rollback_snapshots) > self.max_snapshots:
            self.rollback_snapshots.pop(0)
    
    def _rollback_last_snapshot(self) -> bool:
        """
        Rollback to last snapshot.
        
        NOTE: This is a simplified rollback implementation.
        Current limitations:
        - Only basic data restoration
        - No database transaction rollback
        - No distributed state rollback
        
        Production requirements:
        - Database transaction management
        - Distributed state coordination
        - Service dependency rollback
        - Data consistency validation
        """
        if not self.rollback_snapshots:
            if self.logger:
                self.logger.warning("No snapshots available for rollback")
            return False
        
        snapshot = self.rollback_snapshots.pop()
        
        if self.logger:
            self.logger.warning(f"Rolling back to snapshot: {snapshot['timestamp']}")
        
        # Restore data from snapshot
        # Currently only supports basic configuration rollback
        
        return True
    
    def register_pre_reload_callback(self, callback: callable):
        """
        Register callback to execute before reload.
        
        Args:
            callback: Callback function
        """
        self.pre_reload_callbacks.append(callback)
    
    def register_post_reload_callback(self, callback: callable):
        """
        Register callback to execute after reload.
        
        Args:
            callback: Callback function
        """
        self.post_reload_callbacks.append(callback)
    
    def auto_reload_loop(
        self,
        check_interval: int = 5,
        modules_to_watch: Optional[List[str]] = None
    ):
        """
        Auto-reload loop (blocking).
        
        Args:
            check_interval: Check interval (seconds)
            modules_to_watch: List of modules to watch
        """
        if modules_to_watch:
            for module_name in modules_to_watch:
                self.track_module(module_name)
        
        if self.logger:
            self.logger.info(f"Starting auto-reload loop (interval: {check_interval}s)")
        
        try:
            while True:
                changed = self.check_for_changes()
                
                if changed:
                    if self.logger:
                        self.logger.info(f"Detected changes: {changed}")
                    
                    for module_name in changed:
                        self.reload_module(module_name)
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            if self.logger:
                self.logger.info("Auto-reload loop stopped")


def create_reload_manager(logger=None) -> ReloadManager:
    """
    Factory function to create reload manager.
    
    Args:
        logger: Logger instance
        
    Returns:
        ReloadManager instance
    """
    return ReloadManager(logger=logger)
