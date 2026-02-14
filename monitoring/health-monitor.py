#!/usr/bin/env python3
"""
Health Monitor Service
Provides health check endpoints and monitoring for bot coordinator
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

import aiohttp
from aiohttp import web

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HealthMonitor')


class HealthMonitor:
    """Health monitoring service for bot coordinator"""
    
    def __init__(self, config_dir: str = "config", port: int = 8080):
        self.config_dir = Path(config_dir)
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.health_data = {
            "status": "healthy",
            "checks": {},
            "last_update": None
        }
        
    def setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/health', self.health_endpoint)
        self.app.router.add_get('/metrics', self.metrics_endpoint)
        self.app.router.add_get('/logs', self.logs_endpoint)
        self.app.router.add_get('/alerts', self.alerts_endpoint)
        self.app.router.add_get('/', self.dashboard_endpoint)
        
    async def health_endpoint(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "health-monitor"
        })
        
    async def metrics_endpoint(self, request):
        """Metrics endpoint"""
        try:
            # Load bot limits for reference
            with open(self.config_dir / "bot-limits.json") as f:
                limits = json.load(f)
                
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "bots": {
                    "ndax": {"status": "stopped", "health": 0},
                    "quantum": {"status": "stopped", "health": 0},
                    "shadowforge": {"status": "stopped", "health": 0}
                },
                "limits": limits.get("global_limits", {}),
                "system": {
                    "uptime": 0,
                    "memory_usage": 0,
                    "cpu_usage": 0
                }
            }
            
            return web.json_response(metrics)
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return web.json_response({"error": str(e)}, status=500)
            
    async def logs_endpoint(self, request):
        """Logs endpoint"""
        try:
            logs_dir = Path("logs")
            recent_logs = []
            
            if logs_dir.exists():
                for log_file in logs_dir.glob("*.log"):
                    try:
                        with open(log_file) as f:
                            lines = f.readlines()[-50:]  # Last 50 lines
                            recent_logs.extend([
                                {"file": log_file.name, "line": line.strip()}
                                for line in lines
                            ])
                    except Exception as e:
                        logger.error(f"Error reading {log_file}: {e}")
                        
            return web.json_response({
                "timestamp": datetime.now().isoformat(),
                "logs": recent_logs[-100:]  # Return last 100 log entries
            })
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return web.json_response({"error": str(e)}, status=500)
            
    async def alerts_endpoint(self, request):
        """Alerts endpoint"""
        try:
            # Check for active kill switch
            with open(self.config_dir / "kill-switch.json") as f:
                kill_switch = json.load(f)
                
            alerts = []
            
            if kill_switch.get("enabled", False):
                for condition_name, condition in kill_switch.get("conditions", {}).items():
                    if condition.get("enabled", False):
                        alerts.append({
                            "type": "info",
                            "message": f"Kill switch condition active: {condition_name}",
                            "action": condition.get("action", "unknown")
                        })
                        
            return web.json_response({
                "timestamp": datetime.now().isoformat(),
                "alerts": alerts
            })
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return web.json_response({"error": str(e)}, status=500)
            
    async def dashboard_endpoint(self, request):
        """Serve the dashboard HTML"""
        try:
            dashboard_path = Path("monitoring/status-dashboard.html")
            if dashboard_path.exists():
                return web.FileResponse(dashboard_path)
            else:
                return web.Response(text="Dashboard not found", status=404)
        except Exception as e:
            logger.error(f"Error serving dashboard: {e}")
            return web.Response(text=str(e), status=500)
            
    async def run(self):
        """Run the health monitor service"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        logger.info(f"🏥 Health Monitor running on http://localhost:{self.port}")
        logger.info(f"📊 Dashboard: http://localhost:{self.port}/")
        logger.info(f"💚 Health: http://localhost:{self.port}/health")
        logger.info(f"📈 Metrics: http://localhost:{self.port}/metrics")
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Shutting down health monitor...")
        finally:
            await runner.cleanup()


async def main():
    """Main entry point"""
    monitor = HealthMonitor()
    await monitor.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Health monitor stopped by user")
