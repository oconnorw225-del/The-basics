#!/usr/bin/env python3
"""
Centralized Logging System
Consistent logging across all components with structured output
"""

import logging
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler


class UnifiedLogger:
    """
    Centralized logging system with structured output.
    Provides consistent logging across all system components.
    """
    
    def __init__(
        self,
        name: str = "UnifiedSystem",
        log_dir: str = ".unified-system/logs",
        log_level: str = "INFO",
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5,
        json_format: bool = True
    ):
        """
        Initialize unified logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARN, ERROR, FATAL)
            max_bytes: Maximum bytes per log file
            backup_count: Number of backup files to keep
            json_format: Use JSON structured logging
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.json_format = json_format
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers = []
        
        # Create formatters
        if json_format:
            formatter = self._create_json_formatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = self.log_dir / f"{name.lower()}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Error log file
        error_log_file = self.log_dir / f"{name.lower()}_errors.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # Context storage for structured logging
        self.context: Dict[str, Any] = {}
        
    def _create_json_formatter(self):
        """Create JSON formatter for structured logging."""
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # Add exception info if present
                if record.exc_info:
                    log_data['exception'] = self.formatException(record.exc_info)
                
                # Add any extra fields
                if hasattr(record, 'context'):
                    log_data['context'] = record.context
                    
                return json.dumps(log_data)
        
        return JsonFormatter()
    
    def set_context(self, **kwargs):
        """
        Set context values for all subsequent log messages.
        
        Args:
            **kwargs: Context key-value pairs
        """
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context values."""
        self.context = {}
    
    def _add_context(self, extra: Optional[Dict] = None) -> Dict:
        """Add context to log extra data."""
        if extra is None:
            extra = {}
        
        if self.context:
            extra['context'] = {**self.context, **extra.get('context', {})}
        
        return extra
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        extra = self._add_context(kwargs.get('extra'))
        self.logger.debug(message, extra=extra)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        extra = self._add_context(kwargs.get('extra'))
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        extra = self._add_context(kwargs.get('extra'))
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message."""
        extra = self._add_context(kwargs.get('extra'))
        self.logger.error(message, exc_info=exc_info, extra=extra)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical/fatal message."""
        extra = self._add_context(kwargs.get('extra'))
        self.logger.critical(message, exc_info=exc_info, extra=extra)
    
    def fatal(self, message: str, exc_info: bool = False, **kwargs):
        """Alias for critical."""
        self.critical(message, exc_info=exc_info, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        extra = self._add_context(kwargs.get('extra'))
        self.logger.exception(message, extra=extra)
    
    def metric(self, metric_name: str, value: float, tags: Optional[Dict] = None):
        """
        Log performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags/labels
        """
        metric_data = {
            'metric': metric_name,
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if tags:
            metric_data['tags'] = tags
        
        extra = self._add_context({'context': metric_data})
        self.logger.info(f"METRIC: {metric_name}={value}", extra=extra)


def create_logger(
    name: str = "UnifiedSystem",
    log_level: str = None,
    json_format: bool = True
) -> UnifiedLogger:
    """
    Factory function to create a unified logger.
    
    Args:
        name: Logger name
        log_level: Logging level (defaults to INFO or from environment)
        json_format: Use JSON structured logging
        
    Returns:
        UnifiedLogger instance
    """
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    return UnifiedLogger(
        name=name,
        log_level=log_level,
        json_format=json_format
    )
