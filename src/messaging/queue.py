#!/usr/bin/env python3
"""
Inter-service Messaging Queue
Decouples services and provides async communication
"""

import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from collections import deque
from enum import Enum
import json


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3


class Message:
    """Represents a message"""
    
    def __init__(
        self,
        topic: str,
        data: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
        persistent: bool = False
    ):
        """
        Initialize message.
        
        Args:
            topic: Message topic
            data: Message data
            priority: Message priority
            persistent: Whether message should be persisted
        """
        self.message_id = f"{topic}_{int(time.time() * 1000)}"
        self.topic = topic
        self.data = data
        self.priority = priority
        self.persistent = persistent
        self.timestamp = datetime.utcnow()
        self.retry_count = 0


class MessageQueue:
    """
    Inter-service messaging queue.
    Provides publish/subscribe and request/response patterns.
    """
    
    def __init__(
        self,
        logger=None,
        max_queue_size: int = 10000,
        max_retries: int = 3,
        dead_letter_enabled: bool = True
    ):
        """
        Initialize message queue.
        
        Args:
            logger: Logger instance
            max_queue_size: Maximum queue size
            max_retries: Maximum retry attempts
            dead_letter_enabled: Enable dead letter queue
        """
        self.logger = logger
        self.max_queue_size = max_queue_size
        self.max_retries = max_retries
        self.dead_letter_enabled = dead_letter_enabled
        
        # Message queues by topic
        self.queues: Dict[str, deque] = {}
        
        # Subscribers
        self.subscribers: Dict[str, List[Callable]] = {}
        
        # Dead letter queue
        self.dead_letter_queue: deque = deque(maxlen=1000)
        
        # Request/response tracking
        self.pending_requests: Dict[str, Message] = {}
        
        # Statistics
        self.stats = {
            'published': 0,
            'delivered': 0,
            'failed': 0,
            'dead_lettered': 0
        }
    
    def create_topic(self, topic: str):
        """
        Create a new topic.
        
        Args:
            topic: Topic name
        """
        if topic not in self.queues:
            self.queues[topic] = deque(maxlen=self.max_queue_size)
            self.subscribers[topic] = []
            
            if self.logger:
                self.logger.info(f"Created topic: {topic}")
    
    def publish(
        self,
        topic: str,
        data: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
        persistent: bool = False
    ) -> str:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic name
            data: Message data
            priority: Message priority
            persistent: Persist message
            
        Returns:
            Message ID
        """
        # Create topic if it doesn't exist
        if topic not in self.queues:
            self.create_topic(topic)
        
        # Create message
        message = Message(
            topic=topic,
            data=data,
            priority=priority,
            persistent=persistent
        )
        
        # Add to queue
        self.queues[topic].append(message)
        self.stats['published'] += 1
        
        # Immediately deliver to subscribers
        self._deliver_to_subscribers(topic, message)
        
        if self.logger:
            self.logger.debug(f"Published message to {topic}: {message.message_id}")
        
        return message.message_id
    
    def subscribe(self, topic: str, callback: Callable):
        """
        Subscribe to a topic.
        
        Args:
            topic: Topic name
            callback: Callback function
        """
        # Create topic if it doesn't exist
        if topic not in self.subscribers:
            self.create_topic(topic)
        
        self.subscribers[topic].append(callback)
        
        if self.logger:
            self.logger.info(f"New subscriber for topic: {topic}")
    
    def unsubscribe(self, topic: str, callback: Callable):
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic name
            callback: Callback function
        """
        if topic in self.subscribers and callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)
            
            if self.logger:
                self.logger.info(f"Unsubscribed from topic: {topic}")
    
    def _deliver_to_subscribers(self, topic: str, message: Message):
        """
        Deliver message to subscribers.
        
        Args:
            topic: Topic name
            message: Message to deliver
        """
        if topic not in self.subscribers:
            return
        
        for callback in self.subscribers[topic]:
            try:
                callback(message)
                self.stats['delivered'] += 1
            except Exception as e:
                self.stats['failed'] += 1
                
                if self.logger:
                    self.logger.error(
                        f"Subscriber callback failed for {topic}: {e}",
                        exc_info=True
                    )
                
                # Retry logic
                if message.retry_count < self.max_retries:
                    message.retry_count += 1
                    # Re-queue for retry
                    self.queues[topic].append(message)
                elif self.dead_letter_enabled:
                    # Move to dead letter queue
                    self.dead_letter_queue.append(message)
                    self.stats['dead_lettered'] += 1
                    
                    if self.logger:
                        self.logger.warning(
                            f"Message moved to dead letter queue: {message.message_id}"
                        )
    
    def request(
        self,
        topic: str,
        data: Any,
        timeout: float = 30.0
    ) -> Optional[Any]:
        """
        Send request and wait for response.
        
        Args:
            topic: Topic name
            data: Request data
            timeout: Response timeout
            
        Returns:
            Response data or None
        """
        # Create request message
        request_id = f"req_{int(time.time() * 1000)}"
        message = Message(
            topic=f"{topic}_request",
            data={
                'request_id': request_id,
                'data': data
            }
        )
        
        # Publish request
        self.publish(f"{topic}_request", message.data)
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check for response
            if request_id in self.pending_requests:
                response = self.pending_requests.pop(request_id)
                return response.data
            
            time.sleep(0.1)
        
        # Timeout
        if self.logger:
            self.logger.warning(f"Request timeout: {request_id}")
        
        return None
    
    def respond(self, request_id: str, data: Any):
        """
        Send response to a request.
        
        Args:
            request_id: Request ID
            data: Response data
        """
        message = Message(
            topic='response',
            data=data
        )
        
        self.pending_requests[request_id] = message
    
    def get_queue_size(self, topic: str) -> int:
        """
        Get queue size for a topic.
        
        Args:
            topic: Topic name
            
        Returns:
            Queue size
        """
        if topic in self.queues:
            return len(self.queues[topic])
        return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get message queue statistics.
        
        Returns:
            Statistics dict
        """
        total_queued = sum(len(q) for q in self.queues.values())
        
        return {
            **self.stats,
            'topics': len(self.queues),
            'total_queued': total_queued,
            'dead_letter_size': len(self.dead_letter_queue),
            'subscriber_count': sum(len(s) for s in self.subscribers.values())
        }
    
    def clear_topic(self, topic: str):
        """
        Clear all messages from a topic.
        
        Args:
            topic: Topic name
        """
        if topic in self.queues:
            self.queues[topic].clear()
            
            if self.logger:
                self.logger.info(f"Cleared topic: {topic}")


def create_message_queue(
    logger=None,
    max_queue_size: int = 10000
) -> MessageQueue:
    """
    Factory function to create message queue.
    
    Args:
        logger: Logger instance
        max_queue_size: Maximum queue size
        
    Returns:
        MessageQueue instance
    """
    return MessageQueue(
        logger=logger,
        max_queue_size=max_queue_size
    )
