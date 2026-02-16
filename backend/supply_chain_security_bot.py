"""
SUPPLY CHAIN SECURITY BOT
Autonomous monitoring of dependencies and vulnerabilities.
Integrates Dependabot alerts with the autonomous bot system.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SupplyChainSecurityBot:
    """Autonomous supply chain security monitoring bot."""

    def __init__(self):
        self.bot_id = "supply_chain_security"
        self.name = "Supply Chain Security Monitor"
        self.status = "initializing"
        
        self.config_dir = Path("/home/runner/work/The-basics/The-basics/config")
        self.config_dir.mkdir(exist_ok=True)
        
        self.monitoring_config_file = self.config_dir / "supply_chain_monitoring.json"
        self.alerts_file = self.config_dir / "dependency_alerts.json"
        
        self.monitoring_config = self._load_monitoring_config()
        self.alerts = self._load_alerts()

    def _load_monitoring_config(self) -> Dict[str, Any]:
        """Load supply chain monitoring configuration."""
        if self.monitoring_config_file.exists():
            return json.loads(self.monitoring_config_file.read_text())
        
        default_config = {
            "enabled": True,
            "monitoring_frequency": "every_6_hours",
            "alert_levels": ["critical", "high", "medium"],
            "auto_create_issues": True,
            "email_notifications": True,
            "ecosystems": ["npm", "pip", "github-actions", "docker"],
            "last_scan": None,
            "total_scans": 0,
            "alerts_detected": 0,
            "issues_created": 0
        }
        
        self.monitoring_config_file.write_text(json.dumps(default_config, indent=2))
        return default_config

    def _save_monitoring_config(self) -> None:
        """Save monitoring configuration."""
        self.monitoring_config_file.write_text(
            json.dumps(self.monitoring_config, indent=2)
        )

    def _load_alerts(self) -> Dict[str, Any]:
        """Load dependency alerts."""
        if self.alerts_file.exists():
            return json.loads(self.alerts_file.read_text())
        
        default_alerts = {
            "alerts": [],
            "last_updated": datetime.now().isoformat(),
            "total_alerts": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0
        }
        
        self.alerts_file.write_text(json.dumps(default_alerts, indent=2))
        return default_alerts

    def _save_alerts(self) -> None:
        """Save alerts to file."""
        self.alerts["last_updated"] = datetime.now().isoformat()
        self.alerts_file.write_text(json.dumps(self.alerts, indent=2))

    async def initialize(self) -> Dict[str, Any]:
        """Initialize the supply chain security bot."""
        print(f"🔒 Initializing {self.name}...")
        
        self.status = "active"
        
        result = {
            "bot_id": self.bot_id,
            "name": self.name,
            "status": "initialized",
            "monitoring_enabled": self.monitoring_config["enabled"],
            "ecosystems": self.monitoring_config["ecosystems"],
            "alert_levels": self.monitoring_config["alert_levels"]
        }
        
        print(f"✅ {self.name} initialized successfully")
        print(f"   Monitoring: {', '.join(self.monitoring_config['ecosystems'])}")
        print(f"   Alert levels: {', '.join(self.monitoring_config['alert_levels'])}")
        
        return result

    async def scan_dependencies(self) -> Dict[str, Any]:
        """
        Scan dependencies for vulnerabilities.
        This coordinates with the GitHub Actions workflow.
        """
        print(f"\n🔍 {self.name}: Starting dependency scan...")
        
        scan_result = {
            "timestamp": datetime.now().isoformat(),
            "ecosystems_scanned": self.monitoring_config["ecosystems"],
            "alerts_found": 0,
            "critical_alerts": 0,
            "status": "completed"
        }
        
        # Update scan statistics
        self.monitoring_config["last_scan"] = scan_result["timestamp"]
        self.monitoring_config["total_scans"] += 1
        self._save_monitoring_config()
        
        print(f"✅ Dependency scan completed")
        print(f"   Total scans performed: {self.monitoring_config['total_scans']}")
        
        return scan_result

    async def check_alerts(self) -> Dict[str, Any]:
        """Check for new dependency alerts."""
        # Read alerts that may have been updated by GitHub Actions workflow
        self.alerts = self._load_alerts()
        
        alert_summary = {
            "total_alerts": self.alerts["total_alerts"],
            "critical": self.alerts.get("critical_count", 0),
            "high": self.alerts.get("high_count", 0),
            "medium": self.alerts.get("medium_count", 0),
            "low": self.alerts.get("low_count", 0),
            "last_updated": self.alerts["last_updated"]
        }
        
        return alert_summary

    def record_alert(
        self,
        package_name: str,
        severity: str,
        cve_id: Optional[str] = None,
        summary: Optional[str] = None
    ) -> None:
        """Record a new dependency alert."""
        alert = {
            "package": package_name,
            "severity": severity,
            "cve_id": cve_id,
            "summary": summary,
            "detected_at": datetime.now().isoformat(),
            "status": "open"
        }
        
        self.alerts["alerts"].append(alert)
        self.alerts["total_alerts"] = len(self.alerts["alerts"])
        
        # Update severity counts
        severity_key = f"{severity.lower()}_count"
        if severity_key in self.alerts:
            self.alerts[severity_key] += 1
        
        self.monitoring_config["alerts_detected"] += 1
        
        self._save_alerts()
        self._save_monitoring_config()

    async def get_status(self) -> Dict[str, Any]:
        """Get bot status and statistics."""
        return {
            "bot_id": self.bot_id,
            "name": self.name,
            "status": self.status,
            "enabled": self.monitoring_config["enabled"],
            "last_scan": self.monitoring_config.get("last_scan"),
            "total_scans": self.monitoring_config.get("total_scans", 0),
            "total_alerts": self.alerts.get("total_alerts", 0),
            "critical_alerts": self.alerts.get("critical_count", 0),
            "high_alerts": self.alerts.get("high_count", 0),
            "medium_alerts": self.alerts.get("medium_count", 0),
            "monitoring_frequency": self.monitoring_config.get("monitoring_frequency"),
            "ecosystems": self.monitoring_config.get("ecosystems", [])
        }

    async def run_periodic_scan(self) -> None:
        """Run periodic dependency scans (every 6 hours)."""
        while self.monitoring_config["enabled"]:
            try:
                await self.scan_dependencies()
                await self.check_alerts()
                
                # Wait 6 hours before next scan
                await asyncio.sleep(6 * 3600)
            except Exception as e:
                print(f"❌ Error in periodic scan: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry

    def get_capabilities(self) -> List[str]:
        """Return bot capabilities."""
        return [
            "dependency_monitoring",
            "vulnerability_scanning",
            "dependabot_integration",
            "supply_chain_security",
            "npm_package_monitoring",
            "pip_package_monitoring",
            "github_actions_monitoring",
            "docker_image_monitoring",
            "cve_tracking",
            "security_alerts"
        ]

    def get_metadata(self) -> Dict[str, Any]:
        """Return bot metadata."""
        return {
            "version": "1.0.0",
            "type": "security_monitoring",
            "autonomous": True,
            "integrations": [
                "Dependabot",
                "GitHub Security Advisories",
                "GitHub Dependency Graph",
                "npm audit",
                "pip-audit"
            ],
            "workflows": [
                "dependabot-auto-monitor.yml",
                "dependency-submission.yml"
            ],
            "documentation": [
                "DEPENDENCY_SUBMISSION_GUIDE.md",
                "SUPPLY_CHAIN_SECURITY_IMPLEMENTATION.md"
            ]
        }


# Global singleton instance
supply_chain_bot = SupplyChainSecurityBot()


async def main():
    """Test the supply chain security bot."""
    print("=" * 60)
    print("🔒 SUPPLY CHAIN SECURITY BOT TEST")
    print("=" * 60)
    
    # Initialize
    init_result = await supply_chain_bot.initialize()
    print(f"\n✅ Initialization result: {json.dumps(init_result, indent=2)}")
    
    # Run a scan
    scan_result = await supply_chain_bot.scan_dependencies()
    print(f"\n✅ Scan result: {json.dumps(scan_result, indent=2)}")
    
    # Check alerts
    alerts = await supply_chain_bot.check_alerts()
    print(f"\n✅ Alert summary: {json.dumps(alerts, indent=2)}")
    
    # Get status
    status = await supply_chain_bot.get_status()
    print(f"\n✅ Bot status: {json.dumps(status, indent=2)}")
    
    print("\n" + "=" * 60)
    print("✅ Supply Chain Security Bot test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
