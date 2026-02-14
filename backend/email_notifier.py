"""
EMAIL NOTIFICATION SYSTEM
CRITICAL: Email sent ONLY to oconnorw225@gmail.com - HARDCODED, NO PROMPTS
Queues notifications to be sent by GitHub Actions workflow.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class EmailNotifier:
    """
    Email notification system.
    RECIPIENT HARDCODED: oconnorw225@gmail.com
    """

    # HARDCODED EMAIL - DO NOT CHANGE OR PROMPT FOR OTHER EMAILS
    RECIPIENT_EMAIL = "oconnorw225@gmail.com"

    def __init__(self):
        self.notifications_dir = Path(
            "/home/runner/work/The-basics/The-basics/notifications")
        self.notifications_dir.mkdir(exist_ok=True)

        self.outgoing_file = self.notifications_dir / "outgoing.json"
        self.sent_file = self.notifications_dir / "sent.json"

        self.outgoing_queue: List[Dict] = self._load_queue()
        self.sent_log: List[Dict] = self._load_sent()

    def _load_queue(self) -> List[Dict]:
        """Load outgoing notification queue."""
        if self.outgoing_file.exists():
            return json.loads(self.outgoing_file.read_text())
        return []

    def _save_queue(self) -> None:
        """Save outgoing notification queue."""
        self.outgoing_file.write_text(
            json.dumps(self.outgoing_queue, indent=2))

    def _load_sent(self) -> List[Dict]:
        """Load sent notifications log."""
        if self.sent_file.exists():
            return json.loads(self.sent_file.read_text())
        return []

    def _save_sent(self) -> None:
        """Save sent notifications log."""
        self.sent_file.write_text(json.dumps(self.sent_log, indent=2))

    def queue_notification(
        self,
        subject: str,
        body: str,
        notification_type: str = "info",
        priority: str = "normal",
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Queue a notification to be sent to oconnorw225@gmail.com.

        Args:
            subject: Email subject
            body: Email body (can be HTML)
            notification_type: Type of notification (info, alert, summary, etc.)
            priority: Priority level (low, normal, high, critical)
            data: Additional data to include

        Returns:
            Queued notification details
        """
        notification = {
            "id": f"notif_{len(self.outgoing_queue) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "to": self.RECIPIENT_EMAIL,  # HARDCODED
            "subject": subject,
            "body": body,
            "type": notification_type,
            "priority": priority,
            "data": data or {},
            "queued_at": datetime.now().isoformat(),
            "sent": False,
        }

        self.outgoing_queue.append(notification)
        self._save_queue()

        print(f"📧 Queued notification to {self.RECIPIENT_EMAIL}: {subject}")

        return notification

    def bot_discovery_notification(self, bots_discovered: List[Dict]) -> None:
        """Send notification about newly discovered bots."""
        bot_list = "\n".join(
            [
                f"  • {bot.get('name', 'Unknown')} - {bot.get('type', 'Unknown type')}"
                for bot in bots_discovered
            ]
        )

        subject = f"🤖 {len(bots_discovered)} New Bot(s) Discovered"
        body = f"""
<html>
<body>
    <h2>Bot Discovery Report</h2>
    <p>The autonomous system has discovered {len(bots_discovered)} new bot(s):</p>
    <pre>{bot_list}</pre>
    <p>These bots have been registered and configured automatically.</p>
    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
</body>
</html>
"""

        self.queue_notification(
            subject=subject,
            body=body,
            notification_type="bot_discovery",
            priority="normal",
            data={"bots": bots_discovered},
        )

    def recovery_completion_notification(self, recovery_results: Dict) -> None:
        """Send notification about completed asset recovery."""
        subject = "💰 Asset Recovery Scan Complete"
        body = f"""
<html>
<body>
    <h2>Asset Recovery Report</h2>
    <p>Recovery scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>

    <h3>Results:</h3>
    <ul>
        <li>Assets checked: {recovery_results.get('assets_checked', 0)}</li>
        <li>Assets recovered: {recovery_results.get('assets_recovered', 0)}</li>
        <li>Total value recovered: ${recovery_results.get('total_value', 0)}</li>
    </ul>

    <p>Next scan: {recovery_results.get('next_scan', 'In 2 hours')}</p>
</body>
</html>
"""

        self.queue_notification(
            subject=subject,
            body=body,
            notification_type="recovery_completion",
            priority="normal",
            data=recovery_results,
        )

    def daily_summary_notification(self, summary_data: Dict) -> None:
        """Send daily summary at 8 AM."""
        subject = "📊 Daily Bot System Summary"
        body = f"""
<html>
<body>
    <h2>Daily System Summary</h2>
    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>

    <h3>System Status:</h3>
    <ul>
        <li>Active bots: {summary_data.get('active_bots', 0)}</li>
        <li>Total credentials: {summary_data.get('total_credentials', 0)}</li>
        <li>Recovery scans completed: {summary_data.get('recovery_scans', 0)}</li>
        <li>Bot discoveries: {summary_data.get('new_bots', 0)}</li>
    </ul>

    <h3>Performance:</h3>
    <ul>
        <li>Uptime: {summary_data.get('uptime', 'N/A')}</li>
        <li>Errors: {summary_data.get('errors', 0)}</li>
        <li>Successful operations: {summary_data.get('successful_ops', 0)}</li>
    </ul>

    <h3>Next Actions:</h3>
    <ul>
        <li>Next credential scan: {summary_data.get('next_cred_scan', 'In 1 hour')}</li>
        <li>Next bot discovery: {summary_data.get('next_bot_scan', 'In 30 minutes')}</li>
        <li>Next recovery scan: {summary_data.get('next_recovery', 'In 2 hours')}</li>
    </ul>
</body>
</html>
"""

        self.queue_notification(
            subject=subject,
            body=body,
            notification_type="daily_summary",
            priority="low",
            data=summary_data,
        )

    def gatekeeper_alert(self, missing_gatekeepers: List[str]) -> None:
        """Send alert for missing critical gatekeeper credentials."""
        gatekeeper_list = "\n".join(
            [f"  • {gk}" for gk in missing_gatekeepers])

        subject = "⚠️ CRITICAL: Missing Gatekeeper Credentials"
        body = f"""
<html>
<body>
    <h2 style="color: red;">CRITICAL ALERT: Missing Gatekeeper Credentials</h2>
    <p>The autonomous system is missing the following critical credentials:</p>
    <pre>{gatekeeper_list}</pre>

    <h3>Required Actions:</h3>
    <ol>
        <li>Add missing credentials to GitHub Secrets</li>
        <li>Set environment variables locally if running locally</li>
        <li>Restart the system after adding credentials</li>
    </ol>

    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    <p><strong>Impact:</strong> Some bots may not function until these credentials are provided.</p>
</body>
</html>
"""

        self.queue_notification(
            subject=subject,
            body=body,
            notification_type="gatekeeper_alert",
            priority="critical",
            data={"missing_gatekeepers": missing_gatekeepers},
        )

    def system_alert(self, alert_type: str, message: str,
                     details: Optional[Dict] = None) -> None:
        """Send general system alert."""
        subject = f"🚨 System Alert: {alert_type}"
        body = f"""
<html>
<body>
    <h2>System Alert</h2>
    <p><strong>Alert Type:</strong> {alert_type}</p>
    <p><strong>Message:</strong> {message}</p>

    {f'<h3>Details:</h3><pre>{json.dumps(details, indent=2)}</pre>' if details else ''}

    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
</body>
</html>
"""

        self.queue_notification(
            subject=subject,
            body=body,
            notification_type="system_alert",
            priority="high",
            data=details,
        )

    def initialization_notification(self, init_results: Dict) -> None:
        """Send notification when system initializes."""
        subject = "🚀 Bot System Initialized"
        body = f"""
<html>
<body>
    <h2>Bot System Successfully Initialized</h2>
    <p>Your autonomous bot system has been initialized and is now running.</p>

    <h3>Initialization Summary:</h3>
    <ul>
        <li>Bots discovered: {init_results.get('bots_discovered', 0)}</li>
        <li>Credentials found: {init_results.get('credentials_found', 0)}</li>
        <li>Recovery system: {init_results.get('recovery_status', 'Active')}</li>
        <li>Dashboard: {init_results.get('dashboard_status', 'Running')}</li>
    </ul>

    <h3>System Configuration:</h3>
    <ul>
        <li>Recovery scans: Every 2 hours</li>
        <li>Bot discovery: Every 30 minutes</li>
        <li>Credential rescans: Every hour</li>
        <li>Daily summary: 8 AM daily</li>
    </ul>

    <h3>Access:</h3>
    <ul>
        <li>Dashboard: http://localhost:3000</li>
        <li>API: http://localhost:8000</li>
        <li>API Docs: http://localhost:8000/docs</li>
    </ul>

    <p><strong>Status:</strong> All systems operational</p>
    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
</body>
</html>
"""

        self.queue_notification(
            subject=subject,
            body=body,
            notification_type="initialization",
            priority="normal",
            data=init_results,
        )

    def mark_as_sent(self, notification_id: str) -> bool:
        """Mark a notification as sent."""
        for notif in self.outgoing_queue:
            if notif["id"] == notification_id:
                notif["sent"] = True
                notif["sent_at"] = datetime.now().isoformat()

                # Move to sent log
                self.sent_log.append(notif)

                # Remove from outgoing queue
                self.outgoing_queue = [
                    n for n in self.outgoing_queue if n["id"] != notification_id]

                self._save_queue()
                self._save_sent()

                print(f"✅ Marked notification {notification_id} as sent")
                return True

        return False

    def get_pending_notifications(self) -> List[Dict]:
        """Get all pending notifications."""
        return [n for n in self.outgoing_queue if not n["sent"]]

    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        return {
            "pending": len(self.get_pending_notifications()),
            "sent_today": len(
                [
                    n
                    for n in self.sent_log
                    if n.get("sent_at", "").startswith(datetime.now().strftime("%Y-%m-%d"))
                ]
            ),
            "total_sent": len(self.sent_log),
            "recipient": self.RECIPIENT_EMAIL,  # Show hardcoded recipient
        }


# Global instance
email_notifier = EmailNotifier()


def main():
    """Test email notifier."""
    # Test initialization notification
    email_notifier.initialization_notification(
        {
            "bots_discovered": 44,
            "credentials_found": 15,
            "recovery_status": "Active",
            "dashboard_status": "Running",
        }
    )

    # Test bot discovery
    email_notifier.bot_discovery_notification(
        [
            {"name": "quantum_bot", "type": "trading"},
            {"name": "shadowforge_bot", "type": "ai_trader"},
        ]
    )

    # Test gatekeeper alert
    email_notifier.gatekeeper_alert(["GITHUB_TOKEN", "MAIN_WALLET_KEY"])

    # Get stats
    stats = email_notifier.get_notification_stats()
    print(f"\n📊 Notification Stats:")
    print(f"  • Pending: {stats['pending']}")
    print(f"  • Sent today: {stats['sent_today']}")
    print(f"  • Total sent: {stats['total_sent']}")
    print(f"  • Recipient: {stats['recipient']}")

    # Show pending
    pending = email_notifier.get_pending_notifications()
    print(f"\n📧 Pending Notifications:")
    for notif in pending:
        print(f"  • {notif['subject']} ({notif['priority']})")


if __name__ == "__main__":
    main()
