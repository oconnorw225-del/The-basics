#!/usr/bin/env python3
"""
Bot Access Control Middleware
Enforces public/private access rules based on bot-public-access.json configuration
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class BotAccessControl:
    """
    Middleware for controlling bot access to endpoints.
    Enforces public/private access rules.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize bot access control.
        
        Args:
            config_path: Path to bot-public-access.json config file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "bot-public-access.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Build access rules
        self.public_paths = self._build_public_paths()
        self.private_patterns = self._build_private_patterns()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load bot access configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _build_public_paths(self) -> List[str]:
        """Build list of public endpoint paths."""
        public_endpoints = self.config.get('public_endpoints', {}).get('endpoints', [])
        return [endpoint['path'] for endpoint in public_endpoints]
    
    def _build_private_patterns(self) -> List[re.Pattern]:
        """Build regex patterns for private endpoints."""
        private_endpoints = self.config.get('private_endpoints', {}).get('endpoints', [])
        patterns = []
        
        for endpoint in private_endpoints:
            path = endpoint['path']
            # Convert wildcard paths to regex
            # e.g., /api/credentials/* -> ^/api/credentials/.*$
            regex_path = path.replace('*', '.*')
            if not regex_path.startswith('^'):
                regex_path = '^' + regex_path
            if not regex_path.endswith('$'):
                regex_path = regex_path + '$'
            patterns.append(re.compile(regex_path))
        
        return patterns
    
    def is_public_endpoint(self, path: str) -> bool:
        """
        Check if endpoint is public.
        
        Args:
            path: Request path
            
        Returns:
            True if public endpoint
        """
        # Exact match for public paths
        if path in self.public_paths:
            return True
        
        # Check if it matches any private pattern
        for pattern in self.private_patterns:
            if pattern.match(path):
                return False
        
        # Default to private for safety
        return False
    
    def is_private_endpoint(self, path: str) -> bool:
        """
        Check if endpoint is private.
        
        Args:
            path: Request path
            
        Returns:
            True if private endpoint
        """
        return not self.is_public_endpoint(path)
    
    def check_access(
        self,
        path: str,
        method: str,
        bot_type: str = "public",
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if bot has access to endpoint.
        
        Args:
            path: Request path
            method: HTTP method
            bot_type: Type of bot (public, registered, trusted, admin)
            api_key: API key for authentication
            
        Returns:
            Dict with 'allowed' bool and optional 'reason' string
        """
        # Check if endpoint is public
        if self.is_public_endpoint(path):
            return {
                'allowed': True,
                'access_level': 'public',
                'message': 'Public endpoint access granted'
            }
        
        # Private endpoint - check authentication
        if bot_type == "public" and not api_key:
            return {
                'allowed': False,
                'access_level': 'public',
                'reason': 'Private endpoint requires authentication',
                'message': 'This endpoint is not publicly accessible'
            }
        
        # Check bot access level
        bot_levels = self.config.get('bot_access_levels', {}).get('levels', {})
        bot_level = bot_levels.get(bot_type, {})
        
        if not bot_level:
            return {
                'allowed': False,
                'reason': f'Unknown bot type: {bot_type}',
                'message': 'Invalid bot type'
            }
        
        # Check if bot type requires authentication
        if bot_level.get('authentication_required', False) and not api_key:
            return {
                'allowed': False,
                'access_level': bot_type,
                'reason': 'Authentication required',
                'message': 'API key required for this bot type'
            }
        
        # Check additional access for registered/trusted bots
        additional_access = bot_level.get('additional_access', [])
        if path in additional_access:
            return {
                'allowed': True,
                'access_level': bot_type,
                'message': f'{bot_type.capitalize()} bot access granted'
            }
        
        # Admin bots have full access
        if bot_type == "admin":
            return {
                'allowed': True,
                'access_level': 'admin',
                'message': 'Admin access granted'
            }
        
        # Trusted bots have access to most endpoints
        if bot_type == "trusted":
            # Check if it's explicitly forbidden
            forbidden_paths = ['/api/admin/', '/kill-switch']
            if any(forbidden in path for forbidden in forbidden_paths):
                return {
                    'allowed': False,
                    'access_level': 'trusted',
                    'reason': 'Endpoint restricted to admin only',
                    'message': 'Insufficient permissions'
                }
            return {
                'allowed': True,
                'access_level': 'trusted',
                'message': 'Trusted bot access granted'
            }
        
        # Default deny for safety
        return {
            'allowed': False,
            'access_level': bot_type,
            'reason': 'Access not explicitly granted',
            'message': 'Access denied'
        }
    
    def sanitize_response(self, response: Dict[str, Any], access_level: str) -> Dict[str, Any]:
        """
        Sanitize response data based on access level.
        
        Args:
            response: Response data
            access_level: Access level (public, registered, trusted, admin)
            
        Returns:
            Sanitized response
        """
        if access_level == "admin":
            # Admin sees everything
            return response
        
        # Get private data categories
        private_categories = self.config.get('data_classification', {}).get('private', {}).get('categories', [])
        
        # Remove private data from response
        sanitized = {}
        for key, value in response.items():
            # Check if key matches private category
            if any(category in key.lower() for category in ['credential', 'key', 'secret', 'password', 'private']):
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        
        return sanitized
    
    def get_public_info(self) -> Dict[str, Any]:
        """
        Get public platform information.
        
        Returns:
            Public platform info
        """
        return self.config.get('platform_info', {})
    
    def get_public_endpoints(self) -> List[Dict[str, str]]:
        """
        Get list of public endpoints.
        
        Returns:
            List of public endpoint info
        """
        return self.config.get('public_endpoints', {}).get('endpoints', [])
    
    def log_access_attempt(
        self,
        path: str,
        method: str,
        bot_type: str,
        allowed: bool,
        client_id: str = "unknown"
    ):
        """
        Log access attempt (for security monitoring).
        
        Args:
            path: Request path
            method: HTTP method
            bot_type: Type of bot
            allowed: Whether access was allowed
            client_id: Client identifier
        """
        # In production, this should log to a proper logging system
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'client_id': client_id,
            'bot_type': bot_type,
            'path': path,
            'method': method,
            'allowed': allowed,
            'endpoint_type': 'public' if self.is_public_endpoint(path) else 'private'
        }
        
        # For now, just track failed access attempts to private endpoints
        if not allowed and self.is_private_endpoint(path):
            print(f"⚠️ Access denied: {client_id} ({bot_type}) -> {method} {path}")


def create_access_control_middleware(config_path: Optional[str] = None):
    """
    Factory function to create access control middleware.
    
    Args:
        config_path: Path to config file
        
    Returns:
        BotAccessControl instance
    """
    return BotAccessControl(config_path)


# Example middleware function for use with API Gateway
def access_control_middleware(access_control: BotAccessControl):
    """
    Create middleware function for API Gateway.
    
    Args:
        access_control: BotAccessControl instance
        
    Returns:
        Middleware function
    """
    def middleware(request_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Middleware function to check access.
        
        Args:
            request_context: Request context from API Gateway
            
        Returns:
            None if access allowed, error response if denied
        """
        path = request_context.get('path', '')
        method = request_context.get('method', 'GET')
        headers = request_context.get('headers', {})
        
        # Extract bot type and API key from headers
        bot_type = headers.get('X-Bot-Type', 'public')
        api_key = headers.get('X-API-Key') or headers.get('Authorization', '').replace('Bearer ', '')
        client_id = request_context.get('client_id', 'unknown')
        
        # Check access
        access_result = access_control.check_access(path, method, bot_type, api_key)
        
        # Log attempt
        access_control.log_access_attempt(
            path, method, bot_type, access_result['allowed'], client_id
        )
        
        # Return error response if denied
        if not access_result['allowed']:
            return {
                'status': 403,
                'error': 'Access denied',
                'message': access_result.get('message', 'You do not have permission to access this endpoint'),
                'reason': access_result.get('reason', 'Insufficient permissions')
            }
        
        # Access granted - return None to continue processing
        return None
    
    return middleware


if __name__ == "__main__":
    # Test the access control
    access_control = create_access_control_middleware()
    
    print("🔒 Bot Access Control Test")
    print("=" * 60)
    
    # Test public endpoint
    result = access_control.check_access("/health", "GET", "public")
    print(f"\n✅ Public bot -> /health: {result['allowed']}")
    print(f"   Message: {result['message']}")
    
    # Test private endpoint without auth
    result = access_control.check_access("/api/credentials/list", "GET", "public")
    print(f"\n❌ Public bot -> /api/credentials/list: {result['allowed']}")
    print(f"   Message: {result['message']}")
    
    # Test private endpoint with trusted bot
    result = access_control.check_access("/api/trading/status", "GET", "trusted", api_key="test-key")
    print(f"\n✅ Trusted bot -> /api/trading/status: {result['allowed']}")
    print(f"   Message: {result['message']}")
    
    # Test admin endpoint with trusted bot
    result = access_control.check_access("/api/admin/config", "GET", "trusted", api_key="test-key")
    print(f"\n❌ Trusted bot -> /api/admin/config: {result['allowed']}")
    print(f"   Message: {result['message']}")
    
    # Test admin endpoint with admin bot
    result = access_control.check_access("/api/admin/config", "GET", "admin", api_key="admin-key")
    print(f"\n✅ Admin bot -> /api/admin/config: {result['allowed']}")
    print(f"   Message: {result['message']}")
    
    print("\n" + "=" * 60)
    print("📋 Public Platform Information:")
    print(json.dumps(access_control.get_public_info(), indent=2))
