#!/usr/bin/env python3
"""
Unified System Startup Script
Starts all components in correct order with health checks
"""

import os
import sys
import time
import signal
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.logging.logger import create_logger
from src.config.manager import create_config_manager
from src.error_handler import create_error_handler
from src.health_monitor import create_health_monitor
from src.process_manager import create_process_manager
from src.recovery.crash_handler import create_crash_handler
from src.recovery.freeze_detector import create_freeze_detector
from src.ai.manager import create_ai_manager
from src.api.gateway import create_api_gateway


class SystemOrchestrator:
    """
    Main system orchestrator.
    Coordinates startup, monitoring, and shutdown of all components.
    """
    
    def __init__(self):
        """Initialize system orchestrator."""
        self.logger = None
        self.config = None
        self.error_handler = None
        self.health_monitor = None
        self.process_manager = None
        self.crash_handler = None
        self.freeze_detector = None
        self.ai_manager = None
        self.api_gateway = None
        
        self.running = False
        self.startup_complete = False
    
    def initialize_core_systems(self):
        """Initialize core system components."""
        print("🔧 Initializing core systems...")
        
        # 1. Logger (first - needed by all other components)
        print("  📝 Starting unified logger...")
        self.logger = create_logger(
            name="UnifiedSystem",
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
        self.logger.info("Unified logger initialized")
        
        # 2. Configuration manager
        print("  ⚙️  Loading configuration...")
        self.config = create_config_manager()
        self.logger.info(f"Configuration loaded (env: {self.config.environment.value})")
        
        # Check for port conflicts
        conflicts = self.config.check_port_conflicts()
        if conflicts:
            self.logger.warning(f"Port conflicts detected: {conflicts}")
            print(f"  ⚠️  Port conflicts: {conflicts}")
        
        # 3. Error handler
        print("  🛡️  Initializing error handler...")
        self.error_handler = create_error_handler(
            logger=self.logger,
            max_retries=3
        )
        self.logger.info("Error handler initialized")
        
        # 4. Health monitor
        print("  💚 Starting health monitor...")
        self.health_monitor = create_health_monitor(
            logger=self.logger,
            check_interval=int(os.getenv('HEALTH_CHECK_INTERVAL', 60)),
            auto_start=False  # Start later
        )
        self.logger.info("Health monitor initialized")
        
        # 5. Process manager
        print("  🔄 Starting process manager...")
        self.process_manager = create_process_manager(
            logger=self.logger,
            config_manager=self.config
        )
        self.logger.info("Process manager initialized")
        
        # 6. Crash handler
        print("  🚨 Initializing crash handler...")
        self.crash_handler = create_crash_handler(
            logger=self.logger,
            process_manager=self.process_manager
        )
        self.logger.info("Crash handler initialized")
        
        # 7. Freeze detector
        print("  ❄️  Initializing freeze detector...")
        self.freeze_detector = create_freeze_detector(
            logger=self.logger,
            process_manager=self.process_manager,
            crash_handler=self.crash_handler,
            auto_start=False  # Start later
        )
        self.logger.info("Freeze detector initialized")
        
        # 8. AI manager
        print("  🤖 Initializing AI manager...")
        self.ai_manager = create_ai_manager(
            logger=self.logger,
            error_handler=self.error_handler
        )
        self.logger.info("AI manager initialized")
        
        # 9. API gateway
        print("  🌐 Initializing API gateway...")
        self.api_gateway = create_api_gateway(
            logger=self.logger,
            rate_limit=int(os.getenv('API_RATE_LIMIT', 100))
        )
        self.logger.info("API gateway initialized")
        
        print("✅ Core systems initialized\n")
    
    def validate_environment(self):
        """Validate environment and configuration."""
        print("🔍 Validating environment...")
        
        # Check required configuration
        required_keys = []
        validation = self.config.validate_required(required_keys)
        
        if not validation['valid']:
            self.logger.warning(
                f"Missing optional configuration: {validation['missing']}"
            )
            print(f"  ⚠️  Missing optional config: {validation['missing']}")
        
        # Check Python version
        import sys
        if sys.version_info < (3, 8):
            self.logger.error("Python 3.8+ required")
            return False
        
        print(f"  ✓ Python version: {sys.version_info.major}.{sys.version_info.minor}")
        print(f"  ✓ Environment: {self.config.environment.value}")
        print("✅ Environment validated\n")
        return True
    
    def start_backend_services(self):
        """Start Python backend services."""
        print("🐍 Starting Python backend services...")
        
        # Get backend service config
        backend_config = self.config.get_service_config('python_backend')
        
        if backend_config and backend_config.enabled and backend_config.auto_start:
            # Register and start backend server
            self.process_manager.register_process(
                name='python_backend',
                command=['python3', 'backend/server.py'],
                auto_restart=True,
                max_restarts=3
            )
            
            # Register for crash recovery
            self.crash_handler.register_process('python_backend')
            
            # Register watchdog
            self.freeze_detector.register_watchdog('python_backend', timeout=300)
            
            # Start the process
            if self.process_manager.start_process('python_backend'):
                print(f"  ✓ Python backend started on port {backend_config.port}")
                self.logger.info(f"Python backend started on port {backend_config.port}")
            else:
                print("  ✗ Failed to start Python backend")
                self.logger.error("Failed to start Python backend")
        else:
            print("  ⏸️  Python backend disabled or auto_start=false")
        
        print()
    
    def start_node_services(self):
        """Start Node.js services."""
        print("🟢 Starting Node.js services...")
        
        # Start Node server
        server_config = self.config.get_service_config('node_server')
        if server_config and server_config.enabled and server_config.auto_start:
            self.process_manager.register_process(
                name='node_server',
                command=['node', 'server.js'],
                auto_restart=True
            )
            
            self.crash_handler.register_process('node_server')
            self.freeze_detector.register_watchdog('node_server', timeout=300)
            
            if self.process_manager.start_process('node_server'):
                print(f"  ✓ Node server started on port {server_config.port}")
                self.logger.info(f"Node server started on port {server_config.port}")
            else:
                print("  ✗ Failed to start Node server")
        else:
            print("  ⏸️  Node server disabled")
        
        # Start bot
        bot_config = self.config.get_service_config('bot')
        if bot_config and bot_config.enabled and bot_config.auto_start:
            self.process_manager.register_process(
                name='bot',
                command=['node', 'bot.js'],
                env={**os.environ, **bot_config.env_vars},
                auto_restart=True
            )
            
            self.crash_handler.register_process('bot')
            self.freeze_detector.register_watchdog('bot', timeout=300)
            
            if self.process_manager.start_process('bot'):
                print(f"  ✓ Bot started on port {bot_config.port}")
                self.logger.info(f"Bot started on port {bot_config.port}")
            else:
                print("  ✗ Failed to start bot")
        else:
            print("  ⏸️  Bot disabled")
        
        print()
    
    def start_monitoring_services(self):
        """Start monitoring and recovery services."""
        print("📊 Starting monitoring services...")
        
        # Start health monitor
        self.health_monitor.start_monitoring()
        print("  ✓ Health monitor started")
        
        # Start freeze detector
        self.freeze_detector.start_monitoring()
        print("  ✓ Freeze detector started")
        
        print()
    
    def run_health_checks(self):
        """Run initial health checks."""
        print("🏥 Running health checks...")
        
        # Wait a moment for services to start
        time.sleep(3)
        
        # Perform health check
        health = self.health_monitor.perform_full_health_check()
        
        print(f"  Overall status: {health['overall_status']}")
        
        if health.get('unhealthy_processes'):
            print(f"  ⚠️  Unhealthy processes: {health['unhealthy_processes']}")
        
        # Check system resources
        resources = health.get('resources', {})
        print(f"  CPU: {resources.get('cpu_percent', 0):.1f}%")
        print(f"  Memory: {resources.get('memory_percent', 0):.1f}%")
        print(f"  Disk: {resources.get('disk_percent', 0):.1f}%")
        
        print()
    
    def report_system_ready(self):
        """Report that system is ready."""
        self.startup_complete = True
        
        print("\n" + "="*60)
        print("🚀 SYSTEM READY")
        print("="*60)
        
        # Get all service ports
        ports = self.config.get_all_ports()
        
        print("\n📡 Service Endpoints:")
        for service, port in ports.items():
            if port > 0:
                print(f"  • {service}: http://localhost:{port}")
        
        print("\n📊 System Status:")
        process_info = self.process_manager.get_all_process_info()
        for name, info in process_info.items():
            if info:
                status_icon = "✓" if info['status'] == 'running' else "✗"
                print(f"  {status_icon} {name}: {info['status']} (PID: {info['pid']})")
        
        print("\n💡 Monitoring:")
        print(f"  • Health checks: Every {self.health_monitor.check_interval}s")
        print(f"  • Freeze detection: Active")
        print(f"  • Auto-recovery: Enabled")
        
        print("\n⌨️  Commands:")
        print("  • Ctrl+C or SIGTERM: Graceful shutdown")
        print("  • View logs: .unified-system/logs/")
        
        print("\n" + "="*60 + "\n")
        
        self.logger.info("System startup complete - all services operational")
    
    def start(self):
        """Start the entire system."""
        try:
            print("\n" + "="*60)
            print("🔷 THE-BASICS UNIFIED SYSTEM")
            print("="*60 + "\n")
            
            # 1. Initialize core systems
            self.initialize_core_systems()
            
            # 2. Validate environment
            if not self.validate_environment():
                print("❌ Environment validation failed")
                return False
            
            # 3. Start services in order
            self.start_backend_services()
            self.start_node_services()
            
            # 4. Start monitoring
            self.start_monitoring_services()
            
            # 5. Run health checks
            self.run_health_checks()
            
            # 6. Report ready
            self.report_system_ready()
            
            self.running = True
            return True
            
        except KeyboardInterrupt:
            print("\n⚠️  Startup interrupted")
            self.logger.warning("Startup interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Startup failed: {e}")
            self.logger.error(f"Startup failed: {e}", exc_info=True)
            return False
    
    def shutdown(self):
        """Shutdown the entire system gracefully."""
        if not self.running:
            return
        
        print("\n🛑 Shutting down system...")
        self.logger.info("Initiating graceful shutdown")
        
        # Stop monitoring
        if self.freeze_detector:
            print("  Stopping freeze detector...")
            self.freeze_detector.stop_monitoring()
        
        if self.health_monitor:
            print("  Stopping health monitor...")
            self.health_monitor.stop_monitoring()
        
        # Shutdown all processes
        if self.process_manager:
            print("  Stopping all processes...")
            self.process_manager.shutdown_all(timeout=30)
        
        # Final log
        if self.logger:
            self.logger.info("System shutdown complete")
        
        print("✅ Shutdown complete\n")
        self.running = False
    
    def run_forever(self):
        """Keep system running until interrupted."""
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⚠️  Interrupt received")
            self.logger.info("Interrupt signal received")


def main():
    """Main entry point."""
    orchestrator = SystemOrchestrator()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        orchestrator.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start system
    if orchestrator.start():
        # Run forever (until signal)
        orchestrator.run_forever()
        
        # Graceful shutdown
        orchestrator.shutdown()
        sys.exit(0)
    else:
        print("❌ Failed to start system")
        sys.exit(1)


if __name__ == "__main__":
    main()
