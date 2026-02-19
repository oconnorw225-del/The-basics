#!/usr/bin/env python3
"""
Unified API Gateway
Single entry point for all API requests
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from collections import defaultdict
import time


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def check(self, client_id: str) -> bool:
        """
        Check if request is allowed.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if allowed
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Record request
        self.requests[client_id].append(now)
        return True


class APIGateway:
    """
    Unified API gateway.
    Routes requests to appropriate backends with validation and rate limiting.
    """
    
    def __init__(
        self,
        logger=None,
        rate_limit: int = 100,
        rate_window: int = 60
    ):
        """
        Initialize API gateway.
        
        Args:
            logger: Logger instance
            rate_limit: Requests per window
            rate_window: Window size (seconds)
        """
        self.logger = logger
        self.rate_limiter = RateLimiter(rate_limit, rate_window)
        
        # Route handlers
        self.routes: Dict[str, Callable] = {}
        
        # Middleware
        self.middleware: List[Callable] = []
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited': 0
        }
    
    def register_route(self, path: str, handler: Callable, methods: Optional[List[str]] = None):
        """
        Register a route handler.
        
        Args:
            path: Route path
            handler: Handler function
            methods: Allowed HTTP methods
        """
        if methods is None:
            methods = ['GET', 'POST']
        
        self.routes[path] = {
            'handler': handler,
            'methods': methods
        }
        
        if self.logger:
            self.logger.info(f"Registered route: {path} {methods}")
    
    def add_middleware(self, middleware: Callable):
        """
        Add middleware function.
        
        Args:
            middleware: Middleware function
        """
        self.middleware.append(middleware)
    
    async def handle_request(
        self,
        path: str,
        method: str,
        client_id: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Handle an API request.
        
        Args:
            path: Request path
            method: HTTP method
            client_id: Client identifier
            data: Request data
            headers: Request headers
            
        Returns:
            Response dict
        """
        self.stats['total_requests'] += 1
        
        # Rate limiting
        if not self.rate_limiter.check(client_id):
            self.stats['rate_limited'] += 1
            
            return {
                'status': 429,
                'error': 'Rate limit exceeded',
                'retry_after': self.rate_limiter.window_seconds
            }
        
        # Find route
        if path not in self.routes:
            self.stats['failed_requests'] += 1
            
            return {
                'status': 404,
                'error': f'Route not found: {path}'
            }
        
        route = self.routes[path]
        
        # Check method
        if method not in route['methods']:
            self.stats['failed_requests'] += 1
            
            return {
                'status': 405,
                'error': f'Method not allowed: {method}'
            }
        
        # Execute middleware
        request_context = {
            'path': path,
            'method': method,
            'client_id': client_id,
            'data': data,
            'headers': headers or {}
        }
        
        for middleware in self.middleware:
            try:
                result = middleware(request_context)
                if result is not None:
                    # Middleware returned response (auth failed, etc.)
                    self.stats['failed_requests'] += 1
                    return result
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Middleware error: {e}")
                
                self.stats['failed_requests'] += 1
                return {
                    'status': 500,
                    'error': 'Internal server error'
                }
        
        # Execute handler
        try:
            handler = route['handler']
            result = await handler(request_context)
            
            self.stats['successful_requests'] += 1
            
            return {
                'status': 200,
                'data': result
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Handler error for {path}: {e}", exc_info=True)
            
            self.stats['failed_requests'] += 1
            
            return {
                'status': 500,
                'error': 'Internal server error'
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get gateway statistics.
        
        Returns:
            Statistics dict
        """
        return {
            **self.stats,
            'routes': len(self.routes),
            'middleware': len(self.middleware),
            'success_rate': (
                self.stats['successful_requests'] / self.stats['total_requests']
                if self.stats['total_requests'] > 0 else 0
            )
        }


def create_api_gateway(logger=None, rate_limit: int = 100, enable_access_control: bool = True) -> APIGateway:
    """
    Factory function to create API gateway.
    
    Args:
        logger: Logger instance
        rate_limit: Rate limit (requests per minute)
        enable_access_control: Enable bot access control middleware
        
    Returns:
        APIGateway instance
    """
    gateway = APIGateway(logger=logger, rate_limit=rate_limit)
    
    # Add bot access control middleware if enabled
    if enable_access_control:
        try:
            from ..middleware.bot_access_control import create_access_control_middleware, access_control_middleware
            
            access_control = create_access_control_middleware()
            gateway.add_middleware(access_control_middleware(access_control))
            
            if logger:
                logger.info("Bot access control middleware enabled")
        except Exception as e:
            if logger:
                logger.warning(f"Failed to enable bot access control: {e}")
    
    return gateway
