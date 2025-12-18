#!/usr/bin/env python3
"""
Central Process Manager
Coordinates all system components and handles lifecycle events
"""

import os
import signal
import subprocess
import time
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from datetime import datetime
from pathlib import Path


class ProcessStatus(Enum):
    """Process status"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    CRASHED = "crashed"
    FAILED = "failed"


class ManagedProcess:
    """Represents a managed process"""
    
    def __init__(
        self,
        name: str,
        command: List[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        auto_restart: bool = True,
        max_restarts: int = 3,
        restart_delay: float = 5.0,
        health_check: Optional[Callable] = None
    ):
        """
        Initialize managed process.
        
        Args:
            name: Process name
            command: Command and arguments
            cwd: Working directory
            env: Environment variables
            auto_restart: Automatically restart on crash
            max_restarts: Maximum restart attempts
            restart_delay: Delay between restarts (seconds)
            health_check: Health check callable
        """
        self.name = name
        self.command = command
        self.cwd = cwd
        self.env = env or os.environ.copy()
        self.auto_restart = auto_restart
        self.max_restarts = max_restarts
        self.restart_delay = restart_delay
        self.health_check = health_check
        
        self.process: Optional[subprocess.Popen] = None
        self.status = ProcessStatus.STOPPED
        self.pid: Optional[int] = None
        self.start_time: Optional[datetime] = None
        self.restart_count = 0
        self.exit_code: Optional[int] = None


class ProcessManager:
    """
    Central process manager.
    Coordinates all system components and handles lifecycle events.
    """
    
    def __init__(self, logger=None, config_manager=None):
        """
        Initialize process manager.
        
        Args:
            logger: Logger instance
            config_manager: Configuration manager instance
        """
        self.logger = logger
        self.config_manager = config_manager
        
        # Managed processes
        self.processes: Dict[str, ManagedProcess] = {}
        
        # Lifecycle callbacks
        self.on_start_callbacks: Dict[str, List[Callable]] = {}
        self.on_stop_callbacks: Dict[str, List[Callable]] = {}
        self.on_crash_callbacks: Dict[str, List[Callable]] = {}
        
        # Shutdown flag
        self.shutting_down = False
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        if self.logger:
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown")
        
        self.shutdown_all()
    
    def register_process(
        self,
        name: str,
        command: List[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        auto_restart: bool = True,
        max_restarts: int = 3,
        health_check: Optional[Callable] = None
    ) -> ManagedProcess:
        """
        Register a process for management.
        
        Args:
            name: Process name
            command: Command and arguments
            cwd: Working directory
            env: Environment variables
            auto_restart: Auto-restart on crash
            max_restarts: Maximum restart attempts
            health_check: Health check callable
            
        Returns:
            ManagedProcess instance
        """
        process = ManagedProcess(
            name=name,
            command=command,
            cwd=cwd,
            env=env,
            auto_restart=auto_restart,
            max_restarts=max_restarts,
            health_check=health_check
        )
        
        self.processes[name] = process
        
        if self.logger:
            self.logger.info(f"Registered process: {name}")
        
        return process
    
    def start_process(self, name: str) -> bool:
        """
        Start a managed process.
        
        Args:
            name: Process name
            
        Returns:
            True if started successfully
        """
        if name not in self.processes:
            if self.logger:
                self.logger.error(f"Process not found: {name}")
            return False
        
        process = self.processes[name]
        
        if process.status == ProcessStatus.RUNNING:
            if self.logger:
                self.logger.warning(f"Process already running: {name}")
            return True
        
        try:
            if self.logger:
                self.logger.info(f"Starting process: {name}")
            
            process.status = ProcessStatus.STARTING
            
            # Execute on_start callbacks
            self._execute_callbacks(self.on_start_callbacks.get(name, []), process)
            
            # Start process
            process.process = subprocess.Popen(
                process.command,
                cwd=process.cwd,
                env=process.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
            
            process.pid = process.process.pid
            process.start_time = datetime.utcnow()
            process.status = ProcessStatus.RUNNING
            process.exit_code = None
            
            if self.logger:
                self.logger.info(f"Process started: {name} (PID: {process.pid})")
            
            return True
            
        except Exception as e:
            process.status = ProcessStatus.FAILED
            if self.logger:
                self.logger.error(f"Failed to start process {name}: {e}", exc_info=True)
            return False
    
    def stop_process(self, name: str, timeout: int = 10) -> bool:
        """
        Stop a managed process gracefully.
        
        Args:
            name: Process name
            timeout: Timeout for graceful shutdown (seconds)
            
        Returns:
            True if stopped successfully
        """
        if name not in self.processes:
            return False
        
        process = self.processes[name]
        
        if process.status != ProcessStatus.RUNNING or not process.process:
            return True
        
        try:
            if self.logger:
                self.logger.info(f"Stopping process: {name}")
            
            process.status = ProcessStatus.STOPPING
            
            # Execute on_stop callbacks
            self._execute_callbacks(self.on_stop_callbacks.get(name, []), process)
            
            # Try graceful shutdown first (SIGTERM)
            process.process.terminate()
            
            try:
                process.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown times out
                if self.logger:
                    self.logger.warning(f"Process {name} didn't stop gracefully, forcing shutdown")
                process.process.kill()
                process.process.wait()
            
            process.exit_code = process.process.returncode
            process.status = ProcessStatus.STOPPED
            process.pid = None
            
            if self.logger:
                self.logger.info(f"Process stopped: {name}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to stop process {name}: {e}", exc_info=True)
            return False
    
    def restart_process(self, name: str) -> bool:
        """
        Restart a managed process.
        
        Args:
            name: Process name
            
        Returns:
            True if restarted successfully
        """
        if self.logger:
            self.logger.info(f"Restarting process: {name}")
        
        self.stop_process(name)
        time.sleep(1)  # Brief delay
        return self.start_process(name)
    
    def check_process_status(self, name: str) -> Optional[ProcessStatus]:
        """
        Check process status.
        
        Args:
            name: Process name
            
        Returns:
            ProcessStatus or None
        """
        if name not in self.processes:
            return None
        
        process = self.processes[name]
        
        # Check if process is still running
        if process.process and process.status == ProcessStatus.RUNNING:
            poll_result = process.process.poll()
            
            if poll_result is not None:
                # Process exited
                process.exit_code = poll_result
                process.status = ProcessStatus.CRASHED
                process.pid = None
                
                if self.logger:
                    self.logger.warning(
                        f"Process {name} crashed (exit code: {poll_result})"
                    )
                
                # Execute crash callbacks
                self._execute_callbacks(self.on_crash_callbacks.get(name, []), process)
                
                # Auto-restart if configured
                if process.auto_restart and process.restart_count < process.max_restarts:
                    if self.logger:
                        self.logger.info(
                            f"Auto-restarting {name} "
                            f"(attempt {process.restart_count + 1}/{process.max_restarts})"
                        )
                    
                    time.sleep(process.restart_delay)
                    process.restart_count += 1
                    self.start_process(name)
        
        return process.status
    
    def check_all_processes(self) -> Dict[str, ProcessStatus]:
        """
        Check status of all processes.
        
        Returns:
            Dict of process statuses
        """
        statuses = {}
        
        for name in self.processes:
            statuses[name] = self.check_process_status(name)
        
        return statuses
    
    def start_all(self, dependency_order: Optional[List[str]] = None):
        """
        Start all registered processes.
        
        Args:
            dependency_order: Optional list of process names in start order
        """
        if self.logger:
            self.logger.info("Starting all processes")
        
        if dependency_order:
            # Start in specified order
            for name in dependency_order:
                if name in self.processes:
                    self.start_process(name)
                    time.sleep(2)  # Brief delay between starts
        else:
            # Start all processes
            for name in self.processes:
                self.start_process(name)
                time.sleep(2)
    
    def shutdown_all(self, timeout: int = 30):
        """
        Shutdown all processes gracefully.
        
        Args:
            timeout: Timeout for shutdown (seconds)
        """
        if self.shutting_down:
            return
        
        self.shutting_down = True
        
        if self.logger:
            self.logger.info("Shutting down all processes")
        
        # Stop all processes in reverse order
        process_names = list(self.processes.keys())
        process_names.reverse()
        
        for name in process_names:
            self.stop_process(name, timeout=timeout // len(process_names))
        
        if self.logger:
            self.logger.info("All processes shut down")
    
    def _execute_callbacks(self, callbacks: List[Callable], process: ManagedProcess):
        """Execute lifecycle callbacks."""
        for callback in callbacks:
            try:
                callback(process)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Callback failed for {process.name}: {e}")
    
    def on_start(self, process_name: str, callback: Callable):
        """Register on_start callback."""
        if process_name not in self.on_start_callbacks:
            self.on_start_callbacks[process_name] = []
        self.on_start_callbacks[process_name].append(callback)
    
    def on_stop(self, process_name: str, callback: Callable):
        """Register on_stop callback."""
        if process_name not in self.on_stop_callbacks:
            self.on_stop_callbacks[process_name] = []
        self.on_stop_callbacks[process_name].append(callback)
    
    def on_crash(self, process_name: str, callback: Callable):
        """Register on_crash callback."""
        if process_name not in self.on_crash_callbacks:
            self.on_crash_callbacks[process_name] = []
        self.on_crash_callbacks[process_name].append(callback)
    
    def get_process_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get process information.
        
        Args:
            name: Process name
            
        Returns:
            Process info dict or None
        """
        if name not in self.processes:
            return None
        
        process = self.processes[name]
        
        uptime = None
        if process.start_time and process.status == ProcessStatus.RUNNING:
            uptime = (datetime.utcnow() - process.start_time).total_seconds()
        
        return {
            'name': process.name,
            'status': process.status.value,
            'pid': process.pid,
            'uptime': uptime,
            'restart_count': process.restart_count,
            'exit_code': process.exit_code
        }
    
    def get_all_process_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information for all processes."""
        return {
            name: self.get_process_info(name)
            for name in self.processes
        }


def create_process_manager(logger=None, config_manager=None) -> ProcessManager:
    """
    Factory function to create process manager.
    
    Args:
        logger: Logger instance
        config_manager: Configuration manager instance
        
    Returns:
        ProcessManager instance
    """
    return ProcessManager(logger=logger, config_manager=config_manager)
