#!/usr/bin/env python3
"""
AI System Manager
Coordinates all AI components (HuggingFace, paid bot, chimera)
"""

import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
from collections import deque
import asyncio


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task execution status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AITask:
    """Represents an AI task"""
    
    def __init__(
        self,
        task_id: str,
        task_type: str,
        data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[int] = None
    ):
        """
        Initialize AI task.
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task
            data: Task data
            priority: Task priority
            timeout: Task timeout (seconds)
        """
        self.task_id = task_id
        self.task_type = task_type
        self.data = data
        self.priority = priority
        self.timeout = timeout
        
        self.status = TaskStatus.QUEUED
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.retry_count = 0


class AIManager:
    """
    AI system manager.
    Coordinates all AI components and manages task execution.
    """
    
    def __init__(
        self,
        logger=None,
        error_handler=None,
        max_queue_size: int = 100,
        max_concurrent_tasks: int = 5,
        max_retries: int = 3,
        rate_limit_per_minute: int = 60
    ):
        """
        Initialize AI manager.
        
        Args:
            logger: Logger instance
            error_handler: Error handler instance
            max_queue_size: Maximum queue size
            max_concurrent_tasks: Max concurrent tasks
            max_retries: Maximum retry attempts
            rate_limit_per_minute: Rate limit (tasks per minute)
        """
        self.logger = logger
        self.error_handler = error_handler
        self.max_queue_size = max_queue_size
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_retries = max_retries
        self.rate_limit_per_minute = rate_limit_per_minute
        
        # Task queues by priority
        self.task_queues: Dict[TaskPriority, deque] = {
            TaskPriority.CRITICAL: deque(),
            TaskPriority.HIGH: deque(),
            TaskPriority.NORMAL: deque(),
            TaskPriority.LOW: deque()
        }
        
        # Active tasks
        self.active_tasks: Dict[str, AITask] = {}
        
        # Completed tasks (recent)
        self.completed_tasks: deque = deque(maxlen=1000)
        
        # AI component integrations
        self.components: Dict[str, Dict[str, Any]] = {}
        
        # Rate limiting
        self.task_timestamps: deque = deque(maxlen=rate_limit_per_minute)
        
        # Cost tracking
        self.total_cost = 0.0
        self.cost_by_component: Dict[str, float] = {}
        
        # Task handlers
        self.task_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            'tasks_queued': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'tasks_cancelled': 0
        }
    
    def register_component(
        self,
        name: str,
        component_type: str,
        config: Dict[str, Any],
        enabled: bool = True
    ):
        """
        Register an AI component.
        
        Args:
            name: Component name
            component_type: Type (huggingface, bot, chimera)
            config: Component configuration
            enabled: Whether component is enabled
        """
        self.components[name] = {
            'type': component_type,
            'config': config,
            'enabled': enabled,
            'tasks_processed': 0,
            'total_cost': 0.0
        }
        
        self.cost_by_component[name] = 0.0
        
        if self.logger:
            self.logger.info(
                f"Registered AI component: {name} (type: {component_type})"
            )
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """
        Register a task handler.
        
        Args:
            task_type: Task type
            handler: Handler function
        """
        self.task_handlers[task_type] = handler
        
        if self.logger:
            self.logger.debug(f"Registered task handler for: {task_type}")
    
    def queue_task(
        self,
        task_type: str,
        data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """
        Queue an AI task.
        
        Args:
            task_type: Task type
            data: Task data
            priority: Task priority
            timeout: Task timeout
            
        Returns:
            Task ID or None if queue is full
        """
        # Check rate limit
        if not self._check_rate_limit():
            if self.logger:
                self.logger.warning("Rate limit exceeded, task queuing delayed")
            return None
        
        # Check queue size
        total_queued = sum(len(q) for q in self.task_queues.values())
        if total_queued >= self.max_queue_size:
            if self.logger:
                self.logger.warning("Task queue full")
            return None
        
        # Create task
        task_id = f"{task_type}_{int(time.time() * 1000)}"
        task = AITask(
            task_id=task_id,
            task_type=task_type,
            data=data,
            priority=priority,
            timeout=timeout
        )
        
        # Add to appropriate queue
        self.task_queues[priority].append(task)
        self.stats['tasks_queued'] += 1
        
        if self.logger:
            self.logger.info(
                f"Queued task {task_id} with priority {priority.name}"
            )
        
        return task_id
    
    def _check_rate_limit(self) -> bool:
        """
        Check if rate limit allows new task.
        
        Returns:
            True if within rate limit
        """
        now = time.time()
        
        # Remove old timestamps
        while self.task_timestamps and self.task_timestamps[0] < now - 60:
            self.task_timestamps.popleft()
        
        # Check limit
        if len(self.task_timestamps) >= self.rate_limit_per_minute:
            return False
        
        # Record timestamp
        self.task_timestamps.append(now)
        return True
    
    def get_next_task(self) -> Optional[AITask]:
        """
        Get next task from queue (priority-based).
        
        Returns:
            Next task or None
        """
        # Check in priority order
        for priority in [
            TaskPriority.CRITICAL,
            TaskPriority.HIGH,
            TaskPriority.NORMAL,
            TaskPriority.LOW
        ]:
            if self.task_queues[priority]:
                return self.task_queues[priority].popleft()
        
        return None
    
    async def execute_task(self, task: AITask) -> bool:
        """
        Execute an AI task.
        
        Args:
            task: Task to execute
            
        Returns:
            True if successful
        """
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        self.active_tasks[task.task_id] = task
        
        if self.logger:
            self.logger.info(f"Executing task {task.task_id}")
        
        try:
            # Get handler for task type
            if task.task_type not in self.task_handlers:
                raise ValueError(f"No handler for task type: {task.task_type}")
            
            handler = self.task_handlers[task.task_type]
            
            # Execute with timeout
            if task.timeout:
                result = await asyncio.wait_for(
                    handler(task.data),
                    timeout=task.timeout
                )
            else:
                result = await handler(task.data)
            
            # Task completed successfully
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            self.stats['tasks_completed'] += 1
            
            # Track cost if available
            if isinstance(result, dict) and 'cost' in result:
                self.total_cost += result['cost']
            
            if self.logger:
                self.logger.info(f"Task {task.task_id} completed successfully")
            
            return True
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = "Task timeout"
            self.stats['tasks_failed'] += 1
            
            if self.logger:
                self.logger.error(f"Task {task.task_id} timed out")
            
            return False
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.stats['tasks_failed'] += 1
            
            if self.logger:
                self.logger.error(
                    f"Task {task.task_id} failed: {e}",
                    exc_info=True
                )
            
            # Handle error
            if self.error_handler:
                self.error_handler.handle_error(
                    e,
                    context={'task_id': task.task_id, 'task_type': task.task_type}
                )
            
            # Retry if allowed
            if task.retry_count < self.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.QUEUED
                self.task_queues[task.priority].append(task)
                
                if self.logger:
                    self.logger.info(
                        f"Retrying task {task.task_id} "
                        f"(attempt {task.retry_count + 1}/{self.max_retries})"
                    )
            
            return False
            
        finally:
            # Move to completed tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
                self.completed_tasks.append(task)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a queued or active task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if cancelled
        """
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            self.stats['tasks_cancelled'] += 1
            
            if self.logger:
                self.logger.info(f"Cancelled active task {task_id}")
            
            return True
        
        # Check queued tasks
        for priority_queue in self.task_queues.values():
            for i, task in enumerate(priority_queue):
                if task.task_id == task_id:
                    task.status = TaskStatus.CANCELLED
                    priority_queue.remove(task)
                    self.completed_tasks.append(task)
                    self.stats['tasks_cancelled'] += 1
                    
                    if self.logger:
                        self.logger.info(f"Cancelled queued task {task_id}")
                    
                    return True
        
        return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task status.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status dict or None
        """
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return self._task_to_dict(task)
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return self._task_to_dict(task)
        
        # Check queued tasks
        for priority_queue in self.task_queues.values():
            for task in priority_queue:
                if task.task_id == task_id:
                    return self._task_to_dict(task)
        
        return None
    
    def _task_to_dict(self, task: AITask) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'task_id': task.task_id,
            'task_type': task.task_type,
            'status': task.status.value,
            'priority': task.priority.name,
            'created_at': task.created_at.isoformat(),
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'retry_count': task.retry_count,
            'error': task.error
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get AI manager statistics.
        
        Returns:
            Statistics dict
        """
        total_queued = sum(len(q) for q in self.task_queues.values())
        
        return {
            **self.stats,
            'active_tasks': len(self.active_tasks),
            'queued_tasks': total_queued,
            'total_cost': self.total_cost,
            'cost_by_component': self.cost_by_component,
            'components': {
                name: {
                    'enabled': comp['enabled'],
                    'tasks_processed': comp['tasks_processed']
                }
                for name, comp in self.components.items()
            }
        }


def create_ai_manager(
    logger=None,
    error_handler=None,
    max_concurrent_tasks: int = 5
) -> AIManager:
    """
    Factory function to create AI manager.
    
    Args:
        logger: Logger instance
        error_handler: Error handler instance
        max_concurrent_tasks: Max concurrent tasks
        
    Returns:
        AIManager instance
    """
    return AIManager(
        logger=logger,
        error_handler=error_handler,
        max_concurrent_tasks=max_concurrent_tasks
    )
