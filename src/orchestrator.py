#!/usr/bin/env python3
"""
Service Orchestration
Manages startup, shutdown, and coordination of all services
"""

from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from enum import Enum
import time


class ServiceState(Enum):
    """Service states"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class Service:
    """Represents a service"""
    
    def __init__(
        self,
        name: str,
        dependencies: Optional[List[str]] = None,
        startup_timeout: int = 30,
        shutdown_timeout: int = 10
    ):
        """
        Initialize service.
        
        Args:
            name: Service name
            dependencies: List of dependency service names
            startup_timeout: Startup timeout (seconds)
            shutdown_timeout: Shutdown timeout (seconds)
        """
        self.name = name
        self.dependencies = dependencies or []
        self.startup_timeout = startup_timeout
        self.shutdown_timeout = shutdown_timeout
        
        self.state = ServiceState.UNINITIALIZED
        self.started_at: Optional[datetime] = None
        self.stopped_at: Optional[datetime] = None
        self.restart_count = 0


class ServiceOrchestrator:
    """
    Service orchestration.
    Manages startup order, dependencies, and coordination.
    """
    
    def __init__(self, logger=None, process_manager=None):
        """
        Initialize service orchestrator.
        
        Args:
            logger: Logger instance
            process_manager: Process manager instance
        """
        self.logger = logger
        self.process_manager = process_manager
        
        # Services
        self.services: Dict[str, Service] = {}
        
        # Startup/shutdown order
        self.startup_order: List[str] = []
        self.shutdown_order: List[str] = []
    
    def register_service(
        self,
        name: str,
        dependencies: Optional[List[str]] = None,
        startup_timeout: int = 30
    ):
        """
        Register a service.
        
        Args:
            name: Service name
            dependencies: List of dependencies
            startup_timeout: Startup timeout
        """
        service = Service(
            name=name,
            dependencies=dependencies,
            startup_timeout=startup_timeout
        )
        
        self.services[name] = service
        
        if self.logger:
            self.logger.info(f"Registered service: {name}")
    
    def _resolve_dependencies(self) -> List[str]:
        """
        Resolve service dependencies and determine startup order.
        
        Returns:
            Ordered list of service names
        """
        # Topological sort using Kahn's algorithm
        in_degree = {name: 0 for name in self.services}
        adj_list = {name: [] for name in self.services}
        
        # Build graph
        for name, service in self.services.items():
            for dep in service.dependencies:
                if dep in self.services:
                    adj_list[dep].append(name)
                    in_degree[name] += 1
        
        # Find services with no dependencies
        queue = [name for name, degree in in_degree.items() if degree == 0]
        order = []
        
        while queue:
            current = queue.pop(0)
            order.append(current)
            
            # Reduce in-degree for dependents
            for dependent in adj_list[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check for circular dependencies
        if len(order) != len(self.services):
            if self.logger:
                self.logger.error("Circular dependency detected in services")
            raise ValueError("Circular dependency detected")
        
        return order
    
    def start_all_services(self) -> bool:
        """
        Start all services in dependency order.
        
        Returns:
            True if all started successfully
        """
        if self.logger:
            self.logger.info("Starting all services...")
        
        # Resolve startup order
        try:
            self.startup_order = self._resolve_dependencies()
            self.shutdown_order = list(reversed(self.startup_order))
        except ValueError as e:
            if self.logger:
                self.logger.error(f"Failed to resolve dependencies: {e}")
            return False
        
        # Start services in order
        for service_name in self.startup_order:
            if not self._start_service(service_name):
                if self.logger:
                    self.logger.error(f"Failed to start service: {service_name}")
                return False
            
            # Brief delay between starts
            time.sleep(1)
        
        if self.logger:
            self.logger.info("All services started successfully")
        
        return True
    
    def _start_service(self, service_name: str) -> bool:
        """
        Start a specific service.
        
        Args:
            service_name: Service name
            
        Returns:
            True if started successfully
        """
        service = self.services[service_name]
        
        if self.logger:
            self.logger.info(f"Starting service: {service_name}")
        
        # Check dependencies are running
        for dep_name in service.dependencies:
            dep_service = self.services.get(dep_name)
            if not dep_service or dep_service.state != ServiceState.RUNNING:
                if self.logger:
                    self.logger.error(
                        f"Dependency {dep_name} not running for {service_name}"
                    )
                return False
        
        # Update state
        service.state = ServiceState.INITIALIZING
        
        # Start via process manager if available
        if self.process_manager:
            success = self.process_manager.start_process(service_name)
            
            if success:
                service.state = ServiceState.RUNNING
                service.started_at = datetime.utcnow()
                return True
            else:
                service.state = ServiceState.FAILED
                return False
        else:
            # No process manager - just mark as running
            service.state = ServiceState.RUNNING
            service.started_at = datetime.utcnow()
            return True
    
    def stop_all_services(self) -> bool:
        """
        Stop all services in reverse dependency order.
        
        Returns:
            True if all stopped successfully
        """
        if self.logger:
            self.logger.info("Stopping all services...")
        
        # Use shutdown order (reverse of startup)
        for service_name in self.shutdown_order:
            self._stop_service(service_name)
            time.sleep(0.5)
        
        if self.logger:
            self.logger.info("All services stopped")
        
        return True
    
    def _stop_service(self, service_name: str) -> bool:
        """
        Stop a specific service.
        
        Args:
            service_name: Service name
            
        Returns:
            True if stopped successfully
        """
        service = self.services[service_name]
        
        if service.state not in [ServiceState.RUNNING, ServiceState.DEGRADED]:
            return True
        
        if self.logger:
            self.logger.info(f"Stopping service: {service_name}")
        
        service.state = ServiceState.STOPPING
        
        # Stop via process manager if available
        if self.process_manager:
            success = self.process_manager.stop_process(
                service_name,
                timeout=service.shutdown_timeout
            )
            
            if success:
                service.state = ServiceState.STOPPED
                service.stopped_at = datetime.utcnow()
                return True
            else:
                service.state = ServiceState.FAILED
                return False
        else:
            service.state = ServiceState.STOPPED
            service.stopped_at = datetime.utcnow()
            return True
    
    def restart_service(self, service_name: str) -> bool:
        """
        Restart a service.
        
        Args:
            service_name: Service name
            
        Returns:
            True if restarted successfully
        """
        if self.logger:
            self.logger.info(f"Restarting service: {service_name}")
        
        service = self.services[service_name]
        
        # Stop service
        self._stop_service(service_name)
        time.sleep(1)
        
        # Start service
        success = self._start_service(service_name)
        
        if success:
            service.restart_count += 1
        
        return success
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get status of all services.
        
        Returns:
            Status dict
        """
        return {
            name: {
                'state': service.state.value,
                'started_at': service.started_at.isoformat() if service.started_at else None,
                'restart_count': service.restart_count,
                'dependencies': service.dependencies
            }
            for name, service in self.services.items()
        }
    
    def is_all_running(self) -> bool:
        """
        Check if all services are running.
        
        Returns:
            True if all running
        """
        return all(
            service.state == ServiceState.RUNNING
            for service in self.services.values()
        )


def create_service_orchestrator(
    logger=None,
    process_manager=None
) -> ServiceOrchestrator:
    """
    Factory function to create service orchestrator.
    
    Args:
        logger: Logger instance
        process_manager: Process manager instance
        
    Returns:
        ServiceOrchestrator instance
    """
    return ServiceOrchestrator(
        logger=logger,
        process_manager=process_manager
    )
