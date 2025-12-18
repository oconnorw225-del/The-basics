"""
Integration Tests for System Startup
Tests that all components initialize and start correctly
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.logging.logger import create_logger
from src.config.manager import create_config_manager
from src.error_handler import create_error_handler
from src.health_monitor import create_health_monitor
from src.process_manager import create_process_manager
from src.recovery.crash_handler import create_crash_handler
from src.recovery.freeze_detector import create_freeze_detector
from src.ai.manager import create_ai_manager
from src.api.gateway import create_api_gateway
from src.orchestrator import create_service_orchestrator


class TestSystemStartup(unittest.TestCase):
    """Test system startup and initialization."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Silence logs during tests
        os.environ['LOG_LEVEL'] = 'ERROR'
    
    def test_logger_creation(self):
        """Test logger initialization."""
        logger = create_logger(name="TestLogger")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "TestLogger")
    
    def test_config_manager_creation(self):
        """Test configuration manager initialization."""
        config = create_config_manager()
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.environment)
    
    def test_error_handler_creation(self):
        """Test error handler initialization."""
        logger = create_logger()
        error_handler = create_error_handler(logger=logger)
        self.assertIsNotNone(error_handler)
        self.assertEqual(error_handler.max_retries, 3)
    
    def test_health_monitor_creation(self):
        """Test health monitor initialization."""
        logger = create_logger()
        monitor = create_health_monitor(logger=logger)
        self.assertIsNotNone(monitor)
        self.assertFalse(monitor.running)
    
    def test_process_manager_creation(self):
        """Test process manager initialization."""
        logger = create_logger()
        pm = create_process_manager(logger=logger)
        self.assertIsNotNone(pm)
        self.assertEqual(len(pm.processes), 0)
    
    def test_crash_handler_creation(self):
        """Test crash handler initialization."""
        logger = create_logger()
        pm = create_process_manager(logger=logger)
        crash_handler = create_crash_handler(logger=logger, process_manager=pm)
        self.assertIsNotNone(crash_handler)
    
    def test_freeze_detector_creation(self):
        """Test freeze detector initialization."""
        logger = create_logger()
        pm = create_process_manager(logger=logger)
        crash_handler = create_crash_handler(logger=logger, process_manager=pm)
        detector = create_freeze_detector(
            logger=logger,
            process_manager=pm,
            crash_handler=crash_handler
        )
        self.assertIsNotNone(detector)
        self.assertFalse(detector.running)
    
    def test_ai_manager_creation(self):
        """Test AI manager initialization."""
        logger = create_logger()
        error_handler = create_error_handler(logger=logger)
        ai_manager = create_ai_manager(logger=logger, error_handler=error_handler)
        self.assertIsNotNone(ai_manager)
        self.assertEqual(ai_manager.max_concurrent_tasks, 5)
    
    def test_api_gateway_creation(self):
        """Test API gateway initialization."""
        logger = create_logger()
        gateway = create_api_gateway(logger=logger)
        self.assertIsNotNone(gateway)
        self.assertEqual(len(gateway.routes), 0)
    
    def test_service_orchestrator_creation(self):
        """Test service orchestrator initialization."""
        logger = create_logger()
        pm = create_process_manager(logger=logger)
        orchestrator = create_service_orchestrator(logger=logger, process_manager=pm)
        self.assertIsNotNone(orchestrator)
        self.assertEqual(len(orchestrator.services), 0)
    
    def test_component_integration(self):
        """Test that all components can be created together."""
        # Create all components
        logger = create_logger(name="IntegrationTest")
        config = create_config_manager()
        error_handler = create_error_handler(logger=logger)
        health_monitor = create_health_monitor(logger=logger)
        pm = create_process_manager(logger=logger, config_manager=config)
        crash_handler = create_crash_handler(logger=logger, process_manager=pm)
        freeze_detector = create_freeze_detector(
            logger=logger,
            process_manager=pm,
            crash_handler=crash_handler
        )
        ai_manager = create_ai_manager(logger=logger, error_handler=error_handler)
        gateway = create_api_gateway(logger=logger)
        orchestrator = create_service_orchestrator(logger=logger, process_manager=pm)
        
        # Verify all created
        self.assertIsNotNone(logger)
        self.assertIsNotNone(config)
        self.assertIsNotNone(error_handler)
        self.assertIsNotNone(health_monitor)
        self.assertIsNotNone(pm)
        self.assertIsNotNone(crash_handler)
        self.assertIsNotNone(freeze_detector)
        self.assertIsNotNone(ai_manager)
        self.assertIsNotNone(gateway)
        self.assertIsNotNone(orchestrator)
        
        logger.info("All components integrated successfully")


if __name__ == '__main__':
    unittest.main()
