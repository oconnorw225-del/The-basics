#!/usr/bin/env python3
"""
System Health Monitoring
Tracks health of all components and triggers recovery actions
"""

import time
import psutil
import subprocess
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
from threading import Thread, Event


class HealthStatus(Enum):
    """Health status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ProcessState(Enum):
    """Process state"""
    RUNNING = "running"
    STOPPED = "stopped"
    FROZEN = "frozen"
    CRASHED = "crashed"
    UNKNOWN = "unknown"


class HealthMonitor:
    """
    System health monitoring.
    Monitors processes, resources, and triggers recovery actions.
    """
    
    def __init__(
        self,
        logger=None,
        check_interval: int = 60,
        freeze_timeout: int = 300,
        memory_threshold: float = 90.0,
        cpu_threshold: float = 90.0,
        disk_threshold: float = 90.0
    ):
        """
        Initialize health monitor.
        
        Args:
            logger: Logger instance
            check_interval: Interval between health checks (seconds)
            freeze_timeout: Timeout to detect frozen processes (seconds)
            memory_threshold: Memory usage threshold (percentage)
            cpu_threshold: CPU usage threshold (percentage)
            disk_threshold: Disk usage threshold (percentage)
        """
        self.logger = logger
        self.check_interval = check_interval
        self.freeze_timeout = freeze_timeout
        self.memory_threshold = memory_threshold
        self.cpu_threshold = cpu_threshold
        self.disk_threshold = disk_threshold
        
        # Process tracking
        self.processes: Dict[str, Dict[str, Any]] = {}
        
        # Health data
        self.health_data: Dict[str, Any] = {}
        self.last_check: Optional[datetime] = None
        
        # Recovery callbacks
        self.recovery_callbacks: Dict[str, Callable] = {}
        
        # Monitoring thread
        self.monitoring_thread: Optional[Thread] = None
        self.stop_event = Event()
        self.running = False
    
    def register_process(
        self,
        name: str,
        pid: Optional[int] = None,
        port: Optional[int] = None,
        health_endpoint: Optional[str] = None
    ):
        """
        Register a process for monitoring.
        
        Args:
            name: Process name/identifier
            pid: Process ID (optional)
            port: Process port (optional)
            health_endpoint: HTTP health check endpoint (optional)
        """
        self.processes[name] = {
            'name': name,
            'pid': pid,
            'port': port,
            'health_endpoint': health_endpoint,
            'state': ProcessState.UNKNOWN,
            'last_heartbeat': None,
            'last_check': None,
            'consecutive_failures': 0,
            'start_time': datetime.utcnow()
        }
        
        if self.logger:
            self.logger.info(f"Registered process for monitoring: {name}")
    
    def unregister_process(self, name: str):
        """
        Unregister a process from monitoring.
        
        Args:
            name: Process name
        """
        if name in self.processes:
            del self.processes[name]
            if self.logger:
                self.logger.info(f"Unregistered process: {name}")
    
    def heartbeat(self, name: str):
        """
        Record a heartbeat from a process.
        
        Args:
            name: Process name
        """
        if name in self.processes:
            self.processes[name]['last_heartbeat'] = datetime.utcnow()
            self.processes[name]['consecutive_failures'] = 0
    
    def check_process_health(self, name: str) -> Dict[str, Any]:
        """
        Check health of a specific process.
        
        Args:
            name: Process name
            
        Returns:
            Health check result
        """
        if name not in self.processes:
            return {
                'status': HealthStatus.UNKNOWN.value,
                'reason': 'Process not registered'
            }
        
        process = self.processes[name]
        now = datetime.utcnow()
        
        # Check if process is running (by PID)
        if process['pid']:
            try:
                proc = psutil.Process(process['pid'])
                if proc.is_running():
                    process['state'] = ProcessState.RUNNING
                else:
                    process['state'] = ProcessState.STOPPED
                    return {
                        'status': HealthStatus.UNHEALTHY.value,
                        'reason': 'Process not running',
                        'state': process['state'].value
                    }
            except psutil.NoSuchProcess:
                process['state'] = ProcessState.CRASHED
                return {
                    'status': HealthStatus.UNHEALTHY.value,
                    'reason': 'Process crashed',
                    'state': process['state'].value
                }
        
        # Check heartbeat
        if process['last_heartbeat']:
            time_since_heartbeat = (now - process['last_heartbeat']).total_seconds()
            
            if time_since_heartbeat > self.freeze_timeout:
                process['state'] = ProcessState.FROZEN
                return {
                    'status': HealthStatus.UNHEALTHY.value,
                    'reason': f'No heartbeat for {time_since_heartbeat:.0f}s',
                    'state': process['state'].value
                }
        
        # Check HTTP health endpoint
        if process['health_endpoint']:
            try:
                import httpx
                response = httpx.get(process['health_endpoint'], timeout=5.0)
                
                if response.status_code == 200:
                    process['consecutive_failures'] = 0
                    return {
                        'status': HealthStatus.HEALTHY.value,
                        'state': ProcessState.RUNNING.value
                    }
                else:
                    process['consecutive_failures'] += 1
                    return {
                        'status': HealthStatus.DEGRADED.value,
                        'reason': f'Health check returned {response.status_code}',
                        'consecutive_failures': process['consecutive_failures']
                    }
            except Exception as e:
                process['consecutive_failures'] += 1
                return {
                    'status': HealthStatus.UNHEALTHY.value,
                    'reason': f'Health check failed: {e}',
                    'consecutive_failures': process['consecutive_failures']
                }
        
        # Default to healthy if no issues detected
        return {
            'status': HealthStatus.HEALTHY.value,
            'state': ProcessState.RUNNING.value
        }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resource usage.
        
        Returns:
            Resource usage data
        """
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Network connectivity
        network_ok = self._check_network_connectivity()
        
        # Determine overall status
        issues = []
        
        if cpu_percent > self.cpu_threshold:
            issues.append(f'High CPU usage: {cpu_percent:.1f}%')
        
        if memory_percent > self.memory_threshold:
            issues.append(f'High memory usage: {memory_percent:.1f}%')
        
        if disk_percent > self.disk_threshold:
            issues.append(f'High disk usage: {disk_percent:.1f}%')
        
        if not network_ok:
            issues.append('Network connectivity issue')
        
        status = HealthStatus.HEALTHY
        if issues:
            status = HealthStatus.DEGRADED if len(issues) <= 2 else HealthStatus.UNHEALTHY
        
        return {
            'status': status.value,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'memory_available_mb': memory.available // (1024 * 1024),
            'disk_percent': disk_percent,
            'disk_free_gb': disk.free // (1024 * 1024 * 1024),
            'network_ok': network_ok,
            'issues': issues
        }
    
    def _check_network_connectivity(self) -> bool:
        """
        Check basic network connectivity.
        
        NOTE: Uses Google's DNS (8.8.8.8) for connectivity test.
        Configure CONNECTIVITY_TEST_HOST env var to use a different host.
        """
        try:
            # Get test host from environment or use default
            test_host = os.getenv('CONNECTIVITY_TEST_HOST', '8.8.8.8')
            
            # Try to ping the test host
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', test_host],
                capture_output=True,
                timeout=3
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def perform_full_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Complete health status
        """
        now = datetime.utcnow()
        
        # Check all processes
        process_health = {}
        unhealthy_processes = []
        
        for name in self.processes:
            health = self.check_process_health(name)
            process_health[name] = health
            
            if health['status'] != HealthStatus.HEALTHY.value:
                unhealthy_processes.append(name)
        
        # Check system resources
        resource_health = self.check_system_resources()
        
        # Determine overall status
        overall_status = HealthStatus.HEALTHY
        
        if unhealthy_processes or resource_health['status'] != HealthStatus.HEALTHY.value:
            overall_status = HealthStatus.DEGRADED
        
        if len(unhealthy_processes) > len(self.processes) // 2:
            overall_status = HealthStatus.UNHEALTHY
        
        self.health_data = {
            'timestamp': now.isoformat(),
            'overall_status': overall_status.value,
            'processes': process_health,
            'resources': resource_health,
            'unhealthy_processes': unhealthy_processes
        }
        
        self.last_check = now
        
        # Trigger recovery if needed
        if unhealthy_processes:
            self._trigger_recovery(unhealthy_processes)
        
        return self.health_data
    
    def _trigger_recovery(self, unhealthy_processes: List[str]):
        """
        Trigger recovery actions for unhealthy processes.
        
        Args:
            unhealthy_processes: List of unhealthy process names
        """
        for process_name in unhealthy_processes:
            if process_name in self.recovery_callbacks:
                try:
                    if self.logger:
                        self.logger.warning(f"Triggering recovery for {process_name}")
                    
                    self.recovery_callbacks[process_name](self.processes[process_name])
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Recovery failed for {process_name}: {e}")
    
    def register_recovery_callback(self, process_name: str, callback: Callable):
        """
        Register a recovery callback for a process.
        
        Args:
            process_name: Process name
            callback: Recovery function
        """
        self.recovery_callbacks[process_name] = callback
    
    def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        self.monitoring_thread = Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        if self.logger:
            self.logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop health monitoring."""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        if self.logger:
            self.logger.info("Health monitoring stopped")
    
    def _monitoring_loop(self):
        """Monitoring loop (runs in separate thread)."""
        while not self.stop_event.is_set():
            try:
                self.perform_full_health_check()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Health check failed: {e}", exc_info=True)
            
            # Wait for next check interval
            self.stop_event.wait(self.check_interval)
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status.
        
        Returns:
            Health status data
        """
        if not self.health_data:
            return {
                'status': HealthStatus.UNKNOWN.value,
                'message': 'No health data available'
            }
        
        return self.health_data
    
    def get_process_uptime(self, name: str) -> Optional[float]:
        """
        Get process uptime in seconds.
        
        Args:
            name: Process name
            
        Returns:
            Uptime in seconds or None
        """
        if name not in self.processes:
            return None
        
        start_time = self.processes[name].get('start_time')
        if start_time:
            return (datetime.utcnow() - start_time).total_seconds()
        
        return None


def create_health_monitor(
    logger=None,
    check_interval: int = 60,
    auto_start: bool = False
) -> HealthMonitor:
    """
    Factory function to create health monitor.
    
    Args:
        logger: Logger instance
        check_interval: Interval between checks
        auto_start: Start monitoring immediately
        
    Returns:
        HealthMonitor instance
    """
    monitor = HealthMonitor(logger=logger, check_interval=check_interval)
    
    if auto_start:
        monitor.start_monitoring()
    
    return monitor
