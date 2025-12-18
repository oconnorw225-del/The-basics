#!/usr/bin/env python3
"""
Centralized Configuration Management
Single source of truth for all system settings
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


@dataclass
class ServiceConfig:
    """Configuration for a service"""
    name: str
    enabled: bool = True
    port: int = 0
    host: str = "localhost"
    auto_start: bool = True
    max_retries: int = 3
    health_check_interval: int = 60
    env_vars: Dict[str, str] = field(default_factory=dict)


class ConfigManager:
    """
    Centralized configuration management.
    Loads configuration from environment variables, .env files, and config files.
    Validates required settings and provides type-safe access.
    """
    
    def __init__(
        self,
        config_dir: str = ".unified-system/config",
        env_file: str = ".env"
    ):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory for configuration files
            env_file: Path to .env file
        """
        self.config_dir = Path(config_dir)
        self.env_file = Path(env_file)
        self.config: Dict[str, Any] = {}
        self.services: Dict[str, ServiceConfig] = {}
        
        # Create config directory
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine environment
        self.environment = Environment(
            os.getenv('NODE_ENV', os.getenv('ENV', 'development')).lower()
        )
        
        # Load configurations
        self._load_env_file()
        self._load_config_files()
        self._load_service_configs()
        
    def _load_env_file(self):
        """Load environment variables from .env file."""
        if not self.env_file.exists():
            return
        
        try:
            with open(self.env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            # Only set if not already in environment
                            if key not in os.environ:
                                os.environ[key] = value.strip('"').strip("'")
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")
    
    def _load_config_files(self):
        """Load configuration from JSON files."""
        # Load main config
        main_config = self.config_dir / "config.json"
        if main_config.exists():
            try:
                with open(main_config) as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config.json: {e}")
        
        # Load environment-specific config
        env_config = self.config_dir / f"config.{self.environment.value}.json"
        if env_config.exists():
            try:
                with open(env_config) as f:
                    env_data = json.load(f)
                    # Merge with main config (env-specific overrides)
                    self.config.update(env_data)
            except Exception as e:
                print(f"Warning: Could not load environment config: {e}")
    
    def _load_service_configs(self):
        """Load service configurations."""
        # Define default service configurations
        self.services = {
            'python_backend': ServiceConfig(
                name='python_backend',
                enabled=True,
                port=int(os.getenv('PYTHON_PORT', 8000)),
                host=os.getenv('BACKEND_HOST', '0.0.0.0'),
                auto_start=True
            ),
            'node_server': ServiceConfig(
                name='node_server',
                enabled=True,
                port=int(os.getenv('PORT', 3000)),
                host=os.getenv('SERVER_HOST', '0.0.0.0'),
                auto_start=True
            ),
            'bot': ServiceConfig(
                name='bot',
                enabled=os.getenv('BOT_ENABLED', 'true').lower() == 'true',
                port=int(os.getenv('BOT_PORT', 9000)),
                host=os.getenv('BOT_HOST', '0.0.0.0'),
                auto_start=os.getenv('AUTO_START', 'true').lower() == 'true',
                env_vars={
                    'TRADING_MODE': os.getenv('TRADING_MODE', 'paper'),
                    'FREELANCE_ENABLED': os.getenv('FREELANCE_ENABLED', 'false'),
                    'AI_ENABLED': os.getenv('AI_ENABLED', 'false')
                }
            ),
            'health_monitor': ServiceConfig(
                name='health_monitor',
                enabled=True,
                auto_start=True,
                health_check_interval=int(os.getenv('HEALTH_CHECK_INTERVAL', 60))
            ),
            'error_handler': ServiceConfig(
                name='error_handler',
                enabled=True,
                auto_start=True
            )
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        # Try environment variable first
        env_value = os.getenv(key.upper())
        if env_value is not None:
            return self._convert_type(env_value)
        
        # Try config dictionary
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            value: Value to set
        """
        keys = key.split('.')
        current = self.config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _convert_type(self, value: str) -> Union[str, int, float, bool]:
        """Convert string value to appropriate type."""
        # Boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float
        try:
            return float(value)
        except ValueError:
            pass
        
        # String
        return value
    
    def validate_required(self, required_keys: List[str]) -> Dict[str, List[str]]:
        """
        Validate that required configuration keys are present.
        
        Args:
            required_keys: List of required configuration keys
            
        Returns:
            Dict with 'valid' boolean and 'missing' list
        """
        missing = []
        
        for key in required_keys:
            if self.get(key) is None:
                missing.append(key)
        
        return {
            'valid': len(missing) == 0,
            'missing': missing
        }
    
    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """
        Get service configuration.
        
        Args:
            service_name: Name of the service
            
        Returns:
            ServiceConfig or None
        """
        return self.services.get(service_name)
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    def get_database_url(self) -> Optional[str]:
        """Get database URL from environment."""
        return os.getenv('DATABASE_URL') or self.get('database.url')
    
    def get_redis_url(self) -> Optional[str]:
        """Get Redis URL from environment."""
        return os.getenv('REDIS_URL') or self.get('redis.url', 'redis://localhost:6379')
    
    def get_all_ports(self) -> Dict[str, int]:
        """Get all configured service ports."""
        return {
            name: service.port
            for name, service in self.services.items()
            if service.port > 0
        }
    
    def check_port_conflicts(self) -> List[Dict[str, Any]]:
        """
        Check for port conflicts between services.
        
        Returns:
            List of conflicts
        """
        conflicts = []
        ports = {}
        
        for name, service in self.services.items():
            if service.port > 0:
                if service.port in ports:
                    conflicts.append({
                        'port': service.port,
                        'services': [ports[service.port], name]
                    })
                else:
                    ports[service.port] = name
        
        return conflicts
    
    def save_config(self):
        """Save current configuration to file."""
        config_file = self.config_dir / "config.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_secrets(self) -> Dict[str, str]:
        """
        Get all secret/sensitive configuration values.
        
        Returns:
            Dict of secrets (API keys, tokens, etc.)
        """
        secrets = {}
        
        # Common secret environment variables
        secret_keys = [
            'NDAX_API_KEY',
            'NDAX_API_SECRET',
            'STRIPE_API_KEY',
            'STRIPE_SECRET_KEY',
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'HUGGINGFACE_API_KEY',
            'DATABASE_URL',
            'REDIS_URL',
            'JWT_SECRET'
        ]
        
        for key in secret_keys:
            value = os.getenv(key)
            if value:
                secrets[key] = value
        
        return secrets
    
    def __repr__(self) -> str:
        """String representation."""
        return f"ConfigManager(environment={self.environment.value}, services={len(self.services)})"


def create_config_manager(config_dir: str = None, env_file: str = None) -> ConfigManager:
    """
    Factory function to create configuration manager.
    
    Args:
        config_dir: Directory for config files
        env_file: Path to .env file
        
    Returns:
        ConfigManager instance
    """
    kwargs = {}
    if config_dir:
        kwargs['config_dir'] = config_dir
    if env_file:
        kwargs['env_file'] = env_file
    
    return ConfigManager(**kwargs)
