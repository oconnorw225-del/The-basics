#!/usr/bin/env python3
"""
Bot Coordinator - Central coordination system for NDAX, Quantum, and ShadowForge bots
Provides health monitoring, sequential activation, safety oversight, and error recovery
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot-coordinator.log"),
        logging.StreamHandler()],
)
logger = logging.getLogger("BotCoordinator")


class BotStatus(Enum):
    """Bot status states"""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    RECOVERY = "recovery"


class BotCoordinator:
    """Central coordinator for managing multiple trading bots"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.bots = {
            "ndax": {"status": BotStatus.STOPPED, "health": 0, "errors": []},
            "quantum": {"status": BotStatus.STOPPED, "health": 0, "errors": []},
            "shadowforge": {"status": BotStatus.STOPPED, "health": 0, "errors": []},
        }
        self.kill_switch_active = False
        self.session: Optional[aiohttp.ClientSession] = None

        # Load configuration
        self.load_config()

        # Initialize metrics
        self.metrics = {
            "total_trades": 0,
            "total_profit_loss": 0.0,
            "bots_started": 0,
            "errors_handled": 0,
            "kill_switches_triggered": 0,
            "recoveries_attempted": 0,
            "recoveries_succeeded": 0,
        }

    def load_config(self):
        """Load all configuration files"""
        try:
            with open(self.config_dir / "bot-limits.json") as f:
                self.limits = json.load(f)
            with open(self.config_dir / "kill-switch.json") as f:
                self.kill_switch_config = json.load(f)
            with open(self.config_dir / "recovery-settings.json") as f:
                self.recovery_settings = json.load(f)
            with open(self.config_dir / "api-endpoints.json") as f:
                self.endpoints = json.load(f)
            with open(self.config_dir / "notification-config.json") as f:
                self.notification_config = json.load(f)

            logger.info("✅ Configuration loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            raise

    async def initialize(self):
        """Initialize coordinator and create HTTP session"""
        self.session = aiohttp.ClientSession()
        logger.info("🚀 Bot Coordinator initialized")

    async def shutdown(self):
        """Cleanup coordinator resources"""
        if self.session:
            await self.session.close()
        logger.info("🛑 Bot Coordinator shutdown complete")

    async def check_bot_health(self, bot_name: str) -> bool:
        """Check health of a specific bot"""
        try:
            bot_config = self.endpoints.get(f"{bot_name}_bot")
            if not bot_config:
                logger.warning(f"⚠️  No endpoint config for {bot_name}")
                return False

            url = f"{bot_config['base_url']}{bot_config['health_endpoint']}"
            timeout = aiohttp.ClientTimeout(total=5)

            async with self.session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    self.bots[bot_name]["health"] = 100
                    return True
                else:
                    self.bots[bot_name]["health"] = max(
                        0, self.bots[bot_name]["health"] - 10)
                    return False
        except Exception as e:
            logger.error(f"❌ Health check failed for {bot_name}: {e}")
            self.bots[bot_name]["health"] = max(
                0, self.bots[bot_name]["health"] - 20)
            self.bots[bot_name]["errors"].append(str(e))
            return False

    async def start_bot(self, bot_name: str) -> bool:
        """Start a specific bot with dependency checks"""
        logger.info(f"🚀 Starting {bot_name} bot...")

        # Check if kill switch is active
        if self.kill_switch_active:
            logger.warning(
                f"⚠️  Cannot start {bot_name}: Kill switch is active")
            return False

        # Check dependencies (would be implemented based on bot requirements)
        if not await self.check_dependencies(bot_name):
            logger.error(f"❌ Dependencies not met for {bot_name}")
            return False

        # Update status
        self.bots[bot_name]["status"] = BotStatus.STARTING

        try:
            bot_config = self.endpoints.get(f"{bot_name}_bot")
            if not bot_config:
                raise ValueError(f"No configuration for {bot_name}")

            url = f"{bot_config['base_url']}{bot_config['control_endpoint']}"

            async with self.session.post(url, json={"action": "start"}) as response:
                if response.status == 200:
                    self.bots[bot_name]["status"] = BotStatus.RUNNING
                    self.metrics["bots_started"] += 1
                    logger.info(f"✅ {bot_name} bot started successfully")
                    await self.send_notification("system_startup", {"bot_name": bot_name})
                    return True
                else:
                    raise Exception(f"Failed to start: HTTP {response.status}")

        except Exception as e:
            logger.error(f"❌ Failed to start {bot_name}: {e}")
            self.bots[bot_name]["status"] = BotStatus.ERROR
            self.bots[bot_name]["errors"].append(str(e))
            await self.send_notification("bot_stopped", {"bot_name": bot_name, "reason": str(e)})
            return False

    async def stop_bot(
            self,
            bot_name: str,
            reason: str = "Manual stop") -> bool:
        """Stop a specific bot safely"""
        logger.info(f"🛑 Stopping {bot_name} bot: {reason}")

        try:
            bot_config = self.endpoints.get(f"{bot_name}_bot")
            if not bot_config:
                raise ValueError(f"No configuration for {bot_name}")

            url = f"{bot_config['base_url']}{bot_config['control_endpoint']}"

            async with self.session.post(url, json={"action": "stop"}) as response:
                if response.status == 200:
                    self.bots[bot_name]["status"] = BotStatus.STOPPED
                    logger.info(f"✅ {bot_name} bot stopped successfully")
                    await self.send_notification(
                        "bot_stopped", {"bot_name": bot_name, "reason": reason}
                    )
                    return True
                else:
                    raise Exception(f"Failed to stop: HTTP {response.status}")

        except Exception as e:
            logger.error(f"❌ Failed to stop {bot_name}: {e}")
            self.bots[bot_name]["errors"].append(str(e))
            return False

    async def check_dependencies(self, bot_name: str) -> bool:
        """Check if bot dependencies are met"""
        # For now, just return True
        # In production, check database, API connectivity, etc.
        return True

    async def check_safety_limits(self) -> Dict[str, bool]:
        """Check if any safety limits are violated"""
        violations = {}

        # Check global limits
        global_limits = self.limits.get("global_limits", {})

        # Example checks (would integrate with actual trading data)
        violations["total_loss"] = False  # Would check actual loss
        violations["total_exposure"] = False  # Would check actual exposure
        violations["consecutive_losses"] = False  # Would check loss history

        return violations

    async def trigger_kill_switch(self, reason: str):
        """Trigger emergency kill switch"""
        logger.critical(f"🚨 KILL SWITCH TRIGGERED: {reason}")
        self.kill_switch_active = True
        self.metrics["kill_switches_triggered"] += 1

        # Stop all bots
        for bot_name in self.bots.keys():
            if self.bots[bot_name]["status"] == BotStatus.RUNNING:
                await self.stop_bot(bot_name, f"Kill switch: {reason}")

        # Send critical notification
        await self.send_notification("kill_switch_triggered", {"condition": reason})

    async def disable_kill_switch(self):
        """Manually disable kill switch after review"""
        if self.kill_switch_active:
            logger.warning("⚠️  Disabling kill switch - Manual override")
            self.kill_switch_active = False

    async def attempt_recovery(self, bot_name: str) -> bool:
        """Attempt automated recovery for a failed bot"""
        logger.info(f"🔄 Attempting recovery for {bot_name}")
        self.metrics["recoveries_attempted"] += 1

        if not self.recovery_settings["auto_recovery"]["enabled"]:
            logger.info("Auto-recovery disabled, manual intervention required")
            return False

        self.bots[bot_name]["status"] = BotStatus.RECOVERY
        await self.send_notification("recovery_started", {"bot_name": bot_name})

        try:
            # Wait for cooldown
            delay = self.recovery_settings["auto_recovery"]["initial_delay_seconds"]
            logger.info(f"Waiting {delay}s before recovery attempt...")
            await asyncio.sleep(delay)

            # Check health
            if await self.check_bot_health(bot_name):
                logger.info(f"✅ Bot {bot_name} is healthy, no recovery needed")
                self.bots[bot_name]["status"] = BotStatus.RUNNING
                return True

            # Attempt restart
            success = await self.start_bot(bot_name)

            if success:
                logger.info(f"✅ Recovery successful for {bot_name}")
                self.metrics["recoveries_succeeded"] += 1
                await self.send_notification("recovery_success", {"bot_name": bot_name})
                return True
            else:
                logger.error(f"❌ Recovery failed for {bot_name}")
                await self.send_notification("recovery_failed", {"bot_name": bot_name})
                return False

        except Exception as e:
            logger.error(f"❌ Recovery error for {bot_name}: {e}")
            self.bots[bot_name]["status"] = BotStatus.ERROR
            await self.send_notification("recovery_failed", {"bot_name": bot_name})
            return False

    async def send_notification(self, alert_type: str, context: Dict):
        """Send notification through configured channels"""
        alert_config = self.notification_config["alert_types"].get(
            alert_type, {})
        message = alert_config.get("message_template", "").format(**context)
        priority = alert_config.get("priority", "info")

        logger.info(f"📢 [{priority.upper()}] {message}")

        # Would implement actual notification sending here
        # For now, just log

    async def health_monitor_loop(self):
        """Continuous health monitoring loop"""
        logger.info("🏥 Starting health monitoring loop")

        while True:
            try:
                for bot_name in self.bots.keys():
                    if self.bots[bot_name]["status"] == BotStatus.RUNNING:
                        healthy = await self.check_bot_health(bot_name)

                        if not healthy:
                            logger.warning(
                                f"⚠️  Health check failed for {bot_name}")
                            await self.send_notification(
                                "health_check_failed", {"bot_name": bot_name}
                            )

                            # Check if recovery is needed
                            if len(self.bots[bot_name]["errors"]) >= 3:
                                await self.attempt_recovery(bot_name)

                # Check safety limits
                violations = await self.check_safety_limits()
                if any(violations.values()):
                    await self.trigger_kill_switch("Safety limit violation")

                # Wait before next check
                await asyncio.sleep(self.endpoints["health_check_config"]["interval_seconds"])

            except Exception as e:
                logger.error(f"❌ Error in health monitor: {e}")
                await asyncio.sleep(10)

    async def start_sequential(self):
        """Start all bots in proper sequence"""
        logger.info("🚀 Starting bots in sequence...")

        # Start order: NDAX -> Quantum -> ShadowForge
        bot_sequence = ["ndax", "quantum", "shadowforge"]

        for bot_name in bot_sequence:
            success = await self.start_bot(bot_name)
            if not success:
                logger.error(
                    f"❌ Failed to start {bot_name}, aborting sequence")
                return False
            await asyncio.sleep(5)  # Wait between starts

        logger.info("✅ All bots started successfully")
        return True

    async def stop_all(self, reason: str = "Coordinator shutdown"):
        """Stop all bots safely"""
        logger.info("🛑 Stopping all bots...")

        for bot_name in self.bots.keys():
            if self.bots[bot_name]["status"] in [
                    BotStatus.RUNNING, BotStatus.PAUSED]:
                await self.stop_bot(bot_name, reason)

        logger.info("✅ All bots stopped")

    def get_status(self) -> Dict:
        """Get current status of all bots and coordinator"""
        return {
            "kill_switch_active": self.kill_switch_active,
            "bots": {
                name: {
                    "status": bot["status"].value,
                    "health": bot["health"],
                    "error_count": len(bot["errors"]),
                    "latest_errors": bot["errors"][-3:] if bot["errors"] else [],
                }
                for name, bot in self.bots.items()
            },
            "metrics": self.metrics,
            "timestamp": datetime.now().isoformat(),
        }


async def main():
    """Main entry point"""
    coordinator = BotCoordinator()

    try:
        await coordinator.initialize()

        # Start health monitoring in background
        monitor_task = asyncio.create_task(coordinator.health_monitor_loop())

        # For demo, just show status
        logger.info("=== Bot Coordinator Status ===")
        status = coordinator.get_status()
        logger.info(json.dumps(status, indent=2))

        # Keep running
        logger.info("Bot Coordinator running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await coordinator.stop_all()
        await coordinator.shutdown()


if __name__ == "__main__":
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Coordinator stopped by user")
