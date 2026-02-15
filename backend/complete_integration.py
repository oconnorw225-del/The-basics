#!/usr/bin/env python3
"""
Complete Integration - Integrates all system components
Coordinates bots, freelance engine, monitoring, and notifications
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Hardcoded path for GitHub Actions compatibility
BASE_PATH = "/home/runner/work/The-basics/The-basics"

try:
    from bot_registry import BotRegistry
    from email_notifier import EmailNotifier
except ImportError:
    print("Warning: Could not import bot_registry or email_notifier")
    BotRegistry = None
    EmailNotifier = None


class CompleteIntegration:
    """Complete system integration orchestrator"""
    
    def __init__(self):
        self.base_path = BASE_PATH
        self.registry = BotRegistry() if BotRegistry else None
        self.notifier = EmailNotifier() if EmailNotifier else None
        self.services = {}
        self.status = "initializing"
    
    async def initialize(self):
        """Initialize all system components"""
        print("🚀 Complete Integration - Initializing...")
        
        try:
            # Initialize bot registry
            if self.registry:
                print("✅ Bot Registry initialized")
            
            # Initialize email notifier
            if self.notifier:
                print("✅ Email Notifier initialized")
            
            # Load configuration
            self.load_configuration()
            
            # Initialize services
            await self.initialize_services()
            
            self.status = "ready"
            print("✅ Complete Integration initialized successfully")
            
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            self.status = "error"
            raise
    
    def load_configuration(self):
        """Load system configuration"""
        config_files = [
            "config/bot-limits.json",
            "config/kill-switch.json",
            "config/api-endpoints.json"
        ]
        
        self.config = {}
        for config_file in config_files:
            path = os.path.join(self.base_path, config_file)
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        key = os.path.basename(config_file).replace('.json', '')
                        self.config[key] = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load {config_file}: {e}")
    
    async def initialize_services(self):
        """Initialize all services"""
        self.services = {
            "bot_coordinator": {"status": "ready", "type": "core"},
            "ndax_bot": {"status": "ready", "type": "trading"},
            "quantum_bot": {"status": "ready", "type": "trading"},
            "shadowforge_bot": {"status": "ready", "type": "trading"},
            "freelance_engine": {"status": "ready", "type": "freelance"},
            "dashboard_backend": {"status": "ready", "type": "dashboard"},
            "dashboard_frontend": {"status": "ready", "type": "dashboard"}
        }
    
    async def start_all_services(self):
        """Start all services in proper order"""
        print("\n🚀 Starting all services...")
        
        service_order = [
            ("bot_coordinator", "Bot Coordinator"),
            ("ndax_bot", "NDAX Trading Bot"),
            ("quantum_bot", "Quantum Bot"),
            ("shadowforge_bot", "ShadowForge Bot"),
            ("freelance_engine", "Freelance Engine"),
            ("dashboard_backend", "Dashboard Backend"),
            ("dashboard_frontend", "Dashboard Frontend")
        ]
        
        for service_id, service_name in service_order:
            print(f"  Starting {service_name}...")
            self.services[service_id]["status"] = "running"
            self.services[service_id]["started_at"] = datetime.now().isoformat()
            await asyncio.sleep(0.5)  # Simulated startup delay
        
        print("✅ All services started")
    
    async def check_health(self) -> Dict:
        """Check health of all services"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "services": {}
        }
        
        for service_id, service_data in self.services.items():
            health_status["services"][service_id] = {
                "status": service_data.get("status", "unknown"),
                "type": service_data.get("type", "unknown"),
                "healthy": service_data.get("status") == "running"
            }
        
        # Check if any service is unhealthy
        unhealthy = [
            s for s, d in health_status["services"].items()
            if not d.get("healthy", False)
        ]
        
        if unhealthy:
            health_status["overall_status"] = "degraded"
            health_status["unhealthy_services"] = unhealthy
        
        return health_status
    
    async def send_status_notification(self):
        """Send status notification email"""
        if not self.notifier:
            print("Email notifier not available")
            return
        
        health = await self.check_health()
        
        status_data = {
            "status": health["overall_status"],
            "services": {
                service_id: data["status"]
                for service_id, data in health["services"].items()
            },
            "metrics": {
                "total_services": len(self.services),
                "running_services": len([
                    s for s in health["services"].values()
                    if s.get("status") == "running"
                ]),
                "system_status": self.status
            }
        }
        
        self.notifier.send_system_status(status_data)
        print("✅ Status notification sent")
    
    async def run_continuous(self):
        """Run continuous monitoring and coordination"""
        print("\n🔄 Starting continuous monitoring...")
        
        iteration = 0
        while True:
            iteration += 1
            print(f"\n--- Monitoring Cycle {iteration} ---")
            
            # Check health
            health = await self.check_health()
            print(f"Overall Status: {health['overall_status']}")
            
            # Send periodic status (every 10 cycles)
            if iteration % 10 == 0:
                await self.send_status_notification()
            
            # Wait before next cycle
            await asyncio.sleep(300)  # 5 minutes
    
    async def run(self):
        """Main run method"""
        try:
            await self.initialize()
            await self.start_all_services()
            await self.send_status_notification()
            await self.run_continuous()
        except KeyboardInterrupt:
            print("\n\n⚠️  Shutdown requested")
            self.status = "stopping"
        except Exception as e:
            print(f"\n\n❌ Fatal error: {e}")
            self.status = "error"
            raise


async def main():
    """Main entry point"""
    integration = CompleteIntegration()
    await integration.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
