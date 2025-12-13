"""
Integration Tests for Error Recovery
Tests error handling and recovery mechanisms
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.logging.logger import create_logger
from src.error_handler import create_error_handler, ErrorSeverity, ErrorCategory


class TestErrorRecovery(unittest.TestCase):
    """Test error handling and recovery."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = create_logger(name="TestErrorHandler", log_level="ERROR")
        self.error_handler = create_error_handler(logger=self.logger)
    
    def test_error_categorization(self):
        """Test error categorization."""
        # Network error
        network_error = ConnectionError("Connection failed")
        category = self.error_handler.categorize_error(network_error)
        self.assertEqual(category, ErrorCategory.NETWORK)
        
        # File error
        file_error = FileNotFoundError("File not found")
        category = self.error_handler.categorize_error(file_error)
        self.assertEqual(category, ErrorCategory.FILESYSTEM)
    
    def test_severity_assessment(self):
        """Test error severity assessment."""
        # Recoverable error
        network_error = ConnectionError("Timeout")
        severity = self.error_handler.assess_severity(network_error)
        self.assertEqual(severity, ErrorSeverity.RECOVERABLE)
        
        # Fatal error
        system_exit = SystemExit(1)
        severity = self.error_handler.assess_severity(system_exit)
        self.assertEqual(severity, ErrorSeverity.FATAL)
    
    def test_error_handling(self):
        """Test error handling flow."""
        error = ValueError("Test error")
        result = self.error_handler.handle_error(error, context={'test': True})
        
        self.assertTrue(result['handled'])
        self.assertIn('category', result)
        self.assertIn('severity', result)
    
    def test_retry_mechanism(self):
        """Test retry with backoff."""
        call_count = [0]
        
        def failing_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        # Should succeed on 3rd try
        result = self.error_handler.retry_with_backoff(
            failing_function,
            max_retries=3
        )
        
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 3)
    
    def test_error_statistics(self):
        """Test error statistics tracking."""
        # Generate some errors
        for i in range(5):
            error = ValueError(f"Error {i}")
            self.error_handler.handle_error(error)
        
        stats = self.error_handler.get_error_statistics()
        
        self.assertGreater(stats['total_errors'], 0)
        self.assertIn('by_category', stats)
    
    def test_recent_errors(self):
        """Test recent error retrieval."""
        # Generate errors
        for i in range(3):
            self.error_handler.handle_error(ValueError(f"Test {i}"))
        
        recent = self.error_handler.get_recent_errors(count=2)
        
        self.assertEqual(len(recent), 2)
        self.assertIn('timestamp', recent[0])


if __name__ == '__main__':
    unittest.main()
