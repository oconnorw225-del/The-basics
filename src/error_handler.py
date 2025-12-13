#!/usr/bin/env python3
"""
Centralized Error Handling
Catches, logs, and recovers from errors across all components
"""

import sys
import traceback
import time
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from datetime import datetime
from pathlib import Path


class ErrorSeverity(Enum):
    """Error severity levels"""
    WARNING = "warning"
    RECOVERABLE = "recoverable"
    FATAL = "fatal"


class ErrorCategory(Enum):
    """Error categories"""
    NETWORK = "network"
    DATABASE = "database"
    API = "api"
    FILESYSTEM = "filesystem"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    UNKNOWN = "unknown"


class ErrorHandler:
    """
    Centralized error handling system.
    Catches, categorizes, logs, and attempts recovery from errors.
    """
    
    def __init__(
        self,
        logger=None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        exponential_backoff: bool = True,
        crash_dump_dir: str = ".unified-system/crash-dumps"
    ):
        """
        Initialize error handler.
        
        Args:
            logger: Logger instance (optional)
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
            exponential_backoff: Use exponential backoff for retries
            crash_dump_dir: Directory for crash dumps
        """
        self.logger = logger
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.exponential_backoff = exponential_backoff
        self.crash_dump_dir = Path(crash_dump_dir)
        
        # Create crash dump directory
        self.crash_dump_dir.mkdir(parents=True, exist_ok=True)
        
        # Error statistics
        self.error_counts: Dict[str, int] = {}
        self.last_errors: List[Dict[str, Any]] = []
        self.max_error_history = 100
        
        # Notification handlers
        self.notification_handlers: List[Callable] = []
        
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """
        Categorize an error based on its type.
        
        Args:
            error: Exception to categorize
            
        Returns:
            ErrorCategory
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # Network errors
        if any(keyword in error_type.lower() for keyword in ['connection', 'timeout', 'network']):
            return ErrorCategory.NETWORK
        if any(keyword in error_msg for keyword in ['connection', 'timeout', 'network']):
            return ErrorCategory.NETWORK
        
        # Database errors
        if any(keyword in error_type.lower() for keyword in ['database', 'sql', 'db']):
            return ErrorCategory.DATABASE
        
        # API errors
        if any(keyword in error_type.lower() for keyword in ['api', 'http', 'request']):
            return ErrorCategory.API
        
        # Filesystem errors
        if any(keyword in error_type.lower() for keyword in ['file', 'io', 'path']):
            return ErrorCategory.FILESYSTEM
        if isinstance(error, (FileNotFoundError, PermissionError, IOError)):
            return ErrorCategory.FILESYSTEM
        
        # Configuration errors
        if any(keyword in error_type.lower() for keyword in ['config', 'environment', 'setting']):
            return ErrorCategory.CONFIGURATION
        
        # Security errors
        if any(keyword in error_type.lower() for keyword in ['security', 'auth', 'permission']):
            return ErrorCategory.SECURITY
        
        return ErrorCategory.UNKNOWN
    
    def assess_severity(self, error: Exception, context: Optional[Dict] = None) -> ErrorSeverity:
        """
        Assess error severity.
        
        Args:
            error: Exception to assess
            context: Optional context information
            
        Returns:
            ErrorSeverity
        """
        category = self.categorize_error(error)
        
        # Fatal errors
        if isinstance(error, (SystemExit, KeyboardInterrupt)):
            return ErrorSeverity.FATAL
        
        if category == ErrorCategory.SECURITY:
            return ErrorSeverity.FATAL
        
        # Recoverable errors
        if category in [ErrorCategory.NETWORK, ErrorCategory.API]:
            return ErrorSeverity.RECOVERABLE
        
        # Configuration errors are usually fatal
        if category == ErrorCategory.CONFIGURATION:
            return ErrorSeverity.FATAL
        
        # Database errors can be recoverable
        if category == ErrorCategory.DATABASE:
            return ErrorSeverity.RECOVERABLE
        
        # Default to warning for unknown errors
        return ErrorSeverity.WARNING
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict] = None,
        severity: Optional[ErrorSeverity] = None
    ) -> Dict[str, Any]:
        """
        Handle an error with categorization and logging.
        
        Args:
            error: Exception that occurred
            context: Optional context information
            severity: Optional override for severity assessment
            
        Returns:
            Error handling result
        """
        # Categorize and assess
        category = self.categorize_error(error)
        if severity is None:
            severity = self.assess_severity(error, context)
        
        # Create error record
        error_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'category': category.value,
            'severity': severity.value,
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        # Log error
        self._log_error(error_record)
        
        # Update statistics
        self._update_statistics(error_record)
        
        # Store in history
        self.last_errors.append(error_record)
        if len(self.last_errors) > self.max_error_history:
            self.last_errors.pop(0)
        
        # Generate crash dump for fatal errors
        if severity == ErrorSeverity.FATAL:
            self._generate_crash_dump(error_record)
        
        # Notify handlers
        self._notify(error_record)
        
        return {
            'handled': True,
            'category': category.value,
            'severity': severity.value,
            'recoverable': severity != ErrorSeverity.FATAL
        }
    
    def retry_with_backoff(
        self,
        func: Callable,
        *args,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with automatic retry and exponential backoff.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            max_retries: Override max retries
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        last_error = None
        delay = self.retry_delay
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                if attempt < max_retries:
                    # Log retry attempt
                    if self.logger:
                        self.logger.warning(
                            f"Retry {attempt + 1}/{max_retries} after error: {e}"
                        )
                    
                    # Wait before retry
                    time.sleep(delay)
                    
                    # Exponential backoff
                    if self.exponential_backoff:
                        delay *= 2
        
        # All retries failed
        self.handle_error(
            last_error,
            context={
                'function': func.__name__,
                'attempts': max_retries + 1
            }
        )
        
        raise last_error
    
    def _log_error(self, error_record: Dict[str, Any]):
        """Log error record."""
        if self.logger:
            severity = error_record['severity']
            message = (
                f"{error_record['category'].upper()} ERROR: "
                f"{error_record['error_type']}: {error_record['error_message']}"
            )
            
            if severity == 'fatal':
                self.logger.critical(message, exc_info=True)
            elif severity == 'recoverable':
                self.logger.error(message, exc_info=True)
            else:
                self.logger.warning(message)
        else:
            # Fallback to print
            print(f"ERROR [{error_record['severity']}]: {error_record['error_message']}")
    
    def _update_statistics(self, error_record: Dict[str, Any]):
        """Update error statistics."""
        category = error_record['category']
        self.error_counts[category] = self.error_counts.get(category, 0) + 1
    
    def _generate_crash_dump(self, error_record: Dict[str, Any]):
        """Generate crash dump file for fatal errors."""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        dump_file = self.crash_dump_dir / f"crash_{timestamp}.json"
        
        try:
            import json
            with open(dump_file, 'w') as f:
                json.dump(error_record, f, indent=2)
            
            if self.logger:
                self.logger.info(f"Crash dump saved to {dump_file}")
        except Exception as e:
            print(f"Failed to generate crash dump: {e}")
    
    def _notify(self, error_record: Dict[str, Any]):
        """Send notifications through registered handlers."""
        for handler in self.notification_handlers:
            try:
                handler(error_record)
            except Exception as e:
                print(f"Notification handler failed: {e}")
    
    def add_notification_handler(self, handler: Callable):
        """
        Add a notification handler.
        
        Args:
            handler: Callable that receives error_record dict
        """
        self.notification_handlers.append(handler)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'total_errors': sum(self.error_counts.values()),
            'by_category': self.error_counts,
            'recent_errors': len(self.last_errors)
        }
    
    def get_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent errors.
        
        Args:
            count: Number of recent errors to return
            
        Returns:
            List of error records
        """
        return self.last_errors[-count:]
    
    def clear_error_history(self):
        """Clear error history and statistics."""
        self.error_counts = {}
        self.last_errors = []


def create_error_handler(
    logger=None,
    max_retries: int = 3,
    exponential_backoff: bool = True
) -> ErrorHandler:
    """
    Factory function to create error handler.
    
    Args:
        logger: Logger instance
        max_retries: Maximum retry attempts
        exponential_backoff: Use exponential backoff
        
    Returns:
        ErrorHandler instance
    """
    return ErrorHandler(
        logger=logger,
        max_retries=max_retries,
        exponential_backoff=exponential_backoff
    )
