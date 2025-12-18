"""
Integration Tests for Health Monitoring
Tests health check and monitoring functionality
"""

import unittest
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.logging.logger import create_logger
from src.health_monitor import create_health_monitor, HealthStatus, ProcessState


class TestHealthMonitoring(unittest.TestCase):
    """Test health monitoring functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = create_logger(name="TestHealthMonitor", log_level="ERROR")
        self.monitor = create_health_monitor(logger=self.logger, check_interval=1)
    
    def test_process_registration(self):
        """Test process registration."""
        self.monitor.register_process(
            name="test_process",
            port=8000,
            health_endpoint="http://localhost:8000/health"
        )
        
        self.assertIn("test_process", self.monitor.processes)
    
    def test_heartbeat(self):
        """Test heartbeat mechanism."""
        self.monitor.register_process("test_process")
        
        # Send heartbeat
        self.monitor.heartbeat("test_process")
        
        process = self.monitor.processes["test_process"]
        self.assertIsNotNone(process['last_heartbeat'])
    
    def test_system_resource_check(self):
        """Test system resource checking."""
        resources = self.monitor.check_system_resources()
        
        self.assertIn('status', resources)
        self.assertIn('cpu_percent', resources)
        self.assertIn('memory_percent', resources)
        self.assertIn('disk_percent', resources)
    
    def test_health_check(self):
        """Test full health check."""
        self.monitor.register_process("test_process")
        self.monitor.heartbeat("test_process")
        
        health = self.monitor.perform_full_health_check()
        
        self.assertIn('overall_status', health)
        self.assertIn('processes', health)
        self.assertIn('resources', health)
    
    def test_process_uptime(self):
        """Test process uptime calculation."""
        self.monitor.register_process("test_process")
        
        # Wait a bit
        time.sleep(0.1)
        
        uptime = self.monitor.get_process_uptime("test_process")
        self.assertIsNotNone(uptime)
        self.assertGreater(uptime, 0)


if __name__ == '__main__':
    unittest.main()
